// T50 probe (J 10-08, readback confirmed: "a 35-50t as the memory bus with a 50t as the core"; T30-CORE-0 S7 first probe).
// Question: on the pod (EPYC 9575F, AVX-512 BW) is the per-event cost of an omniring FLAT in the ring count when a whole tier fits one
// register? T25/T30 fit one 32-byte AVX2 row (residues < 128); T50 (3…233, residues < 256) fits ONE 64-byte AVX-512 row (two AVX2 rows).
// Two operations, exactly the T25 core's: TICK (VOCAB jump rope: every ring + κ, wrap at m) and TWIST (per-ring gap a − b mod m between
// two points, the T25 kernel's vpsubb/vpcmpgtb/vpand/vpaddb). Each vector path is checked against scalar. Build: gcc -O3 -march=native.
// NOTE: a standalone kernel, not the JIT-rendered t25.rs program (that EVEX port is S7 step 2).
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int odd_primes(int n, uint8_t *out) { int k = 0; for (int p = 3; k < n; p += 2) { int ok = 1; for (int d = 3; d * d <= p; d += 2) if (p % d == 0) { ok = 0; break; } if (ok) out[k++] = (uint8_t)p; } return k; }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }

#define N 1000000   // events
#define W 64        // lanes stored per event (zero-padded beyond the tier)

static void twist_scalar(const uint8_t *a, const uint8_t *b, uint8_t *o, const uint8_t *m, int n) {
    for (int i = 0; i < n; i++) for (int j = 0; j < W; j++) { int d = a[i*W+j] - b[i*W+j]; if (d < 0) d += m[j]; o[i*W+j] = (uint8_t)d; } }
static void twist_avx2(const uint8_t *a, const uint8_t *b, uint8_t *o, const uint8_t *m, int n, int rows) {
    __m256i M0 = _mm256_loadu_si256((const __m256i *)m), M1 = _mm256_loadu_si256((const __m256i *)(m + 32));
    for (int i = 0; i < n; i++) for (int r = 0; r < rows; r++) {
        const uint8_t *pa = a + i*W + 32*r, *pb = b + i*W + 32*r; __m256i M = r ? M1 : M0;
        __m256i x = _mm256_loadu_si256((const __m256i *)pa), y = _mm256_loadu_si256((const __m256i *)pb);
        __m256i d = _mm256_sub_epi8(x, y);
        __m256i lt = _mm256_cmpeq_epi8(_mm256_max_epu8(x, y), y);          // x <= y (unsigned)
        lt = _mm256_andnot_si256(_mm256_cmpeq_epi8(x, y), lt);              // x < y
        _mm256_storeu_si256((__m256i *)(o + i*W + 32*r), _mm256_add_epi8(d, _mm256_and_si256(lt, M))); } }
static void twist_avx512(const uint8_t *a, const uint8_t *b, uint8_t *o, const uint8_t *m, int n) {
    __m512i M = _mm512_loadu_si512(m);
    for (int i = 0; i < n; i++) {
        __m512i x = _mm512_loadu_si512(a + i*W), y = _mm512_loadu_si512(b + i*W);
        __mmask64 lt = _mm512_cmplt_epu8_mask(x, y);
        __m512i d = _mm512_sub_epi8(x, y);
        _mm512_storeu_si512(o + i*W, _mm512_mask_add_epi8(d, lt, d, M)); } }

static void tick_scalar(uint8_t *r, const uint8_t *m, int k, long steps) { for (long s = 0; s < steps; s++) for (int j = 0; j < k; j++) { r[j]++; if (r[j] >= m[j]) r[j] = 0; } }
static void tick_avx2(uint8_t *r, const uint8_t *m, long steps, int rows) {
    __m256i one = _mm256_set1_epi8(1), M0 = _mm256_loadu_si256((const __m256i *)m), M1 = _mm256_loadu_si256((const __m256i *)(m + 32));
    __m256i R0 = _mm256_loadu_si256((const __m256i *)r), R1 = _mm256_loadu_si256((const __m256i *)(r + 32));
    for (long s = 0; s < steps; s++) {
        R0 = _mm256_add_epi8(R0, one); R0 = _mm256_min_epu8(R0, _mm256_sub_epi8(R0, M0));   // r+1 < m keeps r+1; r+1 == m wraps to 0
        if (rows > 1) { R1 = _mm256_add_epi8(R1, one); R1 = _mm256_min_epu8(R1, _mm256_sub_epi8(R1, M1)); } }
    _mm256_storeu_si256((__m256i *)r, R0); _mm256_storeu_si256((__m256i *)(r + 32), R1); }
