//! Resident session (OMNI-RENDER-GPU-0 § CYCLONE-ARRAY C2): the state lives on the device for the whole run. Buffers are device-local and
//! persist across steps; each compute pass (module + specialization constants + the session buffers it binds + workgroups) is built
//! once; the whole step is recorded ONCE as a chain of passes in one command buffer and re-submitted every step. A compute→compute
//! barrier follows every pass (the last one orders the next submission's first pass: barriers act in queue submission order), so a
//! step never touches the host. Only `write` / `read` cross, through one host-visible staging buffer, when the caller asks.
use crate::run::Gpu;
use crate::vk_gen::*;
use core::ffi::{c_void, CStr};
use core::ptr::{null, null_mut};
use std::time::Instant;

macro_rules! f {
    ($t:expr, $n:ident) => {
        $t.$n.ok_or(concat!(stringify!($n), " not loaded"))?
    };
}
fn ok(r: VkResult, what: &str) -> Result<(), String> { if r == VK_SUCCESS { Ok(()) } else { Err(format!("{what}: VkResult {}", r.0)) } }

struct Pass { pipe: VkPipeline, pl: VkPipelineLayout, dsl: VkDescriptorSetLayout, pool: VkDescriptorPool, set: VkDescriptorSet, groups: [u32; 3],
              indirect: Option<usize> }   // Some(buffer): vkCmdDispatchIndirect reads [x, y, z] from that buffer (written by an earlier pass)

#[derive(Debug, Default)]
pub struct StepStats { pub steps: u32, pub wall_ms: f64, pub gpu_ms_last: Option<f64> }

pub struct Session<'g> {
    g: &'g Gpu,
    bufs: Vec<(VkBuffer, VkDeviceMemory, u64)>,
    /// per buffer (offset, owned): a VIEW (M0 arena) is a range of an owned buffer, bound at its offset with its exact range
    offs: Vec<(u64, bool)>,
    stage: Option<(VkBuffer, VkDeviceMemory, *mut c_void, u64)>,
    modules: Vec<VkShaderModule>,
    passes: Vec<Pass>,
    cpool: VkCommandPool,
    step_cb: VkCommandBuffer,
    xfer_cb: VkCommandBuffer,
    fence: VkFence,
    qp: VkQueryPool,
    recorded: bool,
    /// per-pass GPU timestamps (OMNI_GPU_PROFILE=1): a timestamp after every pass of the recorded step
    profile: bool, pq: VkQueryPool,
    /// buffers placed in DEVICE_LOCAL memory (false only where the device has none, e.g. a CPU driver's single heap)
    pub device_local: bool,
    /// SEGMENTS (GROW-RUN-0 GPU decode): pass index where each segment starts + its own recorded command buffer — a program with several
    /// steps on the same buffers (decode: prep = quantise the weights after they change · step = every station one token); empty = one step
    segs: Vec<usize>, seg_cbs: Vec<VkCommandBuffer>,
    /// the queue this session submits to (Gpu::queue, or Gpu::queue2 for the array server's decode) · an async step in flight
    q: VkQueue, inflight: bool,
}

impl<'g> Session<'g> {
    pub fn new(g: &'g Gpu) -> Result<Self, String> {
        let (d, fd) = (g.device, &g.fd);
        unsafe {
            let cpci = VkCommandPoolCreateInfo { flags: VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT, queueFamilyIndex: g.qfam, ..Default::default() };
            let mut cpool = VkCommandPool::NULL;
            ok(f!(fd, vkCreateCommandPool)(d, &cpci, null(), &mut cpool), "vkCreateCommandPool")?;
            let cbai = VkCommandBufferAllocateInfo { commandPool: cpool, level: VK_COMMAND_BUFFER_LEVEL_PRIMARY, commandBufferCount: 2, ..Default::default() };
            let mut cbs = [VkCommandBuffer::NULL; 2];
            ok(f!(fd, vkAllocateCommandBuffers)(d, &cbai, cbs.as_mut_ptr()), "vkAllocateCommandBuffers")?;
            let mut fence = VkFence::NULL;
            ok(f!(fd, vkCreateFence)(d, &VkFenceCreateInfo::default(), null(), &mut fence), "vkCreateFence")?;
            let mut qp = VkQueryPool::NULL;
            if g.timestamps {
                let qpi = VkQueryPoolCreateInfo { queryType: VK_QUERY_TYPE_TIMESTAMP, queryCount: 2, ..Default::default() };
                ok(f!(fd, vkCreateQueryPool)(d, &qpi, null(), &mut qp), "vkCreateQueryPool")?;
            }
            let device_local = (0..g.mem.memoryTypeCount).any(|i| g.mem.memoryTypes[i as usize].propertyFlags & VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT != 0);
            let profile = g.timestamps && std::env::var("OMNI_GPU_PROFILE").map(|v| v == "1").unwrap_or(false);
            Ok(Self { g, bufs: vec![], offs: vec![], stage: None, modules: vec![], passes: vec![], cpool, step_cb: cbs[0], xfer_cb: cbs[1], fence, qp,
                      recorded: false, profile, pq: VkQueryPool::NULL, device_local, segs: vec![], seg_cbs: vec![], q: g.queue, inflight: false })
        }
    }

