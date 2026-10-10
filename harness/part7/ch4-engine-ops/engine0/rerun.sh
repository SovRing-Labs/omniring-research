# ENGINE-0 rerun (from omni-render-claude root)
set -e
cd results/doctor-interp/engine0
g++ -O2 -std=c++17 -mavx2 -mfma -fopenmp -w -o driver driver.cpp
B=../../../target/release/omni-render; D=$PWD/driver; rm -f specs.jsonl specs.jsonl.oracle-map.json
$B core --abc blackbox --cmd $D --fn dot8 --args f32list,f32list --ret f32 --equation "(fold (range 0 (len a0)) 0 (+ acc1.0 (* (idx a0 item1) (idx a1 item1))))" --out specs.jsonl --append
$B core --abc blackbox --cmd $D --fn rms_row --args f32list,f32list --ret f32list --equation "(map a0 (/ (* (idx a0 item1) (idx a1 item1)) (sqrt (+ (/ (fold (range 0 (len a0)) 0 (+ acc2.0 (* (idx a0 item2) (idx a0 item2)))) (len a0)) 1.1920928955078125e-07f))))" --out specs.jsonl --append
$B core --abc blackbox --cmd $D --fn sgemm --args f32list,f32list,int,int,int --len 0=a2*a4 --len 1=a4*a3 --int-range 1:6 --ret f32list --equation "(map (range 0 (* a2 a3)) (fold (range 0 a4) 0 (+ acc2.0 (* (idx a0 (+ (* (/ item1 a3) a4) item2)) (idx a1 (+ (* item2 a3) (% item1 a3)))))))" --out specs.jsonl --append
$B core --abc wall --specs specs.jsonl --src driver.cpp --out specs.wall.jsonl --refused refused.jsonl --seed-leaks
$B core --abc need --src ../../../src/layout.rs --needs specs.wall.jsonl --emit --build-dir /tmp/en-rerun --out impl.jsonl > impl.log
