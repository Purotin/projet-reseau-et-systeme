#include "peer_communication.h"
#include <stdio.h>

int main(int argc, char *argv[]) {
    int server_sockfd, client_sockfd, new_sockfd;

    // Vérifier si le nombre d'arguments est correct
    if (argc != 5) {
        fprintf(stderr, "Usage: %s <IP> <PORT> <py_to_c_NAME> <c_to_py_NAME>\n", argv[0]);
        return 1;  // Terminer le programme avec un code d'erreur
    }

    char *ip = argv[1];
    char *port = argv[2];
    char *py_to_c_name = argv[3];
    char *c_to_py_name = argv[4];

    // Ouvrir les pipes pour la communication entre Python et C
    open_pipes(py_to_c_name, c_to_py_name);

    // Créer un socket pour agir en tant que serveur
    server_sockfd = create_server_socket(port);

    // Créer un socket pour agir en tant que client
    client_sockfd = create_client_socket(ip, port);

    // Accepter une connexion entrante sur le socket serveur
    new_sockfd = accept_incoming_connection(server_sockfd);

    // Recevoir des messages du pair
    receive_messages(&new_sockfd);

    // Lire les messages du pipe de Python vers C et les envoyer au pair
    read_and_send_messages(client_sockfd);

    return 0;
}