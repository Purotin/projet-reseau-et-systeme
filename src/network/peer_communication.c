#include "peer_communication.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/time.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <time.h>
#define MAX_LENGTH 1024

int py_to_c, c_to_py;

// Ouvrir les pipes de communication avec Python
void open_pipes(char *py_to_c_name, char *c_to_py_name, int *py_to_c_fd, int *c_to_py_fd) {
    // Ouvrir les pipes
    if ((*py_to_c_fd = open(py_to_c_name, O_RDONLY)) < 0) {
        perror("Erreur lors de l'ouverture du pipe de Python vers C");
        exit(EXIT_FAILURE);
    }

    if ((*c_to_py_fd = open(c_to_py_name, O_WRONLY)) < 0) {
        perror("Erreur lors de l'ouverture du pipe de C vers Python");
        exit(EXIT_FAILURE);
    }
}

// Créer un socket pour agir en tant que serveur multicast
int create_server_socket(char *multicast_ip, char *port) {
    struct sockaddr_in server_addr;
    int server_sockfd;
    struct ip_mreq mreq;

    // Créer un socket pour agir en tant que serveur
    if ((server_sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket serveur");
        exit(EXIT_FAILURE);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(atoi(port));
    server_addr.sin_addr.s_addr = INADDR_ANY;  // Écouter sur toutes les interfaces réseau

    if (bind(server_sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Erreur lors de la liaison du socket serveur");
        exit(EXIT_FAILURE);
    }

    // Rejoindre le groupe multicast
    mreq.imr_multiaddr.s_addr = inet_addr(multicast_ip);
    mreq.imr_interface.s_addr = htonl(INADDR_ANY);
    if (setsockopt(server_sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char *)&mreq, sizeof(mreq)) < 0) {
        perror("Erreur lors de l'adhésion au groupe multicast");
        exit(EXIT_FAILURE);
    }

    return server_sockfd;
}


// Créer un socket pour agir en tant que client multicast
int create_client_socket(char *multicast_ip, char *port, struct sockaddr_in *peer_addr, socklen_t *peer_addr_len) {
    int client_sockfd;

    // Créer un socket pour agir en tant que client
    if ((client_sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket client");
        exit(EXIT_FAILURE);
    }

    peer_addr->sin_family = AF_INET;
    peer_addr->sin_port = htons(atoi(port));  // Se connecter au port du pair
    peer_addr->sin_addr.s_addr = inet_addr(multicast_ip);  // Se connecter à l'adresse IP multicast   

    *peer_addr_len = sizeof(*peer_addr);

    return client_sockfd;
}



// Lire les messages du pair et les écrire dans le pipe vers Python
void handle_communication(int py_to_c, int c_to_py, int client_sockfd, struct sockaddr_in *peer_addr, socklen_t peer_addr_len, int sockfd) { 
    fd_set readfds;
    char message[MAX_LENGTH];
    struct sockaddr_in peer_addr_recv;
    socklen_t peer_addr_len_recv = sizeof(peer_addr_recv);
    
    srand(time(0));

    char random_number_str[6];  // 4 chiffres + 1 caractère de fin de chaîne

    sprintf(random_number_str, "%d", (rand() % (9999 - 1000 + 1)) + 1000);
    printf("Le nombre aléatoire généré est : %s\n", random_number_str);

    char my_ip[INET_ADDRSTRLEN];

    sendto(client_sockfd, &random_number_str, sizeof(random_number_str), 0, (struct sockaddr *)peer_addr, peer_addr_len);

    // Attendre que nous recevions notre propre adresse IP
    while (1) {
        int num_bytes_recv = recvfrom(sockfd, message, MAX_LENGTH, 0, (struct sockaddr *)&peer_addr_recv, &peer_addr_len_recv);
        if (num_bytes_recv > 0) {
            message[num_bytes_recv] = '\0';  // Assurez-vous que le message est terminé
            if (strcmp(message, random_number_str) == 0) {
                inet_ntop(AF_INET, &(peer_addr_recv.sin_addr), my_ip, INET_ADDRSTRLEN);
                memset(message, '\0', MAX_LENGTH);
                break;
            }
            
        }
    }

    while (1) {
        FD_ZERO(&readfds);
        FD_SET(py_to_c, &readfds);
        FD_SET(sockfd, &readfds);

        int max_fd = (py_to_c > sockfd) ? py_to_c : sockfd;

        if (select(max_fd + 1, &readfds, NULL, NULL, NULL) < 0) {
            perror("Erreur lors de l'appel à select");
            exit(EXIT_FAILURE);
        }

        if (FD_ISSET(py_to_c, &readfds)) {
            // Lire une ligne depuis le pipe Python vers C
            int num_bytes_read = read(py_to_c, message, MAX_LENGTH);
            if (num_bytes_read > 0) {
                message[num_bytes_read] = '\0';  // Assurez-vous que le message est terminé
                // Envoyer le message au pair
                sendto(client_sockfd, message, num_bytes_read, 0, (struct sockaddr *)peer_addr, peer_addr_len);
            }
        }

        if (FD_ISSET(sockfd, &readfds)) {
            // Recevoir un message du pair
            int num_bytes_recv = recvfrom(sockfd, message, MAX_LENGTH, 0, (struct sockaddr *)&peer_addr_recv, &peer_addr_len_recv);
            if (num_bytes_recv > 0) {
                message[num_bytes_recv] = '\0';  // Assurez-vous que le message est terminé
                // Écrire le message dans le pipe C vers Python
                
                //tester si le message vient de my_ip
                if (strcmp(inet_ntoa(peer_addr_recv.sin_addr), my_ip) != 0) {
                    write(c_to_py, message, num_bytes_recv);
                }
            }
        }

        memset(message, '\0', MAX_LENGTH);
    }
}
