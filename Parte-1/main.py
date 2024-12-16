from constraint import *
import sys
import csv

class CSP:
    def __init__(self, franjas, dimensiones, STD, SPC, PRK, aviones):
        self.franjas = franjas
        self.dimensiones = dimensiones
        self.STD = STD
        self.SPC = SPC
        self.PRK = PRK
        self.aviones = aviones
        self.problema = Problem()

    def addvariables(self):
        self.variables = []
        for f in range(self.franjas):
            for avion in self.aviones:
                variable = (avion, f)
                self.problema.addVariable(variable, self.PRK+self.STD+self.SPC)
                self.variables.append(variable)

    def no_dos_JMB_en_taller(*res):
        # Res es el valor de restriccion, que es una lista con tres valores: puntero, valor de variable1, valor de variable2
        if res[1][1] != "PRK" and res[2][1] != "PRK":
            if res[1] == res[2]:
                return False
        return True

    def restricciones(self):
        variables_por_franja = []
        for franja in range(self.franjas):
            variables_por_franja.append([])
        for variable in self.variables:
            variables_por_franja[variable[1]].append(variable)
        # No puede haber más de dos aviones en un taller
        for franja in variables_por_franja:
            aviones_JMB = []
            for variable in franja:
                if variable[0][1] == "JMB":
                    aviones_JMB.append(variable)
            self.problema.addConstraint(self.no_dos_JMB_en_taller, aviones_JMB)

    def realizar_problema(self):
        self.addvariables()
        self.restricciones()
        soluciones = self.problema.getSolution()
        print(soluciones)

def leer_archivo(path):
    archivo = open(path, 'r')
    filas = []
    for fila in archivo:
        filas.append(fila)
    franjas = int(filas[0][-2])
    dimensiones = [int(filas[1][0]), int(filas[1][2])]
    STD = []
    filas_STD = filas[2][4:]
    for i in range(len(filas_STD)//6):
        STD.append(((int(filas_STD[i*6+1]), int(filas_STD[i*6+3])), "STD"))
    SPC = []
    fila_SPC = filas[3][4:]
    for i in range(len(fila_SPC)//6):
        SPC.append(((int(fila_SPC[i*6+1]), int(fila_SPC[i*6+3])), "SPC"))
    PRK = []
    fila_PRK = filas[4][4:]
    for i in range(len(fila_PRK)//6):
        PRK.append(((int(fila_PRK[i*6+1]), int(fila_PRK[i*6+3])), "PRK"))
    aviones = []
    filas_aviones = filas[5:]
    for fila in filas_aviones:
        aviones.append((int(fila[0]), str(fila[2:5]), str(fila[6]), int(fila[8]), int(fila[10])))
    return franjas, dimensiones, STD, SPC, PRK, aviones

def main():
    franjas, dimensiones, STD, SPC, PRK, aviones = leer_archivo(sys.argv[1])
    print(STD+SPC+PRK)
    csp = CSP(franjas, dimensiones, STD, SPC, PRK, aviones)
    csp.realizar_problema()

if __name__ == "__main__":
    main()