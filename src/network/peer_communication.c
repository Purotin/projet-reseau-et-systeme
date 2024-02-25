#include "peer_communication.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/time.h>

#define MAX_LENGTH 1024


int py_to_c, c_to_py;

// // Recevoir les messages entrants du pair et les écrire dans le pipe vers Python
// void *receive_messages(void *socket) {
//     int sockfd = *((int *)socket);
//     char message[MAX_LENGTH];
//     struct sockaddr_in peer_addr;
//     socklen_t peer_addr_len = sizeof(peer_addr);

   
//     if (recvfrom(sockfd, message, MAX_LENGTH, 0, (struct sockaddr *)&peer_addr, &peer_addr_len) > 0) {
//         // Écrire le message dans le pipe vers Python
//         write(c_to_py, message, strlen(message));
//     }
    

//     memset(message, '\0', MAX_LENGTH);

//     return NULL;
// }

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

// Créer un socket pour agir en tant que serveur
int create_server_socket(char *port) {
    struct sockaddr_in server_addr;
    int server_sockfd;

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


    return server_sockfd;
}

// Créer un socket pour agir en tant que client
int create_client_socket(char *ip, char *port, struct sockaddr_in *peer_addr, socklen_t *peer_addr_len) {
    int client_sockfd;

    // Créer un socket pour agir en tant que client
    if ((client_sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket client");
        exit(EXIT_FAILURE);
    }

    peer_addr->sin_family = AF_INET;
    peer_addr->sin_port = htons(atoi(port));  // Se connecter au port du pair
    peer_addr->sin_addr.s_addr = inet_addr(ip);  // Se connecter à l'adresse IP du pair   

    *peer_addr_len = sizeof(*peer_addr);

    return client_sockfd;
}


// // Lire les messages entrants de Python et les envoyer au pair
// void read_and_send_messages(int client_sockfd, struct sockaddr_in *peer_addr, socklen_t peer_addr_len) {
//     char message[MAX_LENGTH];

    
//     // Read a line from the Python to C pipe
//     if (read(py_to_c, message, MAX_LENGTH) > 0) {
//         // Send the message to the peer
//         sendto(client_sockfd, message, strlen(message), 0, (struct sockaddr *)peer_addr, peer_addr_len);
//     }
    

//     memset(message, '\0', MAX_LENGTH);
// }

// Lire les messages du pair et les écrire dans le pipe vers Python
void handle_communication(int py_to_c, int c_to_py, int client_sockfd, struct sockaddr_in *peer_addr, socklen_t peer_addr_len, int sockfd) { 
    fd_set readfds;
    char message[MAX_LENGTH];
    struct sockaddr_in peer_addr_recv;
    socklen_t peer_addr_len_recv = sizeof(peer_addr_recv);

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
            // Read a line from the Python to C pipe
            if (read(py_to_c, message, MAX_LENGTH) > 0) {
                // Send the message to the peer
                sendto(client_sockfd, message, strlen(message), 0, (struct sockaddr *)peer_addr, peer_addr_len);
            }
        }

        if (FD_ISSET(sockfd, &readfds)) {
            // Receive a message from the peer
            if (recvfrom(sockfd, message, MAX_LENGTH, 0, (struct sockaddr *)&peer_addr_recv, &peer_addr_len_recv) > 0) {
                // Write the message to the Python to C pipe
                write(c_to_py, message, strlen(message));
            }
        }

        memset(message, '\0', MAX_LENGTH);
    }
}