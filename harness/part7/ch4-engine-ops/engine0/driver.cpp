// ENGINE-0 probe driver (reader side of the wall): includes OUR engine read-only and answers op calls on stdin.
// Line in:  op args… (f32list = "n v1 … vn", int, f32)   ·   line out: the result values (space separated), or "x".
// The doctor's black-box reader sees only these lines; the spec's equation is authored from the op's published math.
#include "<workspace>/projects/thead-trial/engine/omni_train/omni_train.cpp"
#include <iostream>
#include <sstream>
using namespace ot;
static std::vector<float> rd(std::istringstream &s) { size_t n; s >> n; std::vector<float> v(n); for (auto &x : v) s >> x; return v; }
int main() {
    std::cout.precision(9); std::string line;
    while (std::getline(std::cin, line)) {
        std::istringstream s(line); std::string op; s >> op;
        if (op == "dot8") { auto a = rd(s), b = rd(s); if (a.size() != b.size()) { std::cout << "x\n"; continue; } std::cout << dot8(a.data(), b.data(), (int)a.size()) << "\n"; }
        else if (op == "rms_row") { auto x = rd(s), g = rd(s); if (x.size() != g.size() || x.empty()) { std::cout << "x\n"; continue; }
            int D = (int)x.size(); std::vector<float> y(D); float r; rms_fwd(x.data(), g.data(), y.data(), &r, 1, D);
            for (int i = 0; i < D; i++) std::cout << (i ? " " : "") << y[i]; std::cout << "\n"; }
        else if (op == "sgemm") { auto A = rd(s), B = rd(s); int M, N, K; s >> M >> N >> K;
            if (M <= 0 || N <= 0 || K <= 0 || (int)A.size() != M * K || (int)B.size() != K * N) { std::cout << "x\n"; continue; }
            std::vector<float> C((size_t)M * N); sgemm(M, N, K, A.data(), K, false, B.data(), N, false, C.data(), N, false, false);
            for (int i = 0; i < M * N; i++) std::cout << (i ? " " : "") << C[i]; std::cout << "\n"; }
        else if (op == "rms_bwd_dx" || op == "rms_bwd_dg") { auto x = rd(s), g = rd(s), dy = rd(s); if (x.size() != g.size() || x.size() != dy.size() || x.empty()) { std::cout << "x\n"; continue; }
            int D = (int)x.size(); std::vector<float> y(D), dx(D), dg(D, 0.f); float r; rms_fwd(x.data(), g.data(), y.data(), &r, 1, D);
            rms_bwd(x.data(), g.data(), &r, dy.data(), dx.data(), dg.data(), 1, D, false);
            const std::vector<float> &o = op == "rms_bwd_dx" ? dx : dg; for (int i = 0; i < D; i++) std::cout << (i ? " " : "") << o[i]; std::cout << "\n"; }
        else if (op == "mem_fwd") { auto q = rd(s), k = rd(s), v = rd(s); size_t nq, nk; s >> nq; std::vector<int> bq(nq); for (auto &x : bq) s >> x; s >> nk; std::vector<int> bk(nk); for (auto &x : bk) s >> x;
            int T, DH; s >> T >> DH; if (T <= 0 || DH <= 0 || (int)q.size() != T * DH || (int)k.size() != T * DH || (int)v.size() != T * DH || (int)nq != T || (int)nk != T) { std::cout << "x\n"; continue; }
            std::vector<float> y((size_t)T * DH), den(T); mem_fwd_core(q.data(), k.data(), v.data(), DH, bq.data(), bk.data(), y.data(), den.data(), 1, T, DH);
            for (int i = 0; i < T * DH; i++) std::cout << (i ? " " : "") << y[i]; std::cout << "\n"; }
        else std::cout << "x\n";
        std::cout.flush();
    }
}
