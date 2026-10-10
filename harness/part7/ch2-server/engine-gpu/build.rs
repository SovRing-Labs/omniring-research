// link the CPU engine so the loader keeps it as a dependency (DT_NEEDED): dlsym on this library's handle then finds every engine symbol
// this library does not define. OMR_CPU_LIB_DIR = the directory of libomnitrain_trial.so at build time; at run time the CPU library sits
// beside this one ($ORIGIN) or on LD_LIBRARY_PATH.
fn main() {
    let dir = std::env::var("OMR_CPU_LIB_DIR").unwrap_or_else(|_| "<workspace>/projects/thead-trial/engine/omni_train".into());
    println!("cargo:rustc-link-search=native={dir}");
    println!("cargo:rustc-link-arg=-Wl,--no-as-needed");
    println!("cargo:rustc-link-arg=-lomnitrain_trial");
    println!("cargo:rustc-link-arg=-Wl,-rpath,$ORIGIN");
    println!("cargo:rerun-if-env-changed=OMR_CPU_LIB_DIR");
}
