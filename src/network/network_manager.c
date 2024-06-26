#include "peer_communication.h"
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

int main(int argc, char *argv[]) {
    int server_sockfd, client_sockfd;
    struct sockaddr_in peer_addr;
    socklen_t peer_addr_len = sizeof(peer_addr);

    // Vérifier si le nombre d'arguments est correct
    if (argc != 6) {
        fprintf(stderr, "Usage: %s <MULTICAST_IP> <PORT> <py_to_c_NAME> <c_to_py_NAME> <UUID_Player>\n", argv[0]);
        return 1;  // Terminer le programme avec un code d'erreur
    }

    char *multicast_ip = argv[1];
    char *port = argv[2];
    char *py_to_c_name = argv[3];
    char *c_to_py_name = argv[4];
    char *UUID_Player = argv[5];

    int py_to_c, c_to_py;
    // Ouvrir les pipes pour la communication entre Python et C
    open_pipes(py_to_c_name, c_to_py_name, &py_to_c, &c_to_py);

    // Créer un socket pour agir en tant que serveur multicast
    server_sockfd = create_server_socket(multicast_ip, port);

    // Créer un socket pour agir en tant que client multicast
    client_sockfd = create_client_socket(multicast_ip, port, &peer_addr, &peer_addr_len);

    // Gérer la communication entre les deux sockets
    handle_communication(py_to_c, c_to_py, client_sockfd, &peer_addr, peer_addr_len, server_sockfd, UUID_Player);

    return 0;
}
