/* mkcase: synthesize a login-crib ciphertext for a single-race scenario (self-test for racescan).
 * usage: mkcase <seed> <p> <pattern> <d> */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "camellia.h"
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
static uint32_t rng_next(rng_t *r) {
    uint32_t t = r->x ^ (r->x << 15);
    r->x = r->y; r->y = r->z; r->z = r->w;
    r->w = t ^ r->w ^ ((t ^ (r->w >> 17)) >> 4);
    return r->w;
}
static uint32_t g3(uint32_t x1, uint32_t x2, uint32_t w) { uint32_t t = (x1 << 15) ^ x2; return t ^ w ^ ((t ^ (w >> 17)) >> 4); }
int main(int argc, char **argv) {
    rng_t r; rng_init(&r, strtoul(argv[1], 0, 0));
    long p = atol(argv[2]); int k = atoi(argv[3]); long d = atol(argv[4]);
    for (long i = 0; i < p; i++) rng_next(&r);
    uint32_t v[16] = {r.x, r.y, r.z, r.w};
    for (int q = 0; q < NDER; q++) v[4 + q] = g3(v[DER[q][0]], v[DER[q][1]], v[DER[q][2]]);
    rng_t s = {v[PAT[k][0]], v[PAT[k][1]], v[PAT[k][2]], v[PAT[k][3]]};
    for (long i = 0; i < d; i++) rng_next(&s);
    unsigned char key[33] = {0};
    for (int i = 0; i < 32; i++) key[i] = ALPHA[rng_next(&s) & 63];
    unsigned char pt[16] = {0x01, 0, 0, 0x02, 0x34}, ct[16]; KEY_TABLE_TYPE kt;
    for (int i = 0; i < 16; i++) pt[i] ^= IV[i];
    Camellia_Ekeygen(256, key, kt); Camellia_EncryptBlock(256, pt, kt, ct);
    for (int i = 0; i < 16; i++) printf("%02x", ct[i]);
    printf(" %s\n", key);
}
