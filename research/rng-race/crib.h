/* First plaintext block of L2C/S2C CLIENT_CHALLENGE_RES, constant in every decrypted capture:
 * 01|2C 00 00 02 34 00.. (the second block 0010108979eed698ad50785502ccb988 is constant too). */
#include <string.h>
static inline int crib_match(const unsigned char *pt, const unsigned char *iv, unsigned char c0) {
    unsigned char want[16] = {0}; want[0] = c0; want[3] = 0x02; want[4] = 0x34;
    for (int i = 0; i < 16; i++) if ((unsigned char)(pt[i] ^ iv[i]) != want[i]) return 0;
    return 1;
}
