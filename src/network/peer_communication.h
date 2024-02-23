#ifndef PEER_COMMUNICATION_H
#define PEER_COMMUNICATION_H

#include <pthread.h>
#include <netinet/in.h>

#define MAX_LENGTH 1024

/**
 * Fonction pour recevoir des messages d'un socket et les écrire dans un pipe.
 * @param socket Le socket à partir duquel lire les messages.
 * @return NULL
 */
void *receive_messages(void *socket, struct sockaddr_in *client_addr, socklen_t addr_len);
/**
 * Ouvre les pipes pour la communication entre Python et C.
 * @param py_to_c_name Le nom du pipe de Python vers C.
 * @param c_to_py_name Le nom du pipe de C vers Python.
 */
void open_pipes(char *py_to_c_name, char *c_to_py_name);

/**
 * Crée un socket pour agir en tant que serveur.
 * @param port Le port sur lequel le serveur doit écouter.
 * @return Le descripteur de fichier du socket serveur.
 */
int create_server_socket(char *port);

/**
 * Crée un socket pour agir en tant que client.
 * @param ip L'adresse IP du pair à connecter.
 * @param port Le port du pair à connecter.
 * @return Le descripteur de fichier du socket client.
 */
int create_client_socket(char *ip, char *port);

/**
 * Accepte une connexion entrante sur un socket serveur.
 * @param server_sockfd Le descripteur de fichier du socket serveur.
 * @return Le descripteur de fichier du nouveau socket pour la connexion acceptée.
 */

void read_and_send_messages(int client_sockfd, struct sockaddr_in *client_addr, socklen_t addr_len);

#endif