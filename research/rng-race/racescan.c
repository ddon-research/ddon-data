/* racescan: single-race search. The rng runs clean from init(seed) for p calls, one overlapping
 * pair of calls tears the state into one of the patterns in pat2.h, then the sequence runs clean
 * again for d calls before the 32 key chars.
 * usage: racescan <cipher16hex> <login|game> <seed> <p_from> <p_to> <D> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#include "camellia.h"
#include "crib.h"
#include "pat2.h"
static const char ALPHA[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
static const unsigned char IV[16] = "$cbM6WP)aX=%J^zA";
typedef struct { uint32_t x, y, z, w; } rng_t;
static void rng_init(rng_t *r, uint32_t seed) {
    uint32_t v2 = 0x159A55E5, v3 = 521288629, v4 = 88675123, v5 = seed ^ 0xAC9365, v7 = 0;
    for (int i = 0; i < 100; i++) {
        v7 = v2; v2 = v3; v3 = v4;
        uint32_t a = v5 ^ (0x65AC9365u >> (v5 & 3));
        v5 ^= (0x65AC9365u >> (v5 & 3)) ^ (a >> 3) ^ (a >> 4) ^ (a << 3) ^ (a << 4);
        v4 ^= v5 ^ (v5 << 15) ^ ((v5 ^ (v5 << 15)) >> 4) ^ (v4 >> 21);
    }
    r->x = v7; r->y = v2; r->z = v3; r->w = v4;
}
static inline uint32_t rng_next(rng_t *r) {
    uint32_t t = r->x ^ (r->x << 15);
    r->x = r->y; r->y = r->z; r->z = r->w;
    r->w = t ^ r->w ^ ((t ^ (r->w >> 17)) >> 4);
    return r->w;
}
static inline uint32_t g3(uint32_t x1, uint32_t x2, uint32_t w) {
    uint32_t t = (x1 << 15) ^ x2;
    return t ^ w ^ ((t ^ (w >> 17)) >> 4);
}
int main(int argc, char **argv) {
    if (argc < 7) return 2;
    unsigned char ct[16];
    for (int i = 0; i < 16; i++) sscanf(argv[1] + 2 * i, "%2hhx", &ct[i]);
    unsigned char c0 = strcmp(argv[2], "game") ? 0x01 : 0x2C;
    uint32_t seed = strtoul(argv[3], 0, 0);
    long long p0 = atoll(argv[4]), p1 = atoll(argv[5]); long long D = atoll(argv[6]);
    rng_t base; rng_init(&base, seed);
    for (long long i = 0; i < p0; i++) rng_next(&base);
    long long n = (p1 - p0) * NPAT;
    long long hits = 0;
#pragma omp parallel for schedule(dynamic, 1) reduction(+:hits)
    for (long long j = 0; j < n; j++) {
        long long p = p0 + j / NPAT; int k = (int)(j % NPAT);
        rng_t r = base;
        for (long long i = p0; i < p; i++) rng_next(&r);
        uint32_t v[16] = {r.x, r.y, r.z, r.w};
        for (int q = 0; q < NDER; q++) v[4 + q] = g3(v[DER[q][0]], v[DER[q][1]], v[DER[q][2]]);
        rng_t s = {v[PAT[k][0]], v[PAT[k][1]], v[PAT[k][2]], v[PAT[k][3]]};
        unsigned char win[32]; KEY_TABLE_TYPE kt; unsigned char pt[16];
        for (int i = 0; i < 32; i++) win[i] = ALPHA[rng_next(&s) & 63];
        for (long long d = 0; d < D; d++) {
            Camellia_Ekeygen(256, win, kt);
            Camellia_DecryptBlock(256, ct, kt, pt);
            if (crib_match(pt, IV, c0)) {
#pragma omp critical
                { printf("HIT p=%lld pattern=%d depth=%lld key=%.32s\n", p, k, d, win); fflush(stdout); }
                hits++;
            }
            memmove(win, win + 1, 31);
            win[31] = ALPHA[rng_next(&s) & 63];
        }
    }
    printf("done hits=%lld candidates=%lld\n", hits, n * D);
    return 0;
}
