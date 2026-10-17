/* seedscan: like ddon_common_key_bruteforce but fast: seeds [s0,s1) x depth [0,D).
 * usage: seedscan <cipher16hex> <login|game> <s0> <s1> <D> */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>
#include "camellia.h"
#include "crib.h"
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
int main(int argc, char **argv) {
    if (argc < 6) return 2;
    unsigned char ct[16];
    for (int i = 0; i < 16; i++) sscanf(argv[1] + 2 * i, "%2hhx", &ct[i]);
    unsigned char c0 = strcmp(argv[2], "game") ? 0x01 : 0x2C;
    long long s0 = atoll(argv[3]), s1 = atoll(argv[4]); int D = atoi(argv[5]);
#pragma omp parallel for schedule(dynamic, 64)
    for (long long s = s0; s < s1; s++) {
        rng_t r; rng_init(&r, (uint32_t)s);
        unsigned char win[32]; KEY_TABLE_TYPE kt; unsigned char pt[16];
        for (int i = 0; i < 32; i++) win[i] = ALPHA[rng_next(&r) & 63];
        for (int d = 0; d < D; d++) {
            Camellia_Ekeygen(256, win, kt);
            Camellia_DecryptBlock(256, ct, kt, pt);
            if (crib_match(pt, IV, c0)) {
#pragma omp critical
                { printf("HIT seed=%lld depth=%d key=%.32s\n", s, d, win); fflush(stdout); }
            }
            memmove(win, win + 1, 31);
            win[31] = ALPHA[rng_next(&r) & 63];
        }
    }
    printf("done\n");
    return 0;
}
