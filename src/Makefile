# Variables
CC = gcc
CFLAGS = -Wall -Wextra
TARGET = tmp/network_manager
OBJS = tmp/network_manager.o tmp/peer_communication.o

# Règle par défaut
all: $(TARGET)

# Règle pour l'édition de liens
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

# Règle pour la compilation
tmp/network_manager.o: network/network_manager.c network/peer_communication.h
	$(CC) $(CFLAGS) -c network/network_manager.c -o tmp/network_manager.o

tmp/peer_communication.o: network/peer_communication.c network/peer_communication.h
	$(CC) $(CFLAGS) -c network/peer_communication.c -o tmp/peer_communication.o

# Règle pour nettoyer les fichiers objets, l'exécutable et les pipes
clean:
	rm -f tmp/*