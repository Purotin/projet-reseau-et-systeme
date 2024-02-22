import os
import sys
import select

def main():

    # Vérifier si le nombre d'arguments est correct
    if len(sys.argv) != 3:
        print("Usage: python3 message_handler.py <py_to_c_NAME> <c_to_py_NAME>")
        sys.exit(1)

    # Noms des pipes
    py_to_c = sys.argv[1]
    c_to_py = sys.argv[2]

    # Ouvrir les pipes
    py_to_c = open(py_to_c, 'w')
    c_to_py = open(c_to_py, 'r')

    print("Python message handler")
    print("Entrez un message: ", end="\n")
    while True:
        # Utiliser select pour vérifier si nous pouvons lire du c_to_py ou écrire dans py_to_c
        readables, writables, _ = select.select([c_to_py, sys.stdin], [py_to_c], [])

        # Si nous pouvons lire du c_to_py, afficher le message
        if c_to_py in readables:
            message = c_to_py.readline().strip()
            if message:
                print("Message reçu: ", message)

        # Si nous pouvons écrire dans py_to_c, demander à l'utilisateur d'entrer un message
        if py_to_c in writables:
            message = sys.stdin.readline().strip()
            print(message + '\n', file=py_to_c, end='')
            py_to_c.flush()
            print("Entrez un message: ", end="\n")


if __name__ == "__main__":
    main()