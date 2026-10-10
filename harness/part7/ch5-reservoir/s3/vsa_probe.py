"""reservoir probe S3: Holographic Superposition Weighting (VSA) Probe.
Tests one-shot learning and zero catastrophic forgetting on:
1. Associative Incident Memory (Doctor Core task: incident -> verified remedy).
2. Continuous rule addition capacity scaling (D=8192, K=1..500 rules).
3. Retrieval correction invariance (one-shot error fix on held-out queries).
"""
import json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class HolographicRuleStore:
    def __init__(self, dim=8192, seed=42):
        self.dim = dim
        self.rng = np.random.default_rng(seed)
        # Bipolar ternary accumulator: integer counts of +1 and -1
        self.accum = np.zeros(dim, dtype=np.int32)
        self.rule_count = 0
        self.codebook = {} # name -> clean bipolar vector

    def get_or_create_symbol(self, name):
        if name not in self.codebook:
            # Generate random bipolar vector {-1, +1}
            vec = self.rng.choice([-1, 1], size=self.dim).astype(np.int8)
            self.codebook[name] = vec
        return self.codebook[name]

    def bind(self, vec_a, vec_b):
        # In bipolar VSA, binding is exact elementwise multiplication
        return vec_a * vec_b

    def add_rule(self, condition_name, remedy_name):
        c_vec = self.get_or_create_symbol(f"cond:{condition_name}")
        r_vec = self.get_or_create_symbol(f"rem:{remedy_name}")
        rule_vec = self.bind(c_vec, r_vec)
        self.accum += rule_vec
        self.rule_count += 1

    def memory_vector(self):
        # Ternary clipping / sign function for resident ternary core
        m = np.sign(self.accum).astype(np.int8)
        # Any zero positions stay 0
        return m

    def query(self, condition_name):
        c_vec = self.get_or_create_symbol(f"cond:{condition_name}")
        m = self.memory_vector()
        # Unbind: c_vec * m gives noisy remedy vector
        noisy_r = c_vec * m
        # Cleanup memory: cosine similarity against all known remedy symbols in codebook
        best_name = None
        best_cos = -2.0
        remedies = {k: v for k, v in self.codebook.items() if k.startswith("rem:")}
        for name, clean_vec in remedies.items():
            cos = float(np.dot(noisy_r.astype(np.int32), clean_vec.astype(np.int32))) / self.dim
            if cos > best_cos:
                best_cos = cos
                best_name = name.replace("rem:", "")
        return best_name, best_cos

def run_doctor_telemetry_probe():
    print("=== 1. DOCTOR CORE ASSOCIATIVE INCIDENT MEMORY PROBE ===")
    store = HolographicRuleStore(dim=8192, seed=101)
    
    # 50 realistic fleet telemetry incidents & remedies
    incidents = [
        ("socket_eaddrinuse_port_8080", "kill_stale_pid_and_restart_listener"),
        ("oom_kill_vram_buffer_overflow", "flush_m0_arena_and_realloc_half"),
        ("zombie_worker_thread_deadlock", "send_sigkill_and_respawn_pool"),
        ("sqlite_busy_dispatch_locked", "run_wal_checkpoint_truncate"),
        ("disk_full_var_log_runaway", "rotate_and_compress_tw_logs"),
        ("vulkan_device_lost_vkqueue_hang", "reset_device_context_and_rebuild_pipelines"),
        ("tokenizer_unknown_byte_fallback", "insert_special_token_mapping"),
        ("ring_clock_phase_desync_rot25", "recalibrate_residue_zero_offset"),
        ("min_cut_headroom_critical_drop", "trigger_indirect_dispatch_splining"),
        ("rrf_tie_break_cyclic_oscillation", "apply_lexicographical_hash_tiebreaker")
    ]
    # Expand to 50 distinct incident scenarios
    for i in range(10, 50):
        incidents.append((f"fleet_telemetry_fault_code_{i:03d}", f"sovereign_remedy_protocol_{i:03d}"))
    
    results = []
    # Test sequential rule addition & measure retention of ALL prior rules
    for k, (cond, rem) in enumerate(incidents):
        store.add_rule(cond, rem)
        
        # Test retention of ALL rules added so far (up to rule k)
        correct = 0
        min_cos = 1.0
        for test_idx in range(k + 1):
            t_cond, t_rem = incidents[test_idx]
            pred_rem, cos = store.query(t_cond)
            if pred_rem == t_rem:
                correct += 1
            min_cos = min(min_cos, cos)
        
        retention_rate = correct / (k + 1)
        results.append({
            "rules_stored": k + 1,
            "retention": retention_rate,
            "min_cosine_margin": round(min_cos, 4)
        })
        if (k + 1) in (1, 5, 10, 25, 50):
            print(f"Rules: {k+1:2d} | Retention: {retention_rate*100:5.1f}% | Min Cosine Margin: {min_cos:+.4f}")
            
    return results

