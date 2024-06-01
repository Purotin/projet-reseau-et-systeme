#ifndef PEER_COMMUNICATION_H
#define PEER_COMMUNICATION_H

#include <arpa/inet.h>
#include <fcntl.h>
#include <sys/socket.h>

#define MAX_LENGTH 1024

/**
 * Ouvre les pipes de communication avec Python.
 * @param py_to_c_name Le nom du pipe de Python vers C.
 * @param c_to_py_name Le nom du pipe de C vers Python.
 * @param py_to_c_fd Le descripteur de fichier du pipe de Python vers C.
 * @param c_to_py_fd Le descripteur de fichier du pipe de C vers Python.
 */
void open_pipes(char *py_to_c_name, char *c_to_py_name, int *py_to_c_fd, int *c_to_py_fd);

/**
 * Crée un socket pour agir en tant que serveur multicast.
 * @param multicast_ip L'adresse IP multicast du groupe.
 * @param port Le port sur lequel le serveur doit écouter.
 * @return Le descripteur de fichier du socket serveur.
 */
int create_server_socket(char *multicast_ip, char *port);

/**
 * Crée un socket pour agir en tant que client multicast.
 * @param multicast_ip L'adresse IP multicast du groupe.
 * @param port Le port du pair à connecter.
 * @param peer_addr L'adresse du pair.
 * @param peer_addr_len La longueur de l'adresse du pair.
 * @return Le descripteur de fichier du socket client.
 */
int create_client_socket(char *multicast_ip, char *port, struct sockaddr_in *peer_addr, socklen_t *peer_addr_len);

/**
 * Gère la communication entre les pipes et les sockets.
 * @param py_to_c Le descripteur de fichier du pipe de Python vers C.
 * @param c_to_py Le descripteur de fichier du pipe de C vers Python.
 * @param client_sockfd Le descripteur de fichier du socket client.
 * @param peer_addr L'adresse du pair.
 * @param peer_addr_len La longueur de l'adresse du pair.
 * @param sockfd Le descripteur de fichier du socket serveur.
 */
void handle_communication(int py_to_c, int c_to_py, int client_sockfd, struct sockaddr_in *peer_addr, socklen_t peer_addr_len, int sockfd);


#endif // PEER_COMMUNICATION_H