    fn mem_type(&self, bits: u32, want: u32) -> Option<u32> {
        (0..self.g.mem.memoryTypeCount).find(|&i| bits & (1 << i) != 0 && self.g.mem.memoryTypes[i as usize].propertyFlags & want == want)
    }

    unsafe fn make_buffer(&self, size: u64, usage: u32, want: u32) -> Result<(VkBuffer, VkDeviceMemory), String> {
        let (d, fd) = (self.g.device, &self.g.fd);
        let bci = VkBufferCreateInfo { size, usage, sharingMode: VK_SHARING_MODE_EXCLUSIVE, ..Default::default() };
        let mut buf = VkBuffer::NULL;
        ok(f!(fd, vkCreateBuffer)(d, &bci, null(), &mut buf), "vkCreateBuffer")?;
        let mut req = VkMemoryRequirements::default();
        f!(fd, vkGetBufferMemoryRequirements)(d, buf, &mut req);
        let mt = self.mem_type(req.memoryTypeBits, want).or_else(|| self.mem_type(req.memoryTypeBits, 0))
            .ok_or_else(|| format!("no memory type for buffer bits {:#x}", req.memoryTypeBits))?;
        let mai = VkMemoryAllocateInfo { allocationSize: req.size, memoryTypeIndex: mt, ..Default::default() };
        let mut mem = VkDeviceMemory::NULL;
        ok(f!(fd, vkAllocateMemory)(d, &mai, null(), &mut mem), "vkAllocateMemory")?;
        ok(f!(fd, vkBindBufferMemory)(d, buf, mem, 0), "vkBindBufferMemory")?;
        Ok((buf, mem))
    }

    /// a device-local storage buffer of `bytes` (rounded up to 4), zero-filled; returns its session index
    pub fn buffer(&mut self, bytes: u64) -> Result<usize, String> {
        let size = (bytes.max(4) + 3) / 4 * 4;
        unsafe {
            let (b, m) = self.make_buffer(size, VK_BUFFER_USAGE_STORAGE_BUFFER_BIT | VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT
                                          | VK_BUFFER_USAGE_INDIRECT_BUFFER_BIT, VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)?;
            self.bufs.push((b, m, size)); self.offs.push((0, true));
            let i = self.bufs.len() - 1;
            self.transfer(|s, cb| { f!(s.g.fd, vkCmdFillBuffer)(cb, s.bufs[i].0, 0, VK_WHOLE_SIZE, 0); Ok(()) })?;
            Ok(i)
        }
    }

    /// a view of buffer `parent`: `bytes` at `offset` (a multiple of minStorageBufferOffsetAlignment), bound with that exact range — the
    /// step builder's arena (OMNI-RENDER-GPU-0 M0): transient buffers whose pass ranges never overlap share one allocation
    pub fn view(&mut self, parent: usize, offset: u64, bytes: u64) -> Result<usize, String> {
        let (b, _, size) = *self.bufs.get(parent).ok_or_else(|| format!("view: no buffer {parent}"))?;
        if !self.offs[parent].1 { return Err(format!("view: buffer {parent} is itself a view")) }
        let al = self.g.props.limits.minStorageBufferOffsetAlignment.max(4); let n = (bytes.max(4) + 3) / 4 * 4;
        if offset % al != 0 || offset + n > size { return Err(format!("view: {n} bytes at {offset} of buffer {parent} ({size} bytes, alignment {al})")) }
        self.bufs.push((b, VkDeviceMemory::NULL, n)); self.offs.push((offset, false));
        Ok(self.bufs.len() - 1)
    }

    unsafe fn ensure_stage(&mut self, size: u64) -> Result<(), String> {
        if self.stage.map(|s| s.3 >= size).unwrap_or(false) { return Ok(()) }
        if let Some((b, m, _, _)) = self.stage.take() {
            f!(self.g.fd, vkUnmapMemory)(self.g.device, m); f!(self.g.fd, vkDestroyBuffer)(self.g.device, b, null()); f!(self.g.fd, vkFreeMemory)(self.g.device, m, null());
        }
        // staging memory: HOST_CACHED when the device has it — the CPU reads every read-back from here, and a write-combined (uncached)
        // mapping reads at a few hundred MB/s (the array server's weight read-back took 0.7 s per step on the A40, GROW-RUN-0)
        let vc = VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
        let cached = (0..self.g.mem.memoryTypeCount).any(|i| self.g.mem.memoryTypes[i as usize].propertyFlags & (vc | VK_MEMORY_PROPERTY_HOST_CACHED_BIT) == vc | VK_MEMORY_PROPERTY_HOST_CACHED_BIT);
        let (b, m) = self.make_buffer(size, VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT,
                                      if cached { vc | VK_MEMORY_PROPERTY_HOST_CACHED_BIT } else { vc })?;
        let mut p: *mut c_void = null_mut();
        ok(f!(self.g.fd, vkMapMemory)(self.g.device, m, 0, VK_WHOLE_SIZE, 0, &mut p), "vkMapMemory")?;
        self.stage = Some((b, m, p, size));
        Ok(())
    }

