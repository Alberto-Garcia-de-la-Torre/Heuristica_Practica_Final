import sys


def leer_archivo(path):
    archivo = open(path, 'r')
    filas = []
    for fila in archivo:
        filas.append(fila)
    n_aviones = int(filas[0][0])
    aviones = []
    for avion in range(n_aviones):
        aviones.append([[int(filas[avion+1][1]), int(filas[avion+1][3])], [int(filas[avion+1][7]), int(filas[avion+1][9])]])
    matriz = []
    for linea in range(len(filas)-len(aviones)-1):
        matriz.append(filas[linea+len(aviones)+1].split(";"))
        matriz[-1][-1] = matriz[-1][-1][0] # Quitar \n
    return aviones, matriz

class ASTAR:
    def __init__(self, inicio, final, matriz):
        self.inicio = inicio
        self.final = final
        self.matriz_original = matriz
        self.g = matriz
        self.h = matriz
        self.f = matriz
        self.dimensiones = [len(matriz), len(matriz[0])]

    def resetear_matriz(self, matriz):
        for fila in range(len(matriz)):
            for valor in range(len(matriz[fila])):
                if matriz[fila][valor] != "G":
                    matriz[fila][valor] = float('inf')
        return matriz
    
    def adyacentes(self, pos):
        return [[pos[0], pos[1]-1], [pos[0], pos[1]+1], [pos[0]-1, pos[1]], [pos[0]+1, pos[1]]]
    
    def in_matriz(self, pos):
        return pos[0] < self.dimensiones[0] and pos[1] < self.dimensiones[1] and pos[0] >= 0 and pos[1] >= 0
    
    def calcular_valores(self, inicio, tipo):
        # -------------------------------------------------------------------------------- Cambiar para cuando acepte casillas amarillas
        # Escoger matriz a cambiar
        if tipo == "g":
            matriz = self.resetear_matriz(self.g)
        elif tipo == "h":
            matriz = self.resetear_matriz(self.h)
        elif tipo == "f":
            matriz = self.resetear_matriz(self.f)
        # Resetear valor inicial
        matriz[inicio[0]][inicio[1]] = 0
        # Calcular adyacentes
        coste = 0
        futuras_posiciones = []
        for ady in self.adyacentes(inicio):
            if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G":
                futuras_posiciones.append(ady)
        self._calcular_valores(futuras_posiciones, matriz, coste)

    
    def _calcular_valores(self, posiciones, matriz, coste):
        coste += 1
        futuras_posiciones = []
        for pos in posiciones:
            # Cambiar valor actual de las posiciones
            matriz[pos[0]][pos[1]] = coste
            # Calcular futuras posiciones
            for ady in self.adyacentes(pos):
                if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G" and ady not in futuras_posiciones and coste < matriz[ady[0]][ady[1]]:
                    futuras_posiciones.append(ady)
        if len(futuras_posiciones) > 0:
            self._calcular_valores(futuras_posiciones, matriz, coste)
    
    def ejecutar_algoritmo(self):
        # Calcular matriz g
        self.calcular_valores(self.inicio, "g")

def realizar_problema(aviones, matriz):
    for avion in aviones:
        algoritmo = ASTAR(avion[0], avion[1], matriz)
        algoritmo.ejecutar_algoritmo()

def main():
    aviones, matriz = leer_archivo(sys.argv[1])
    soluciones = realizar_problema(aviones, matriz)
    # escribir_archivo(sys.argv[2], soluciones)

if __name__ == "__main__":
    main()