static void tick_avx512(uint8_t *r, const uint8_t *m, long steps) {
    __m512i one = _mm512_set1_epi8(1), M = _mm512_loadu_si512(m), R = _mm512_loadu_si512(r);
    for (long s = 0; s < steps; s++) { R = _mm512_add_epi8(R, one); R = _mm512_min_epu8(R, _mm512_sub_epi8(R, M)); }
    _mm512_storeu_si512(r, R); }

int main(void) {
    int tiers[3] = {25, 30, 50};
    uint8_t *a = aligned_alloc(64, (size_t)N*W), *b = aligned_alloc(64, (size_t)N*W), *o1 = aligned_alloc(64, (size_t)N*W), *o2 = aligned_alloc(64, (size_t)N*W);
    printf("{\"events\": %d, \"tiers\": [", N);
    for (int t = 0; t < 3; t++) {
        int k = tiers[t]; uint8_t m[W]; memset(m, 0, W); odd_primes(k, m);
        uint8_t mpad[W]; for (int j = 0; j < W; j++) mpad[j] = j < k ? m[j] : 1;   // inert lanes: modulus 1 → residue 0 forever
        srand(7 + k);
        for (long i = 0; i < (long)N*W; i++) { int j = i % W; a[i] = j < k ? rand() % m[j] : 0; b[i] = j < k ? rand() % m[j] : 0; }
        long double logs = 0; for (int j = 0; j < k; j++) logs += __builtin_log10(m[j]);
        int rows2 = k > 32 ? 2 : 1;
        double best_s = 1e9, best_2 = 1e9, best_5 = 1e9;
        for (int rep = 0; rep < 5; rep++) {
            double t0 = now(); twist_scalar(a, b, o1, mpad, N); double t1 = now(); if (t1 - t0 < best_s) best_s = t1 - t0;
            t0 = now(); twist_avx2(a, b, o2, mpad, N, rows2); t1 = now(); if (t1 - t0 < best_2) best_2 = t1 - t0; }
        int bad2 = 0; for (long i = 0; i < (long)N*W; i++) if ((i % W) < k && o1[i] != o2[i]) bad2++;
        for (int rep = 0; rep < 5; rep++) { double t0 = now(); twist_avx512(a, b, o2, mpad, N); double t1 = now(); if (t1 - t0 < best_5) best_5 = t1 - t0; }
        int bad5 = 0; for (long i = 0; i < (long)N*W; i++) if ((i % W) < k && o1[i] != o2[i]) bad5++;
        // tick: 10 M steps of every ring
        long steps = 10000000; uint8_t r0[W] = {0}, r2[W] = {0}, r5[W] = {0};
        double tk2 = 1e9, tk5 = 1e9;
        for (int rep = 0; rep < 3; rep++) { memset(r2, 0, W); double t0 = now(); tick_avx2(r2, mpad, steps, rows2); double t1 = now(); if (t1 - t0 < tk2) tk2 = t1 - t0;
                                            memset(r5, 0, W); t0 = now(); tick_avx512(r5, mpad, steps); t1 = now(); if (t1 - t0 < tk5) tk5 = t1 - t0; }
        tick_scalar(r0, mpad, k, steps);
        int tbad = 0; for (int j = 0; j < k; j++) { if (r0[j] != r2[j]) tbad++; if (r0[j] != r5[j]) tbad++; if (r0[j] != (uint8_t)(steps % m[j])) tbad++; }
        printf("%s{\"tier\": \"T%d\", \"max_ring\": %d, \"states_log10\": %.1f, \"avx2_rows\": %d, \"twist_ns_scalar\": %.2f, \"twist_ns_avx2\": %.3f, \"twist_ns_avx512\": %.3f, "
               "\"tick_ns_avx2\": %.3f, \"tick_ns_avx512\": %.3f, \"mismatch_avx2\": %d, \"mismatch_avx512\": %d, \"tick_mismatch\": %d}",
               t ? ", " : "", k, m[k-1], (double)logs, rows2, best_s*1e9/N, best_2*1e9/N, best_5*1e9/N, tk2*1e9/steps, tk5*1e9/steps, bad2, bad5, tbad);
    }
    FILE *f = fopen("/proc/loadavg", "r"); char la[64] = ""; if (f) { if (!fgets(la, sizeof la, f)) la[0] = 0; fclose(f); } la[strcspn(la, "\n")] = 0;
    printf("], \"loadavg\": \"%s\"}\n", la);
    return 0;
}