    /// record + submit + wait one transfer command buffer (setup / write / read only — never inside a step)
    unsafe fn transfer(&self, rec: impl Fn(&Self, VkCommandBuffer) -> Result<(), String>) -> Result<(), String> {
        let (d, fd, cb) = (self.g.device, &self.g.fd, self.xfer_cb);
        let bi = VkCommandBufferBeginInfo { flags: VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT, ..Default::default() };
        ok(f!(fd, vkBeginCommandBuffer)(cb, &bi), "vkBeginCommandBuffer")?;
        // order against everything submitted before (a step's passes) and make the copy visible to later passes / the host
        let mb = VkMemoryBarrier { srcAccessMask: VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_TRANSFER_WRITE_BIT,
                                   dstAccessMask: VK_ACCESS_TRANSFER_READ_BIT | VK_ACCESS_TRANSFER_WRITE_BIT, ..Default::default() };
        f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_TRANSFER_BIT, 0,
                                     1, &mb, 0, null(), 0, null());
        rec(self, cb)?;
        let mb2 = VkMemoryBarrier { srcAccessMask: VK_ACCESS_TRANSFER_WRITE_BIT,
                                    dstAccessMask: VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_HOST_READ_BIT, ..Default::default() };
        f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_HOST_BIT, 0,
                                     1, &mb2, 0, null(), 0, null());
        ok(f!(fd, vkEndCommandBuffer)(cb), "vkEndCommandBuffer")?;
        let sub = VkSubmitInfo { commandBufferCount: 1, pCommandBuffers: &cb, ..Default::default() };
        ok(f!(fd, vkQueueSubmit)(self.q, 1, &sub, self.fence), "vkQueueSubmit")?;
        ok(f!(fd, vkWaitForFences)(d, 1, &self.fence, VK_TRUE, u64::MAX), "vkWaitForFences")?;
        ok(f!(fd, vkResetFences)(d, 1, &self.fence), "vkResetFences")?;
        Ok(())
    }

    /// host → buffer i (bytes ≤ its size; the rest keeps its contents)
    pub fn write(&mut self, i: usize, bytes: &[u8]) -> Result<(), String> {
        let (b, _, size) = *self.bufs.get(i).ok_or_else(|| format!("write: no buffer {i}"))?;
        if bytes.len() as u64 > size { return Err(format!("write: {} bytes into buffer {i} of {size}", bytes.len())) }
        if bytes.is_empty() { return Ok(()) }
        unsafe {
            self.ensure_stage(bytes.len() as u64)?;
            let (sb, _, sp, _) = self.stage.unwrap();
            core::ptr::copy_nonoverlapping(bytes.as_ptr(), sp as *mut u8, bytes.len());
            let n = (bytes.len() as u64 + 3) / 4 * 4;
            let off = self.offs[i].0;
            self.transfer(|s, cb| { let r = VkBufferCopy { srcOffset: 0, dstOffset: off, size: n.min(size) }; f!(s.g.fd, vkCmdCopyBuffer)(cb, sb, b, 1, &r); Ok(()) })
        }
    }

    /// many host → buffer pieces in ONE transfer: (buffer, byte offset inside it, bytes) — the array server's per-slot slices (GROW-RUN-0 G3b-4)
    pub fn write_at_many(&mut self, items: &[(usize, u64, &[u8])]) -> Result<(), String> {
        let total: u64 = items.iter().map(|(_, _, b)| (b.len() as u64 + 3) / 4 * 4).sum();
        if total == 0 { return Ok(()) }
        let mut regions = Vec::with_capacity(items.len());
        unsafe {
            self.ensure_stage(total)?;
            let (sb, _, sp, _) = self.stage.unwrap(); let mut so = 0u64;
            for &(i, off, bytes) in items {
                let (b, _, size) = *self.bufs.get(i).ok_or_else(|| format!("write_at_many: no buffer {i}"))?;
                if off + bytes.len() as u64 > size { return Err(format!("write_at_many: {} bytes at {off} into buffer {i} of {size}", bytes.len())) }
                core::ptr::copy_nonoverlapping(bytes.as_ptr(), (sp as *mut u8).add(so as usize), bytes.len());
                let n = (bytes.len() as u64 + 3) / 4 * 4;
                regions.push((b, VkBufferCopy { srcOffset: so, dstOffset: self.offs[i].0 + off, size: n.min(size - off) })); so += n;
            }
            self.transfer(|s, cb| { for (b, r) in &regions { f!(s.g.fd, vkCmdCopyBuffer)(cb, sb, *b, 1, r); } Ok(()) })
        }
    }

    /// many buffer → host pieces in ONE transfer: (buffer, byte offset, bytes) → one Vec per piece
    pub fn read_at_many(&mut self, items: &[(usize, u64, u64)]) -> Result<Vec<Vec<u8>>, String> {
        let total: u64 = items.iter().map(|(_, _, n)| (n + 3) / 4 * 4).sum();
        let mut regions = Vec::with_capacity(items.len()); let mut so = 0u64; let mut at = Vec::with_capacity(items.len());
        for &(i, off, n) in items {
            let (b, _, size) = *self.bufs.get(i).ok_or_else(|| format!("read_at_many: no buffer {i}"))?;
            if off + n > size { return Err(format!("read_at_many: {n} bytes at {off} of buffer {i} ({size})")) }
            regions.push((b, VkBufferCopy { srcOffset: self.offs[i].0 + off, dstOffset: so, size: n })); at.push((so, n)); so += (n + 3) / 4 * 4;
        }
        unsafe {
            self.ensure_stage(total.max(4))?;
            let (sb, _, sp, _) = self.stage.unwrap();
            self.transfer(|s, cb| { for (b, r) in &regions { f!(s.g.fd, vkCmdCopyBuffer)(cb, *b, sb, 1, r); } Ok(()) })?;
            Ok(at.iter().map(|&(o, n)| { let mut v = vec![0u8; n as usize]; core::ptr::copy_nonoverlapping((sp as *const u8).add(o as usize), v.as_mut_ptr(), n as usize); v }).collect())
        }
    }

    /// buffer i → host (its whole size)
    pub fn read(&mut self, i: usize) -> Result<Vec<u8>, String> {
        let (b, _, size) = *self.bufs.get(i).ok_or_else(|| format!("read: no buffer {i}"))?;
        unsafe {
            self.ensure_stage(size)?;
            let (sb, _, sp, _) = self.stage.unwrap();
            let off = self.offs[i].0;
            self.transfer(|s, cb| { let r = VkBufferCopy { srcOffset: off, dstOffset: 0, size }; f!(s.g.fd, vkCmdCopyBuffer)(cb, b, sb, 1, &r); Ok(()) })?;
            let mut v = vec![0u8; size as usize];
            core::ptr::copy_nonoverlapping(sp as *const u8, v.as_mut_ptr(), size as usize);
            Ok(v)
        }
    }

    pub fn module(&mut self, spv: &[u32]) -> Result<usize, String> {
        let smi = VkShaderModuleCreateInfo { codeSize: spv.len() * 4, pCode: spv.as_ptr(), ..Default::default() };
        let mut sm = VkShaderModule::NULL;
        unsafe { ok(f!(self.g.fd, vkCreateShaderModule)(self.g.device, &smi, null(), &mut sm), "vkCreateShaderModule")? };
        self.modules.push(sm);
        Ok(self.modules.len() - 1)
    }

    /// one compute pass: `binds[k]` = the session buffer at set 0 binding k; built now, dispatched every step in the order added
    pub fn pass(&mut self, module: usize, entry: &CStr, spec: &[(u32, u32)], binds: &[usize], groups: [u32; 3]) -> Result<usize, String> {
        let (d, fd) = (self.g.device, &self.g.fd);
        if self.recorded { return Err("pass: the step is already recorded".into()) }
        let sm = *self.modules.get(module).ok_or_else(|| format!("pass: no module {module}"))?;
        for &b in binds { if b >= self.bufs.len() { return Err(format!("pass: no buffer {b}")) } }
        unsafe {
            let lb: Vec<VkDescriptorSetLayoutBinding> = (0..binds.len() as u32)
                .map(|i| VkDescriptorSetLayoutBinding { binding: i, descriptorType: VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, descriptorCount: 1,
                                                         stageFlags: VK_SHADER_STAGE_COMPUTE_BIT, ..Default::default() }).collect();
            let dsli = VkDescriptorSetLayoutCreateInfo { bindingCount: lb.len() as u32, pBindings: lb.as_ptr(), ..Default::default() };
            let mut dsl = VkDescriptorSetLayout::NULL;
            ok(f!(fd, vkCreateDescriptorSetLayout)(d, &dsli, null(), &mut dsl), "vkCreateDescriptorSetLayout")?;
            let pli = VkPipelineLayoutCreateInfo { setLayoutCount: 1, pSetLayouts: &dsl, ..Default::default() };
            let mut pl = VkPipelineLayout::NULL;
            ok(f!(fd, vkCreatePipelineLayout)(d, &pli, null(), &mut pl), "vkCreatePipelineLayout")?;
            let entries: Vec<VkSpecializationMapEntry> = spec.iter().enumerate()
                .map(|(i, &(id, _))| VkSpecializationMapEntry { constantID: id, offset: (i * 4) as u32, size: 4 }).collect();
            let data: Vec<u32> = spec.iter().map(|&(_, v)| v).collect();
            let si = VkSpecializationInfo { mapEntryCount: entries.len() as u32, pMapEntries: entries.as_ptr(), dataSize: data.len() * 4,
                                            pData: data.as_ptr() as *const c_void };
            let stage = VkPipelineShaderStageCreateInfo { stage: VK_SHADER_STAGE_COMPUTE_BIT, module: sm, pName: entry.as_ptr(),
                                                          pSpecializationInfo: if spec.is_empty() { null() } else { &si }, ..Default::default() };
            let cpi = VkComputePipelineCreateInfo { stage, layout: pl, basePipelineIndex: -1, ..Default::default() };
            let mut pipe = VkPipeline::NULL;
            ok(f!(fd, vkCreateComputePipelines)(d, VkPipelineCache::NULL, 1, &cpi, null(), &mut pipe), "vkCreateComputePipelines")?;
            let ps = VkDescriptorPoolSize { r#type: VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, descriptorCount: binds.len().max(1) as u32 };
            let dpi = VkDescriptorPoolCreateInfo { maxSets: 1, poolSizeCount: 1, pPoolSizes: &ps, ..Default::default() };
            let mut pool = VkDescriptorPool::NULL;
            ok(f!(fd, vkCreateDescriptorPool)(d, &dpi, null(), &mut pool), "vkCreateDescriptorPool")?;
            let dsai = VkDescriptorSetAllocateInfo { descriptorPool: pool, descriptorSetCount: 1, pSetLayouts: &dsl, ..Default::default() };
            let mut set = VkDescriptorSet::NULL;
            ok(f!(fd, vkAllocateDescriptorSets)(d, &dsai, &mut set), "vkAllocateDescriptorSets")?;
            let infos: Vec<VkDescriptorBufferInfo> = binds.iter().map(|&b| VkDescriptorBufferInfo { buffer: self.bufs[b].0, offset: self.offs[b].0, range: if self.offs[b].1 { VK_WHOLE_SIZE } else { self.bufs[b].2 } }).collect();
            let writes: Vec<VkWriteDescriptorSet> = infos.iter().enumerate()
                .map(|(i, bi)| VkWriteDescriptorSet { dstSet: set, dstBinding: i as u32, descriptorCount: 1,
                                                       descriptorType: VK_DESCRIPTOR_TYPE_STORAGE_BUFFER, pBufferInfo: bi, ..Default::default() }).collect();
            f!(fd, vkUpdateDescriptorSets)(d, writes.len() as u32, writes.as_ptr(), 0, null());
            self.passes.push(Pass { pipe, pl, dsl, pool, set, groups, indirect: None });
        }
        Ok(self.passes.len() - 1)
    }

    /// a pass whose size the GPU decides: dispatched by vkCmdDispatchIndirect from `args` ([x, y, z] u32 at offset 0, written by an earlier
    /// pass of the same step — GROW-RUN-0 JIT-T50 #1: capacity follows load with no host round trip)
    pub fn pass_indirect(&mut self, module: usize, entry: &CStr, spec: &[(u32, u32)], binds: &[usize], args: usize) -> Result<usize, String> {
        if args >= self.bufs.len() || !self.offs[args].1 { return Err(format!("pass_indirect: args {args} must be a whole buffer")) }
        let i = self.pass(module, entry, spec, binds, [0, 0, 0])?; self.passes[i].indirect = Some(args); Ok(i)
    }

    /// record the step once: every pass in order, a compute→compute barrier after each
    pub fn record(&mut self) -> Result<(), String> {
        let (fd, cb) = (&self.g.fd, self.step_cb);
        unsafe {
            if self.profile {
                let qpi = VkQueryPoolCreateInfo { queryType: VK_QUERY_TYPE_TIMESTAMP, queryCount: self.passes.len() as u32 + 1, ..Default::default() };
                ok(f!(fd, vkCreateQueryPool)(self.g.device, &qpi, null(), &mut self.pq), "vkCreateQueryPool")?;
            }
            ok(f!(fd, vkBeginCommandBuffer)(cb, &VkCommandBufferBeginInfo::default()), "vkBeginCommandBuffer")?;
            if self.g.timestamps {
                f!(fd, vkCmdResetQueryPool)(cb, self.qp, 0, 2);
                f!(fd, vkCmdWriteTimestamp)(cb, VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT, self.qp, 0);
            }
            let mb = VkMemoryBarrier { srcAccessMask: VK_ACCESS_SHADER_WRITE_BIT,
                                       dstAccessMask: VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_INDIRECT_COMMAND_READ_BIT, ..Default::default() };
            if self.profile { f!(fd, vkCmdResetQueryPool)(cb, self.pq, 0, self.passes.len() as u32 + 1); f!(fd, vkCmdWriteTimestamp)(cb, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, self.pq, 0); }
            for (pi, p) in self.passes.iter().enumerate() {
                f!(fd, vkCmdBindPipeline)(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pipe);
                f!(fd, vkCmdBindDescriptorSets)(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pl, 0, 1, &p.set, 0, null());
                match p.indirect {
                    Some(a) => f!(fd, vkCmdDispatchIndirect)(cb, self.bufs[a].0, 0),
                    None => f!(fd, vkCmdDispatch)(cb, p.groups[0], p.groups[1], p.groups[2]),
                }
                f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_DRAW_INDIRECT_BIT,
                                             0, 1, &mb, 0, null(), 0, null());
                if self.profile { f!(fd, vkCmdWriteTimestamp)(cb, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, self.pq, pi as u32 + 1); }
            }
            if self.g.timestamps { f!(fd, vkCmdWriteTimestamp)(cb, VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT, self.qp, 1); }
            ok(f!(fd, vkEndCommandBuffer)(cb), "vkEndCommandBuffer")?;
        }
        self.recorded = true;
        Ok(())
    }

    /// submit to the device's second queue from now on (decode beside training, GROW-RUN-0 array server)
    pub fn use_queue2(&mut self) { self.q = self.g.queue2; }
    /// segment k submitted WITHOUT waiting (the caller does other GPU work, then step_wait)
    pub fn step_seg_async(&mut self, k: usize) -> Result<(), String> {
        if self.seg_cbs.is_empty() { self.step_seg_prepare()?; }
        let sub = VkSubmitInfo { commandBufferCount: 1, pCommandBuffers: &self.seg_cbs[k], ..Default::default() };
        unsafe { ok(f!(self.g.fd, vkQueueSubmit)(self.q, 1, &sub, self.fence), "vkQueueSubmit")?; }
        self.inflight = true; Ok(())
    }
    /// the whole recorded step submitted WITHOUT waiting (the array server serves decode on queue 2 meanwhile), then step_done / step_wait
    pub fn step_async(&mut self) -> Result<(), String> {
        if !self.recorded { self.record()? }
        let sub = VkSubmitInfo { commandBufferCount: 1, pCommandBuffers: &self.step_cb, ..Default::default() };
        unsafe { ok(f!(self.g.fd, vkQueueSubmit)(self.q, 1, &sub, self.fence), "vkQueueSubmit")?; }
        self.inflight = true; Ok(())
    }
    /// is the async step done (non-blocking)
    pub fn step_done(&mut self) -> Result<bool, String> {
        if !self.inflight { return Ok(true) }
        let r = unsafe { f!(self.g.fd, vkGetFenceStatus)(self.g.device, self.fence) };
        if r == VK_SUCCESS { unsafe { ok(f!(self.g.fd, vkResetFences)(self.g.device, 1, &self.fence), "vkResetFences")?; } self.inflight = false; return Ok(true) }
        Ok(false)
    }
    pub fn step_wait(&mut self) -> Result<(), String> {
        if !self.inflight { return Ok(()) }
        unsafe { ok(f!(self.g.fd, vkWaitForFences)(self.g.device, 1, &self.fence, VK_TRUE, u64::MAX), "vkWaitForFences")?;
                 ok(f!(self.g.fd, vkResetFences)(self.g.device, 1, &self.fence), "vkResetFences")?; }
        self.inflight = false; Ok(())
    }
    /// GPU → GPU copies FROM another session's buffers (same device) into ours: (src buffer, src offset, our buffer, our offset, bytes)
    pub fn copy_from(&mut self, src: &Session, items: &[(usize, u64, usize, u64, u64)]) -> Result<(), String> {
        let regions: Vec<(VkBuffer, VkBuffer, VkBufferCopy)> = items.iter().map(|&(si, so, di, dof, n)|
            (src.bufs[si].0, self.bufs[di].0, VkBufferCopy { srcOffset: src.offs[si].0 + so, dstOffset: self.offs[di].0 + dof, size: n })).collect();
        unsafe { self.transfer(|s, cb| { for (a, b, r) in &regions { f!(s.g.fd, vkCmdCopyBuffer)(cb, *a, *b, 1, r); } Ok(()) }) }
    }

    /// start a new segment at the next pass (the first call also makes the passes before it segment 0)
    pub fn segment(&mut self) { if self.segs.is_empty() { self.segs.push(0); } self.segs.push(self.passes.len()); }
    pub fn segments(&self) -> usize { self.segs.len() }

    /// record every segment's command buffer (once)
    fn step_seg_prepare(&mut self) -> Result<(), String> {
        if self.segs.is_empty() { self.segs.push(0); }
        let (d, fd) = (self.g.device, &self.g.fd);
        unsafe {
                let n = self.segs.len() as u32;
                let cbai = VkCommandBufferAllocateInfo { commandPool: self.cpool, level: VK_COMMAND_BUFFER_LEVEL_PRIMARY, commandBufferCount: n, ..Default::default() };
                let mut cbs = vec![VkCommandBuffer::NULL; n as usize];
                ok(f!(fd, vkAllocateCommandBuffers)(d, &cbai, cbs.as_mut_ptr()), "vkAllocateCommandBuffers")?;
                let mb = VkMemoryBarrier { srcAccessMask: VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_TRANSFER_WRITE_BIT,
                                           dstAccessMask: VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_INDIRECT_COMMAND_READ_BIT, ..Default::default() };
                for (si, &cb) in cbs.iter().enumerate() {
                    let (a, b) = (self.segs[si], if si + 1 < self.segs.len() { self.segs[si + 1] } else { self.passes.len() });
                    ok(f!(fd, vkBeginCommandBuffer)(cb, &VkCommandBufferBeginInfo::default()), "vkBeginCommandBuffer")?;
                    f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 1, &mb, 0, null(), 0, null());
                    for p in &self.passes[a..b] {
                        f!(fd, vkCmdBindPipeline)(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pipe);
                        f!(fd, vkCmdBindDescriptorSets)(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pl, 0, 1, &p.set, 0, null());
                        match p.indirect { Some(ai) => f!(fd, vkCmdDispatchIndirect)(cb, self.bufs[ai].0, 0), None => f!(fd, vkCmdDispatch)(cb, p.groups[0], p.groups[1], p.groups[2]) }
                        f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_DRAW_INDIRECT_BIT, 0, 1, &mb, 0, null(), 0, null());
                    }
                    ok(f!(fd, vkEndCommandBuffer)(cb), "vkEndCommandBuffer")?;
                }
                self.seg_cbs = cbs;
        }
        Ok(())
    }

    /// run segment k once (recorded on first use: its passes in order, a barrier after each) and wait for it
    pub fn step_seg(&mut self, k: usize) -> Result<(), String> {
        if k >= self.segs.len() { return Err(format!("step_seg: no segment {k} ({} segments)", self.segs.len())) }
        if self.seg_cbs.is_empty() { self.step_seg_prepare()?; }
        let (d, fd) = (self.g.device, &self.g.fd);
        unsafe {
            if self.seg_cbs.is_empty() {
                let n = self.segs.len() as u32;
                let cbai = VkCommandBufferAllocateInfo { commandPool: self.cpool, level: VK_COMMAND_BUFFER_LEVEL_PRIMARY, commandBufferCount: n, ..Default::default() };
                let mut cbs = vec![VkCommandBuffer::NULL; n as usize];
                ok(f!(fd, vkAllocateCommandBuffers)(d, &cbai, cbs.as_mut_ptr()), "vkAllocateCommandBuffers")?;
                let mb = VkMemoryBarrier { srcAccessMask: VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_TRANSFER_WRITE_BIT,
                                           dstAccessMask: VK_ACCESS_SHADER_READ_BIT | VK_ACCESS_SHADER_WRITE_BIT | VK_ACCESS_INDIRECT_COMMAND_READ_BIT, ..Default::default() };
                for (si, &cb) in cbs.iter().enumerate() {
                    let (a, b) = (self.segs[si], if si + 1 < self.segs.len() { self.segs[si + 1] } else { self.passes.len() });
                    ok(f!(fd, vkBeginCommandBuffer)(cb, &VkCommandBufferBeginInfo::default()), "vkBeginCommandBuffer")?;
                    f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_TRANSFER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, 0, 1, &mb, 0, null(), 0, null());
                    for p in &self.passes[a..b] {
                        f!(fd, vkCmdBindPipeline)(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pipe);
                        f!(fd, vkCmdBindDescriptorSets)(cb, VK_PIPELINE_BIND_POINT_COMPUTE, p.pl, 0, 1, &p.set, 0, null());
                        match p.indirect { Some(ai) => f!(fd, vkCmdDispatchIndirect)(cb, self.bufs[ai].0, 0), None => f!(fd, vkCmdDispatch)(cb, p.groups[0], p.groups[1], p.groups[2]) }
                        f!(fd, vkCmdPipelineBarrier)(cb, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT, VK_PIPELINE_STAGE_COMPUTE_SHADER_BIT | VK_PIPELINE_STAGE_DRAW_INDIRECT_BIT, 0, 1, &mb, 0, null(), 0, null());
                    }
                    ok(f!(fd, vkEndCommandBuffer)(cb), "vkEndCommandBuffer")?;
                }
                self.seg_cbs = cbs;
            }
            let sub = VkSubmitInfo { commandBufferCount: 1, pCommandBuffers: &self.seg_cbs[k], ..Default::default() };
            ok(f!(fd, vkQueueSubmit)(self.q, 1, &sub, self.fence), "vkQueueSubmit")?;
            ok(f!(fd, vkWaitForFences)(d, 1, &self.fence, VK_TRUE, u64::MAX), "vkWaitForFences")?;
            ok(f!(fd, vkResetFences)(d, 1, &self.fence), "vkResetFences")?;
        }
        Ok(())
    }

    /// submit the recorded step `n` times back to back (no host work between them), wait for the last
    pub fn step(&mut self, n: u32) -> Result<StepStats, String> {
        if !self.recorded { self.record()? }
        let (d, fd) = (self.g.device, &self.g.fd);
        let t = Instant::now();
        let sub = VkSubmitInfo { commandBufferCount: 1, pCommandBuffers: &self.step_cb, ..Default::default() };
        unsafe {
            for k in 0..n {
                let fence = if k + 1 == n { self.fence } else { VkFence::NULL };
                ok(f!(fd, vkQueueSubmit)(self.q, 1, &sub, fence), "vkQueueSubmit")?;
            }
            if n > 0 {
                ok(f!(fd, vkWaitForFences)(d, 1, &self.fence, VK_TRUE, u64::MAX), "vkWaitForFences")?;
                ok(f!(fd, vkResetFences)(d, 1, &self.fence), "vkResetFences")?;
            }
            let mut st = StepStats { steps: n, wall_ms: t.elapsed().as_secs_f64() * 1e3, gpu_ms_last: None };
            if self.g.timestamps && n > 0 {
                let mut ts = [0u64; 2];
                ok(f!(fd, vkGetQueryPoolResults)(d, self.qp, 0, 2, 16, ts.as_mut_ptr() as *mut c_void, 8, VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT),
                   "vkGetQueryPoolResults")?;
                st.gpu_ms_last = Some(ts[1].wrapping_sub(ts[0]) as f64 * self.g.props.limits.timestampPeriod as f64 / 1e6);
            }
            Ok(st)
        }
    }

    /// per-pass GPU ms of the last submitted step (empty unless OMNI_GPU_PROFILE=1)
    pub fn pass_ms(&self) -> Result<Vec<f64>, String> {
        if !self.profile || self.pq == VkQueryPool::NULL { return Ok(vec![]) }
        let n = self.passes.len() + 1; let mut ts = vec![0u64; n];
        unsafe { ok(f!(self.g.fd, vkGetQueryPoolResults)(self.g.device, self.pq, 0, n as u32, n * 8, ts.as_mut_ptr() as *mut c_void, 8, VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT), "vkGetQueryPoolResults")?; }
        let per = self.g.props.limits.timestampPeriod as f64 / 1e6;
        Ok(ts.windows(2).map(|w| w[1].wrapping_sub(w[0]) as f64 * per).collect())
    }
    pub fn passes(&self) -> usize { self.passes.len() }
    pub fn buffers(&self) -> usize { self.bufs.len() }
    pub fn size(&self, i: usize) -> u64 { self.bufs[i].2 }
    pub fn bytes(&self) -> u64 { self.bufs.iter().zip(&self.offs).filter(|(_, o)| o.1).map(|(b, _)| b.2).sum() }
}

