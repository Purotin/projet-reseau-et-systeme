#!/bin/bash

# Générer un identifiant unique
id=$(date +%s)

# Créer les pipes nommés s'ils n'existent pas déjà
py_to_c="tmp/py_to_c_$id"
c_to_py="tmp/c_to_py_$id"

[ ! -p $py_to_c ] && mkfifo $py_to_c
[ ! -p $c_to_py ] && mkfifo $c_to_py

# Lancer le programme C avec les noms des pipes en arguments
./tmp/network_manager 127.0.0.1 1234 $py_to_c $c_to_py &

# Enregistrer l'ID du processus
network_manager_pid=$!

# Lancer le script Python avec les noms des pipes en arguments
python3 message_handler.py $py_to_c $c_to_py

# Tuer le processus C
kill -9 $network_manager_pid