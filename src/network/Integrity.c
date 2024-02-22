#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>

// Fonction pour calculer l'empreinte SHA-256 d'un message
void calculateHash(const unsigned char *message, size_t messageLength, unsigned char *hash) {
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL);
    EVP_DigestUpdate(mdctx, message, messageLength);
    unsigned int hashLen;
    EVP_DigestFinal_ex(mdctx, hash, &hashLen);
    EVP_MD_CTX_free(mdctx);
}

// Fonction pour vérifier l'intégrité d'un message
int verifyIntegrity(const unsigned char *message, size_t messageLength, const unsigned char *expectedHash) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    calculateHash(message, messageLength, hash);

    if (memcmp(hash, expectedHash, 32) == 0) {
        return 1; // L'empreinte correspond, le message est intègre
    } else {
        return 0; // L'empreinte ne correspond pas, le message a été altéré
    }
}

int main() {
    const unsigned char *message = (unsigned char *)"Hello, world!";
    size_t messageLength = strlen((const char *)message);

    // Calculer l'empreinte du message original
    unsigned char expectedHash[32];
    calculateHash(message, messageLength, expectedHash);

    // Vérifier l'intégrité du message
    if (verifyIntegrity(message, messageLength, expectedHash)) {
        printf("Le message est intègre.\n");
    } else {
        printf("Le message a été altéré.\n");
    }

    return 0;
}