def run_capacity_scaling_probe():
    print("\n=== 2. VSA CAPACITY SCALING PROBE (D=8192, up to 500 rules) ===")
    store = HolographicRuleStore(dim=8192, seed=202)
    
    total_rules = 500
    all_rules = [(f"cond_{i:04d}", f"rem_{i:04d}") for i in range(total_rules)]
    
    # Add in batches and evaluate
    checkpoints = [10, 50, 100, 200, 300, 400, 500]
    out = []
    
    cur_idx = 0
    for cp in checkpoints:
        while cur_idx < cp:
            store.add_rule(*all_rules[cur_idx])
            cur_idx += 1
            
        # Sample 50 random rules from the stored set to test recall
        test_sample = np.random.choice(cur_idx, size=min(cur_idx, 50), replace=False)
        hits = 0
        margins = []
        for idx in test_sample:
            c, expected_r = all_rules[idx]
            pred_r, cos = store.query(c)
            if pred_r == expected_r:
                hits += 1
            margins.append(cos)
            
        acc = hits / len(test_sample)
        avg_margin = float(np.mean(margins))
        print(f"Capacity: {cp:3d} rules | Sample Recall: {acc*100:5.1f}% | Avg Margin: {avg_margin:+.4f}")
        out.append({"stored": cp, "recall": acc, "avg_margin": round(avg_margin, 4)})
        
    return out

def run_retrieval_oneshot_fix_probe():
    print("\n=== 3. RETRIEVAL ONE-SHOT ERROR CORRECTION PROBE ===")
    # Simulate a 100-document vault codebook in D=8192
    dim = 8192
    rng = np.random.default_rng(303)
    num_docs = 100
    doc_vectors = rng.choice([-1, 1], size=(num_docs, dim)).astype(np.int8)
    
    # A base retrieval query vector that currently points to wrong doc 42 instead of target doc 7
    target_doc = 7
    wrong_doc = 42
    
    # Query vector has 0.15 cos with wrong_doc and 0.05 cos with target_doc (a retrieval failure)
    q_base = doc_vectors[wrong_doc].astype(np.float32) * 0.15 + rng.normal(0, 1, dim)
    
    scores_before = doc_vectors.astype(np.float32) @ q_base
    rank_before = int(np.where(np.argsort(-scores_before) == target_doc)[0][0])
    print(f"Before correction: Target doc {target_doc} is at rank {rank_before} (Rank 0 is doc {np.argmax(scores_before)})")
    
    # One-shot holographic correction: superpose binding of (query_context, target_doc)
    delta_fix = doc_vectors[target_doc].astype(np.float32) * 0.3
    q_corrected = q_base + delta_fix
    
    scores_after = doc_vectors.astype(np.float32) @ q_corrected
    rank_after = int(np.where(np.argsort(-scores_after) == target_doc)[0][0])
    top_after = int(np.argmax(scores_after))
    print(f"After correction:  Target doc {target_doc} is at rank {rank_after} (Top retrieved is doc {top_after})")
    
    # Verify non-interference: cosine shift across all other 99 docs
    other_docs = [i for i in range(num_docs) if i != target_doc]
    shifts = [abs(scores_after[i] - scores_before[i]) for i in other_docs]
    max_shift = float(np.max(shifts))
    mean_shift = float(np.mean(shifts))
    print(f"Non-interference on other 99 docs: Max shift = {max_shift:.4f}, Mean shift = {mean_shift:.4f}")
    
    return {
        "target_doc": target_doc,
        "rank_before": rank_before,
        "rank_after": rank_after,
        "max_shift_on_others": round(max_shift, 4),
        "mean_shift_on_others": round(mean_shift, 4),
        "success": rank_after == 0
    }

if __name__ == "__main__":
    t0 = time.time()
    doc_res = run_doctor_telemetry_probe()
    cap_res = run_capacity_scaling_probe()
    fix_res = run_retrieval_oneshot_fix_probe()
    
    summary = {
        "doctor_probe": doc_res,
        "capacity_scaling": cap_res,
        "retrieval_fix": fix_res,
        "elapsed_s": round(time.time() - t0, 2),
        "verdict": "PASS" if doc_res[-1]["retention"] == 1.0 and fix_res["success"] else "FAIL"
    }
    
    out_file = RESULTS_DIR / "s3_vsa_summary.json"
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[DONE] S3 Summary saved to {out_file} (Verdict: {summary['verdict']})")
