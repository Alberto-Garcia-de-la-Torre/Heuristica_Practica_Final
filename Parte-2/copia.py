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

def escribir_archivo(path, movimientos, nodos, matriz, tiempo):
    archivo = open(path, "w")
    archivo.write("Tiempo total: "+str(tiempo//1000)+"s")
    archivo.write("\nMakespan: "+str(len(movimientos[0])-1))
    archivo.write("\nNodos: "+str(nodos))
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
        archivo = open("animacion_"+path, "w")
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
        for linea in range(len(matriz)):
            for columna in range(len(matriz[0])):
                if matriz[linea][columna] == "G":
                    self.obstaculos.append((linea, columna))
                elif matriz[linea][columna] == "A":
                    self.casillas_amarillas.append((linea, columna))
        self.dimensiones = [len(matriz), len(matriz[0])]
        # Crear matriz heurística por cada avión
        # ---------------------------------------------------------------------------- Cambiarlo para cuando implemente dos heurísticas distintas ------------------------
        self.nodos_abiertos = []
        self.nodos_cerrados = [[]]
        for pos in inicio:
            self.nodos_cerrados[0].append((tuple(pos), tuple(pos)))
        self.nodos_cerrados[0] = tuple(self.nodos_cerrados[0])
        self.configuraciones = copy.deepcopy(self.nodos_cerrados)
        self.camino = [tuple(inicio)]
        self.camino_optimo = []
        self.prof_max = 1000
        self.caminos_anteriores = []
    
    def resetear_variables(self):
        self.caminos_anteriores.append(copy.deepcopy(self.camino_optimo))
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
    
    def generar_matriz_h(self, nodo_actual, pos_inicial, pos_final):
        matriz = self.resetear_matriz(copy.deepcopy(self.matriz_original))
        otros_aviones = []
        for avion in nodo_actual:
            if avion != pos_inicial:
                otros_aviones.append(avion)
        # Resetear valor inicial
        matriz[pos_final[0]][pos_final[1]] = 0
        # Calcular adyacentes
        coste = 0
        futuras_posiciones = []
        for ady in self.adyacentes(pos_final):
            if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G":
                futuras_posiciones.append(ady)
        self._generar_matriz_h(futuras_posiciones, matriz, coste, otros_aviones)
        return matriz
    
    def _generar_matriz_h(self, posiciones, matriz, coste, otros_aviones):
        coste += 1
        futuras_posiciones = []
        for pos in posiciones:
            # Cambiar valor actual de las posiciones
            # if pos in otros_aviones:
            #     coste += 1000
            matriz[pos[0]][pos[1]] = coste
            # Calcular futuras posiciones
            for ady in self.adyacentes(pos):
                if self.in_matriz(ady) and matriz[ady[0]][ady[1]] != "G" and ady not in futuras_posiciones and coste < matriz[ady[0]][ady[1]]:
                    futuras_posiciones.append(ady)
        if len(futuras_posiciones) > 0:
            self._generar_matriz_h(futuras_posiciones, matriz, coste, otros_aviones)

    def calcular_coste(self, nodo):
        # ----------------------------------------- El coste solo es calculado con la heuristica, es posible tener que añadir la matriz g ------------------------------------------------------------------
        coste = 0
        for pos in range(len(nodo)):
            matriz_h = self.generar_matriz_h(nodo, nodo[pos], self.nodo_final[pos])
            coste += matriz_h[nodo[pos][0]][nodo[pos][1]]
        return coste
    
    def realizar_iteracion(self)->int:
        profundidad = 0
        menor_coste = float('inf')
        while menor_coste != 0 and profundidad < self.prof_max:
            # Abrir nuevos nodos
            self.nodos_abiertos = self.buscar_nodos(self.pos_actual)
            # Ver cuál es el nodo con menor coste
            menor_coste = float('inf')
            nodo_ganador = None
            for nodo in self.nodos_abiertos:
                pos = nodo[1]
                coste_nodo = self.calcular_coste(pos)
                if coste_nodo < menor_coste and nodo not in self.nodos_cerrados:
                    menor_coste = coste_nodo
                    nodo_ganador = tuple(nodo)
                    self.pos_actual = tuple(pos)
            if nodo_ganador:
                self.camino.append(self.pos_actual)
                # Comprobar si este camino ya se ha recorrido
                if self.camino in self.caminos_anteriores:
                    self.camino.pop()
                    profundidad -= 1
                else:
                    self.configuraciones.append(nodo_ganador)
                    profundidad += 1
                self.nodos_cerrados.append(nodo_ganador)
            if not nodo_ganador:
                # profundidad -= 1
                # self.camino.pop()
                if len(self.camino) == 0:
                    return -1
                self.pos_actual = self.camino[-1]
                self.configuraciones.pop()
                nodo_ganador = self.configuraciones[-1]
        # print("Camino:")
        # for movimiento in self.camino:
        #     print(movimiento)
        # print("Nodos abiertos:")
        # for nodo in self.nodos_abiertos:
        #     print(nodo)
        # print("Nodos cerrados:")
        # for nodo in self.nodos_cerrados:
        #     print(nodo)
        return 0
    
    def ejecutar_algoritmo(self):
        # contador = 0
        # while True:
            res = self.realizar_iteracion()
            self.camino_optimo = copy.deepcopy(self.camino)
            self.prof_max = len(self.camino_optimo)
            self.resetear_variables()
            # contador += 1
            # if res:
            #     return self.camino_optimo
            return self.camino_optimo
        


def realizar_problema(aviones, matriz, heuristica):
        inicio = []
        final = []
        for avion in aviones:
            inicio.append(avion[0])
            final.append(avion[1])
        astar = ASTAR(heuristica, inicio, final, matriz)
        camino = astar.ejecutar_algoritmo()

        return camino,0
    

        

def main():
    aviones, matriz = leer_archivo(sys.argv[1])
    tiempo = time.time()
    movimientos, nodos = realizar_problema(aviones, matriz, int(sys.argv[2]))
    escribir_archivo(sys.argv[3], movimientos, nodos, matriz, time.time()-tiempo)

if __name__ == "__main__":
    main()