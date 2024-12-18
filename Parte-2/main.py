import sys
import copy
import time


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

def escribir_archivo(path, movimientos, matriz, tiempo):
    archivo = open(path, "w")
    archivo.write("Tiempo total: "+str(tiempo//1000)+"s\n")
    archivo.write("Makespan: "+str(len(movimientos)))
    for movimiento in range(len(movimientos[0])):
        output = []
        



        for linea in range(len(matriz)):
            output.append([])
            for columna in range(len(matriz[0])):
                valor = matriz[linea][columna]
                if valor == "G":
                    valor = "X"
                elif valor == "B":
                    valor = "-"
                elif valor == "A":
                    valor = "+"
                output[linea].append(valor)
        for x in range(len(movimientos)):
            output[movimientos[x][movimiento][0]][movimientos[x][movimiento][1]] = str(x)
        archivo = open("animacion_"+path, "w")
        for linea in output:
            archivo.write("\n")
            for valor in linea:
                archivo.write(valor+",")
        archivo.write("\n\nMovimiento: "+str(movimiento))
        time.sleep(0.5)

class ASTAR:
    def __init__(self, inicio, final, posiciones_prohibidas, matriz):
        self.inicio = inicio
        self.final = final
        self.posiciones_prohibidas = posiciones_prohibidas
        self.matriz_original = matriz
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
    
    def calcular_costes(self, inicio):
        # -------------------------------------------------------------------------------- Cambiar para cuando acepte casillas amarillas
        matriz = self.resetear_matriz(copy.deepcopy(self.matriz_original))
        # Resetear valor inicial
        matriz[inicio[0]][inicio[1]] = 0
        # Calcular adyacentes
        coste = 0
        futuras_posiciones = []
        for ady in self.adyacentes(inicio):
            if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G":
                futuras_posiciones.append(ady)
        self._calcular_costes(futuras_posiciones, matriz, coste)
        return matriz

    
    def _calcular_costes(self, posiciones, matriz, coste):
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
            self._calcular_costes(futuras_posiciones, matriz, coste)
    
    def ejecutar_algoritmo(self):
        # Calcular matriz g
        matriz_g = self.calcular_costes(self.inicio)
        # Calcular matriz h
        matriz_h = self.calcular_costes(self.final)
        # Calcular matriz f
        matriz_f = []
        for fila in range(self.dimensiones[0]):
            matriz_f.append([])
            for columna in range(self.dimensiones[1]):
                matriz_f[fila].append(matriz_g[fila][columna] + matriz_h[fila][columna])
                # matriz_f[fila][columna] = matriz_f[fila][columna][0]
        menor_coste = float('inf')
        ganador = None
        print(matriz_f)
        # Escoger futura posicion
        for ady in self.adyacentes(self.inicio):
            if self.in_matriz(ady):
                coste = matriz_f[ady[0]][ady[1]]
                if coste != "GG" and int(coste) < menor_coste and ady not in self.posiciones_prohibidas:
                    ganador = ady
                    menor_coste = coste
        # Estimar si la posición actual es mejor que las adyacentes
        coste = matriz_f[self.inicio[0]][self.inicio[1]]
        if int(coste) < menor_coste:
            ganador = self.inicio
            menor_coste = coste
        print("Ganador: ", menor_coste, ganador)
        print("Objetivo:", matriz_f[self.inicio[0]][self.inicio[1]])
        return ganador


def realizar_problema(aviones, matriz):
    movimientos = []
    for i in range(len(aviones)):
        movimientos.append([aviones[i][0]])
    posiciones_actuales = []
    for i in range(len(aviones)):
        posiciones_actuales.append(aviones[i][0])
    posiciones_finales = []
    for i in range(len(aviones)):
        posiciones_finales.append(aviones[i][1])
    posiciones_anteriores = copy.deepcopy(posiciones_actuales)

    # while posiciones_actuales != posiciones_finales:
    for x in range(10):
        copia_anteriores = copy.deepcopy(posiciones_anteriores)
        copia_actuales = copy.deepcopy(posiciones_actuales)
        nuevos = [] # Evitar que dos aviones se muevan a la misma posición
        for i in range(len(aviones)):
            posiciones_anteriores[i] = posiciones_actuales[i]
            if posiciones_actuales[i] != posiciones_finales[i]:
                posiciones_prohibidas = copia_anteriores[:i] + copia_anteriores[i+1:] + copia_actuales[:i] + copia_actuales[i+1:] + nuevos
                print("Posiciones prohibidas:", posiciones_prohibidas)
                astar = ASTAR(posiciones_actuales[i], posiciones_finales[i], posiciones_prohibidas,  matriz)
                siguiente_movimiento = astar.ejecutar_algoritmo()
                movimientos[i].append(siguiente_movimiento)
                posiciones_actuales[i] = siguiente_movimiento
                nuevos.append(siguiente_movimiento)
            else:
                # Si ya ha llegado a la casilla final, esperar en el sitio
                movimientos[i].append(movimientos[i][-1])
        print("Anteriores:           ", posiciones_anteriores)
        print("Actuales:             ", posiciones_actuales)
    return movimientos

        

def main():
    aviones, matriz = leer_archivo(sys.argv[1])
    tiempo = time.time()
    movimientos = realizar_problema(aviones, matriz)
    escribir_archivo(sys.argv[2], movimientos, matriz, time.time()-tiempo)

if __name__ == "__main__":
    main()