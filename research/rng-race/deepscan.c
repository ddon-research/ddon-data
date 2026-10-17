/* deepscan: scan a clean (race-free) DDON rng sequence to large depth for a Camellia key
 * whose first decrypted block matches the login/game crib.
 * usage: deepscan <cipher16hex> <login|game> <seed> <depth_from> <depth_to>
 *        deepscan <cipher16hex> <login|game> state:<x>,<y>,<z>,<w> <depth_from> <depth_to>
 * Depth = number of rng calls before the first key char (key chars are outputs depth+1..depth+32).
 */
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
    if (argc < 6) { fprintf(stderr, "usage: deepscan <cipher16hex> <login|game> <seed|state:x,y,z,w> <from> <to>\n"); return 2; }
    unsigned char ct[16];
    for (int i = 0; i < 16; i++) sscanf(argv[1] + 2 * i, "%2hhx", &ct[i]);
    unsigned char crib[1] = {0x01};
    if (!strcmp(argv[2], "game")) crib[0] = 0x2C;
    rng_t base;
    if (!strncmp(argv[3], "state:", 6)) sscanf(argv[3] + 6, "%x,%x,%x,%x", &base.x, &base.y, &base.z, &base.w);
    else rng_init(&base, (uint32_t)strtoul(argv[3], 0, 0));
    long long from = atoll(argv[4]), to = atoll(argv[5]);
    int nt = omp_get_max_threads();
    long long chunk = (to - from + nt - 1) / nt;
    long long hits = 0;
#pragma omp parallel reduction(+:hits)
    {
        int id = omp_get_thread_num();
        long long a = from + id * chunk, b = a + chunk; if (b > to) b = to;
        if (a < b) {
            rng_t r = base;
            for (long long i = 0; i < a; i++) rng_next(&r);
            unsigned char ring[64];
            for (int i = 0; i < 32; i++) ring[i] = ring[i + 32] = 0;
            unsigned char key[32];
            /* window of 32 chars ending at depth d+32 */
            unsigned char win[32 + 1 << 0];
            for (int i = 0; i < 32; i++) win[i] = ALPHA[rng_next(&r) & 63];
            KEY_TABLE_TYPE kt; unsigned char pt[16];
            for (long long d = a; d < b; d++) {
                Camellia_Ekeygen(256, win, kt);
                Camellia_DecryptBlock(256, ct, kt, pt);
                if (crib_match(pt, IV, crib[0])) {
                    memcpy(key, win, 32);
#pragma omp critical
                    { printf("HIT depth=%lld key=%.32s\n", d, key); fflush(stdout); }
                    hits++;
                }
                memmove(win, win + 1, 31);
                win[31] = ALPHA[rng_next(&r) & 63];
            }
        }
    }
    printf("done hits=%lld scanned=%lld\n", hits, to - from);
    return 0;
}