impl Drop for Session<'_> {
    fn drop(&mut self) {
        let (d, fd) = (self.g.device, &self.g.fd);
        unsafe {
            if let Some(f) = fd.vkDeviceWaitIdle { f(d); }
            for p in self.passes.drain(..) {
                if let Some(f) = fd.vkDestroyPipeline { f(d, p.pipe, null()) }
                if let Some(f) = fd.vkDestroyDescriptorPool { f(d, p.pool, null()) }
                if let Some(f) = fd.vkDestroyPipelineLayout { f(d, p.pl, null()) }
                if let Some(f) = fd.vkDestroyDescriptorSetLayout { f(d, p.dsl, null()) }
            }
            for m in self.modules.drain(..) { if let Some(f) = fd.vkDestroyShaderModule { f(d, m, null()) } }
            if let Some((b, m, _, _)) = self.stage.take() {
                if let Some(f) = fd.vkUnmapMemory { f(d, m) }
                if let Some(f) = fd.vkDestroyBuffer { f(d, b, null()) }
                if let Some(f) = fd.vkFreeMemory { f(d, m, null()) }
            }
            let owned: Vec<bool> = self.offs.drain(..).map(|o| o.1).collect();
            for ((b, m, _), own) in self.bufs.drain(..).zip(owned) {
                if !own { continue }
                if let Some(f) = fd.vkDestroyBuffer { f(d, b, null()) }
                if let Some(f) = fd.vkFreeMemory { f(d, m, null()) }
            }
            if self.g.timestamps { if let Some(f) = fd.vkDestroyQueryPool { f(d, self.qp, null()) } }
            if self.pq != VkQueryPool::NULL { if let Some(f) = fd.vkDestroyQueryPool { f(d, self.pq, null()) } }
            if let Some(f) = fd.vkDestroyFence { f(d, self.fence, null()) }
            if let Some(f) = fd.vkDestroyCommandPool { f(d, self.cpool, null()) }
        }
    }
}
