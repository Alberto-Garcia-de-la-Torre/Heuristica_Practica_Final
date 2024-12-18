import sys
import copy
import time
import random


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
    archivo.write("Makespan: "+str(len(movimientos[0])-1))
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
        archivo.write("\n\nMovimiento: "+str(movimiento)+"/"+str(len(movimientos[0])-1))
        archivo.close()
        time.sleep(0.5)

class ASTAR:
    def __init__(self, heuristica, inicio, final, posiciones_prohibidas, posicion_repetida, configuraciones, matriz, matriz_costes):
        self.heuristica = heuristica
        self.inicio = inicio
        self.final = final
        self.posiciones_prohibidas = posiciones_prohibidas
        self.posicion_repetida = posicion_repetida
        self.configuraciones = configuraciones
        self.matriz_original = matriz
        self.matriz_costes = matriz_costes
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
        nodos = self._calcular_costes(futuras_posiciones, matriz, coste)
        return matriz, nodos + len(futuras_posiciones)

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
        nodos = 0
        if len(futuras_posiciones) > 0:
            nodos = self._calcular_costes(futuras_posiciones, matriz, coste)
        return nodos + len(futuras_posiciones)
    
    def utilizar_heruristica(self, matriz: list):
        menor_coste = float('inf')
        ganador = None
        # if self.final == [0,5]:
        #     print("--------------------------")
        #     print(self.inicio)
        # Escoger heuristica
        if self.heuristica == 1:
            # Comprobar si se ha repetido la posición
            if self.posicion_repetida:
                posiciones = self.adyacentes(self.inicio) + [self.inicio]
                posiciones_filtradas = []
                for pos in posiciones:
                    if self.in_matriz(pos) and self.matriz_original[pos[0]][pos[1]] != "G" and pos not in self.posiciones_prohibidas:
                        posiciones_filtradas.append(pos)
                return posiciones_filtradas[random.randint(0, len(posiciones_filtradas)-1)]
            for ady in self.adyacentes(self.inicio):
                if self.in_matriz(ady):
                    coste = matriz[ady[0]][ady[1]]
                    if coste != "GG" and int(coste) < menor_coste and ady not in self.posiciones_prohibidas:
                        ganador = ady
                        menor_coste = coste
            # Estimar si la posición actual es mejor que las adyacentes
            coste = matriz[self.inicio[0]][self.inicio[1]]
            if int(coste) < menor_coste:
                ganador = self.inicio
                menor_coste = coste
        elif self.heuristica == 2:
            for ady in self.adyacentes(self.inicio) + [self.inicio]:
                if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "GG":
                    coste = matriz[ady[0]][ady[1]] + self.matriz_costes[ady[0]][ady[1]]
                    # if self.final == [0,5] and ady not in self.posiciones_prohibidas:
                    #     print(self.matriz_costes[ady[0]][ady[1]])
                    #     print(str(ady)+": "+str(matriz[ady[0]][ady[1]])+" + "+str(self.matriz_costes[ady[0]][ady[1]])+" = "+str(coste))
                    if int(coste) < menor_coste and ady not in self.posiciones_prohibidas:
                        ganador = ady
                        menor_coste = coste
        return ganador
    
    def ejecutar_algoritmo(self):
        # Calcular matriz g
        matriz_g, nodos_g = self.calcular_costes(self.inicio)
        # Calcular matriz h
        matriz_h, nodos_h = self.calcular_costes(self.final)
        # Calcular matriz f
        matriz_f = []
        for fila in range(self.dimensiones[0]):
            matriz_f.append([])
            for columna in range(self.dimensiones[1]):
                matriz_f[fila].append(matriz_g[fila][columna] + matriz_h[fila][columna])
        # Escoger futura posicion
        ganador = self.utilizar_heruristica(matriz_f)
        return ganador, nodos_g + nodos_h


def realizar_problema(aviones, matriz, heuristica):
    movimientos = []
    for avion in range(len(aviones)):
        movimientos.append([aviones[avion][0]])
    posiciones_actuales = []
    for avion in range(len(aviones)):
        posiciones_actuales.append(aviones[avion][0])
    posiciones_finales = []
    for avion in range(len(aviones)):
        posiciones_finales.append(aviones[avion][1])
    posiciones_anteriores = copy.deepcopy(posiciones_actuales)
    configuraciones = [] # Comprobar si se repite la misma posición dos veces
    posicion_repetida = False
    matriz_costes = []
    for avion in range(len(aviones)):
        matriz_costes.append([])
        for linea in range(len(matriz)):
            matriz_costes[avion].append([])
            for columna in range(len(matriz[linea])):
                matriz_costes[avion][linea].append(0)
    total_nodos = 0

    while posiciones_actuales != posiciones_finales:
    # for x in range(20):
        copia_anteriores = copy.deepcopy(posiciones_anteriores)
        copia_actuales = copy.deepcopy(posiciones_actuales)
        nuevos = [] # Evitar que dos aviones se muevan a la misma posición
        configuraciones.append([])
        for avion in range(len(aviones)):
            posiciones_anteriores[avion] = posiciones_actuales[avion]
            if posiciones_actuales[avion] != posiciones_finales[avion]:
                posiciones_prohibidas = copia_anteriores[:avion] + copia_anteriores[avion+1:] + copia_actuales[:avion] + copia_actuales[avion+1:] + nuevos
                astar = ASTAR(heuristica, posiciones_actuales[avion], posiciones_finales[avion], posiciones_prohibidas, posicion_repetida, configuraciones, matriz, matriz_costes[avion])
                siguiente_movimiento, nodos = astar.ejecutar_algoritmo()
                # Actualizar posiciones
                movimientos[avion].append(siguiente_movimiento)
                posiciones_actuales[avion] = siguiente_movimiento
                nuevos.append(siguiente_movimiento)
                configuraciones[-1].append([copia_actuales[avion], siguiente_movimiento])
                matriz_costes[avion][copia_actuales[avion][0]][copia_actuales[avion][1]] += 3
                total_nodos += nodos
            else:
                # Si ya ha llegado a la casilla final, esperar en el sitio
                movimientos[avion].append(movimientos[avion][-1])
        if configuraciones[-1] in configuraciones[:-1]:
            posicion_repetida = True
        else:
            posicion_repetida = False
    print(total_nodos)
    return movimientos

        

def main():
    aviones, matriz = leer_archivo(sys.argv[1])
    tiempo = time.time()
    movimientos = realizar_problema(aviones, matriz, int(sys.argv[2]))
    escribir_archivo(sys.argv[3], movimientos, matriz, time.time()-tiempo)

if __name__ == "__main__":
    main()