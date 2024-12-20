import sys
import copy
import time
import random
import itertools


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

def escribir_archivo(path, movimientos, nodos, h_inicial, matriz, tiempo, heuristica):
    inicio_path = path[:-4]
    archivo = open(inicio_path+"-"+heuristica+".output", "w")
    archivo = open(inicio_path+"-"+heuristica+".output", "a")
    aviones = []
    for avion in range(len(movimientos[0])):
        aviones.append([])
    for movimiento in movimientos:
        for pos in range(len(movimiento)):
            aviones[pos].append(movimiento[pos])
    for avion in aviones:
        pos_prev = []
        for pos in avion:
            if pos == avion[0]:
                pass
            elif pos_prev[0] - pos[0] == 1:
                archivo.write(" ↑ ")
            elif pos_prev[0] - pos[0] == -1:
                archivo.write(" ↓ ")
            elif pos_prev[1] - pos[1] == 1:
                archivo.write(" ← ")
            elif pos_prev[1] - pos[1] == -1:
                archivo.write(" → ")
            elif pos_prev[0] - pos[0] == 0 and pos_prev[1] - pos[1] == 0:
                archivo.write(" w ")
            archivo.write(str(tuple(pos)))
            pos_prev = pos
        archivo.write("\n")
    archivo.close()
    archivo = open(inicio_path+"-"+heuristica+".stat", "w")
    archivo.write("Tiempo total: "+str(tiempo//1000)+"s")
    archivo.write("\nMakespan: "+str(len(movimientos)-1))
    archivo.write("\nH inicial: "+str(h_inicial))
    archivo.write("\nNodos: "+str(nodos))
    archivo.close()
    for movimiento in range(len(movimientos)):
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
        for x in range(len(movimientos[movimiento])):
            output[movimientos[movimiento][x][0]][movimientos[movimiento][x][1]] = str(x)
        archivo = open("animacion", "w")
        for linea in output:
            archivo.write("\n")
            for valor in linea:
                archivo.write(valor+",")
        archivo.write("\n\nMovimiento: "+str(movimiento)+"/"+str(len(movimientos)-1))
        archivo.close()
        time.sleep(0.5)

class ASTAR:
    def __init__(self, heuristica, inicio, final, matriz):
        self.heuristica = heuristica
        self.pos_inicial = tuple(inicio)
        self.nodo_final = tuple(final)
        self.pos_actual = tuple(inicio)
        # Crear matriz y extraer valores de la matriz
        self.matriz_original = matriz
        self.obstaculos = []
        self.casillas_amarillas = []
        self.matrices = []
        for avion in range(len(inicio)):
            self.matrices.append([])
            for linea in range(len(matriz)):
                self.matrices[avion].append([])
                for columna in range(len(matriz[0])):
                    self.matrices[avion][linea].append(0)
        for linea in range(len(matriz)):
            for columna in range(len(matriz[0])):
                if matriz[linea][columna] == "G":
                    self.obstaculos.append((linea, columna))
                elif matriz[linea][columna] == "A":
                    self.casillas_amarillas.append((linea, columna))
        self.dimensiones = [len(matriz), len(matriz[0])]
        # Crear matriz heurística por cada avión
        self.nodos_abiertos = []
        self.nodos_cerrados = [[[], []]]
        for pos in inicio:
            self.nodos_cerrados[0][0].append(tuple(pos))
            self.nodos_cerrados[0][1].append(tuple(pos))
        self.nodos_cerrados[0] = tuple(self.nodos_cerrados[0])
        self.configuraciones = copy.deepcopy(self.nodos_cerrados)
        self.camino = [tuple(inicio)]
        self.camino_optimo = []
        self.prof_max = float('inf')
        self.caminos_anteriores = []
        self.nodos_prof_cerrados = [self.nodos_cerrados[0][0], self.nodos_cerrados[0][1], 1]
        self.nodos_camino = copy.deepcopy(self.nodos_cerrados)
        self.total_nodos = 0
        self.avion_actual = None
        self.h_inicial = None
    
    def resetear_variables(self):
        self.caminos_anteriores.append(copy.deepcopy(self.camino))
        self.pos_actual = copy.deepcopy(self.pos_inicial)
        self.nodos_abiertos = []
        self.nodos_cerrados = [[]]
        for pos in copy.deepcopy(self.pos_inicial):
            self.nodos_cerrados[0].append((tuple(pos), tuple(pos)))
        self.nodos_cerrados[0] = tuple(self.nodos_cerrados[0])
        self.configuraciones = copy.deepcopy(self.nodos_cerrados)
        self.camino = [tuple(copy.deepcopy(self.pos_inicial))]

    def resetear_matriz(self, matriz):
        for fila in range(len(matriz)):
            for valor in range(len(matriz[fila])):
                if matriz[fila][valor] != "G":
                    matriz[fila][valor] = float('inf')
        return matriz
    
    def adyacentes(self, pos):
        return [(pos[0], pos[1]-1), (pos[0], pos[1]+1), (pos[0]-1, pos[1]), (pos[0]+1, pos[1])]
    
    def casillas_posibles(self, pos):
        lista = self.adyacentes(pos)
        lista_filtrada = []
        for valor in range(len(lista)):
            if self.in_matriz(lista[valor]) and lista[valor] not in self.obstaculos and lista[valor] not in self.pos_actual[:valor]+self.pos_actual[valor:]:
                lista_filtrada.append(lista[valor])
        if pos not in self.casillas_amarillas:
            lista_filtrada.append(pos)
        return lista_filtrada
    
    def in_matriz(self, pos):
        return pos[0] < self.dimensiones[0] and pos[1] < self.dimensiones[1] and pos[0] >= 0 and pos[1] >= 0
    
    def buscar_nodos(self, posiciones):
        lista_nodos = []
        for pos in posiciones:
            lista_nodos.append(self.casillas_posibles(pos))
        total_nodos = [
            combinacion for combinacion in itertools.product(*lista_nodos)
            if len(set(map(tuple, combinacion))) == len(combinacion)
        ]
        # Añadir la posicion anterior
        for pos in range(len(total_nodos)):
            total_nodos[pos] = (self.pos_actual, total_nodos[pos])
        return total_nodos
    
    def aplicar_heuristica(self, pos):
        if self.heuristica == 1:
            pass
        elif self.heuristica == 2:
            return self.matrices[self.avion_actual][pos[0]][pos[1]]
        return 0
    
    def generar_matriz_h(self, pos_final):
        matriz = self.resetear_matriz(copy.deepcopy(self.matriz_original))
        # Resetear valor inicial
        matriz[pos_final[0]][pos_final[1]] = 0
        # Calcular adyacentes
        coste = 0
        futuras_posiciones = []
        for ady in self.adyacentes(pos_final):
            if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G":
                futuras_posiciones.append(ady)
        self._generar_matriz_h(futuras_posiciones, matriz, coste)
        return matriz
    
    def _generar_matriz_h(self, posiciones, matriz, coste):
        coste += 1
        futuras_posiciones = []
        for pos in posiciones:
            # Aplicar heuristica
            coste += self.aplicar_heuristica(pos)
            matriz[pos[0]][pos[1]] = coste
            # Calcular futuras posiciones
            for ady in self.adyacentes(pos):
                if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G" and ady not in futuras_posiciones and coste < matriz[ady[0]][ady[1]]:
                    futuras_posiciones.append(ady)
        if len(futuras_posiciones) > 0:
            self._generar_matriz_h(futuras_posiciones, matriz, coste)

    def calcular_coste(self, nodo):
        coste = 0
        for pos in range(len(nodo)):
            self.avion_actual = pos
            matriz_h = self.generar_matriz_h(self.nodo_final[pos])
            coste += matriz_h[nodo[pos][0]][nodo[pos][1]]
        return coste
    
    def ejecutar_algoritmo(self)->int:
        menor_coste = float('inf')
        while len(self.camino) > 0:
            # Comprobar que el camino nuevo puede ser mejor que el optimo
            if len(self.camino) < self.prof_max:
                # Abrir nuevos nodos
                self.nodos_abiertos = self.buscar_nodos(self.pos_actual)
                self.total_nodos += len(self.nodos_abiertos)
                # Ver cuál es el nodo con menor coste
                menor_coste = float('inf')
                nodo_ganador = None
                for nodo in self.nodos_abiertos:
                    pos = nodo[1]
                    coste_nodo = self.calcular_coste(pos)
                    nodo_evaluable = (nodo[0], nodo[1], len(self.camino)+1)
                    if coste_nodo < menor_coste and coste_nodo<self.prof_max and nodo_evaluable not in self.nodos_prof_cerrados and nodo not in self.nodos_camino:
                        menor_coste = coste_nodo
                        nodo_ganador = tuple(nodo)
                        self.pos_actual = tuple(pos)
                    else:
                        pass
                if nodo_ganador:
                    if self.h_inicial == None:
                        self.h_inicial = coste_nodo
                    self.camino.append(self.pos_actual)
                    self.nodos_camino.append(nodo_ganador)
                    self.configuraciones.append(nodo_ganador)
                    self.nodos_cerrados.append(nodo_ganador)
                    self.nodos_prof_cerrados.append((nodo_ganador[0], nodo_ganador[1], len(self.camino)))
                    for avion in range(len(self.pos_actual)):
                        self.matrices[avion][self.pos_actual[avion][0]][self.pos_actual[avion][1]] += 1
                if not nodo_ganador:
                    if len(self.camino) == 1:
                        return self.camino_optimo, self.total_nodos, self.h_inicial
                    self.camino.pop()
                    self.nodos_camino.pop()
                    self.pos_actual = copy.deepcopy(self.camino[-1])
                    self.configuraciones.pop()
                elif menor_coste == 0 and (len(self.camino) < len(self.camino_optimo) or len(self.camino_optimo) == 0):
                    self.camino_optimo = copy.deepcopy(self.camino)
                    self.prof_max = len(self.camino_optimo)-1
                    self.camino.pop()
                    self.nodos_camino.pop()
                    self.configuraciones.pop()
                    self.pos_actual = copy.deepcopy(self.camino[-1])
                    self.nodos_cerrados = [[]]
            else:
                self.camino.pop()
                self.nodos_camino.pop()
                self.configuraciones.pop()
                self.pos_actual = copy.deepcopy(self.camino[-1])
        return self.camino_optimo, self.total_nodos, self.h_inicial

def realizar_problema(aviones, matriz, heuristica):
        inicio = []
        final = []
        for avion in aviones:
            inicio.append(avion[0])
            final.append(avion[1])
        astar = ASTAR(heuristica, inicio, final, matriz)
        camino, nodos, h_inicial = astar.ejecutar_algoritmo()

        return camino, nodos, h_inicial

def main():
    aviones, matriz = leer_archivo(sys.argv[1])
    tiempo = time.time()
    movimientos, nodos, h_inicial = realizar_problema(aviones, matriz, int(sys.argv[2]))
    escribir_archivo(sys.argv[1], movimientos, nodos, h_inicial, matriz, time.time()-tiempo, str(sys.argv[2]))

if __name__ == "__main__":
    main()