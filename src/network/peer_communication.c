#include "peer_communication.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>

int py_to_c, c_to_py;

// Recevoir les messages entrants du pair et les écrire dans le pipe vers Python
void *receive_messages(void *socket) {
    int sockfd = *((int *)socket);
    char message[MAX_LENGTH];

    while (1) {
        if (recv(sockfd, message, MAX_LENGTH, 0) > 0) {
            // Écrire le message dans le pipe vers Python
            write(c_to_py, message, strlen(message));
        }
    }

    memset(message, '\0', MAX_LENGTH);

    #ifdef DEBUG
    printf("Fin de la réception des messages du pair\n");
    #endif

    return NULL;
}

// Ouvrir les pipes de communication avec Python
void open_pipes(char *py_to_c_name, char *c_to_py_name) {
    // Ouvrir les pipes
    if ((py_to_c = open(py_to_c_name, O_RDONLY)) < 0) {
        perror("Erreur lors de l'ouverture du pipe de Python vers C");
        exit(EXIT_FAILURE);
    }

    if ((c_to_py = open(c_to_py_name, O_WRONLY)) < 0) {
        perror("Erreur lors de l'ouverture du pipe de C vers Python");
        exit(EXIT_FAILURE);
    }

    #ifdef DEBUG
    printf("Pipes ouverts pour la communication entre Python et C\n");
    #endif
}

// Créer un socket pour agir en tant que serveur
int create_server_socket(char *port) {
    struct sockaddr_in server_addr;
    int server_sockfd;

    // Créer un socket pour agir en tant que serveur
    if ((server_sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
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

    if (listen(server_sockfd, 1) < 0) {
        perror("Erreur lors de l'écoute sur le socket serveur");
        exit(EXIT_FAILURE);
    }

    #ifdef DEBUG
    printf("Socket serveur créé et en attente de connexion\n");
    #endif

    return server_sockfd;
}

// Créer un socket pour agir en tant que client
int create_client_socket(char *ip, char *port) {
    struct sockaddr_in client_addr;
    int client_sockfd;

    // Créer un socket pour agir en tant que client
    if ((client_sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Erreur lors de la création du socket client");
        exit(EXIT_FAILURE);
    }

    client_addr.sin_family = AF_INET;
    client_addr.sin_port = htons(atoi(port));  // Se connecter au port du pair
    client_addr.sin_addr.s_addr = inet_addr(ip);  // Se connecter à l'adresse IP du pair

    // Essayer de se connecter à l'autre pair
    if (connect(client_sockfd, (struct sockaddr *)&client_addr, sizeof(client_addr)) < 0) {
        perror("Erreur lors de la connexion au pair");
        exit(EXIT_FAILURE);
    }

    #ifdef DEBUG
    printf("Connexion établie avec le pair\n");
    #endif

    return client_sockfd;
}

// Accepter la connexion entrante de l'autre pair
int accept_incoming_connection(int server_sockfd) {
    int new_sockfd;

    // Accepter la connexion entrante de l'autre pair
    if ((new_sockfd = accept(server_sockfd, NULL, NULL)) < 0) {
        perror("Erreur lors de l'acceptation de la connexion entrante");
        exit(EXIT_FAILURE);
    }

    #ifdef DEBUG
    printf("Connexion entrante acceptée\n");
    #endif

    return new_sockfd;
}

// Lire les messages entrants de Python et les envoyer au pair
void read_and_send_messages(int client_sockfd) {
    char message[MAX_LENGTH];

    // Boucle infinie pour lire les messages entrants de Python et les envoyer au pair
    while (1) {
        // Lire une ligne depuis le pipe de Python vers C
        if (read(py_to_c, message, MAX_LENGTH) > 0) {
            // Envoyer le message au pair
            send(client_sockfd, message, strlen(message), 0);
        }
    }

    memset(message, '\0', MAX_LENGTH);

    #ifdef DEBUG
    printf("Fin de la lecture des messages de Python vers C\n");
    #endif
}