/* cbcdec: Camellia-256-CBC decrypt hex with a 32-char key and the DDON IV. usage: cbcdec <key32> <hex> */
#include <stdio.h>
#include <string.h>
#include "camellia.h"
int main(int argc, char **argv) {
    unsigned char iv[16]; memcpy(iv, "$cbM6WP)aX=%J^zA", 16);
    KEY_TABLE_TYPE kt; Camellia_Ekeygen(256, (unsigned char *)argv[1], kt);
    size_t n = strlen(argv[2]) / 2; unsigned char buf[4096];
    for (size_t i = 0; i < n; i++) sscanf(argv[2] + 2 * i, "%2hhx", &buf[i]);
    for (size_t b = 0; b + 16 <= n; b += 16) {
        unsigned char pt[16]; Camellia_DecryptBlock(256, buf + b, kt, pt);
        for (int i = 0; i < 16; i++) { pt[i] ^= iv[i]; printf("%02x", pt[i]); }
        memcpy(iv, buf + b, 16); printf("\n");
    }
}
