import os
import select
class PipeHandler:
    def __init__(self):
        # Création des pipes si nécessaire
        if not os.path.exists("py_to_c"):
            os.mkfifo("py_to_c")
        if not os.path.exists("c_to_py"):
            os.mkfifo("c_to_py")

        try:
            self.pipe_py_to_c = open("py_to_c", 'w')
        except OSError as e:
            print("Erreur lors de l'ouverture du pipe py_to_c: ", e)

        try:
            self.pipe_c_to_py = open("c_to_py", 'r')
        except OSError as e:
            print("Erreur lors de l'ouverture du pipe c_to_py: ", e)

    def send(self, data):
        if self.pipe_py_to_c and self.pipe_py_to_c in select.select([], [self.pipe_py_to_c], [], 0)[1]:
            print(data, file=self.pipe_py_to_c)
            self.pipe_py_to_c.flush()

    def recv(self):
        if self.pipe_c_to_py and self.pipe_c_to_py in select.select([self.pipe_c_to_py], [], [], 0)[0]:
            return self.pipe_c_to_py.readline().strip()
        return ""
        
    def close(self):
        if self.pipe_py_to_c:
            self.pipe_py_to_c.close()
        if self.pipe_c_to_py:
            self.pipe_c_to_py.close()