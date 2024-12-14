from constraint import *
import sys
import csv
    
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

def addvariables(aviones, STD, SPC, PRK, franjas):
    problema = Problem()
    variables = []
    for f in range(franjas):
        for avion in aviones:
            problema.addVariable((avion, f), PRK+STD+SPC)
            variables.append((avion, f))
    return problema, variables

def restricciones(problema: Constraint, variables, franjas):
    # No puede haber más de dos aviones en un taller
    aviones_franja = []
    for i in range(franjas):
        aviones_franja.append([])
    for variable in variables:
        aviones_franja[variable[1]].append(variable)
    for franja in aviones_franja:
        for avion in franja:










    for f in range(franjas):
        # Para cada tipo de taller (STD, SPC, PRK)
        for taller in STD + SPC + PRK:
            # Crear una lista de variables que representan aviones en esa franja y taller
            aviones_en_taller = []
            for variable in variables:
                avion, franja = variable
                if franja == f and taller in problema.getDomain(variable):  # Verificar si el taller está en el dominio
                    aviones_en_taller.append(variable)

            # Añadir la restricción de que no pueden haber más de 2 aviones en el mismo taller en la misma franja
            if len(aviones_en_taller) > 2:
                # Por ejemplo, puedes agregar una restricción que garantice que no se asignen más de 2 aviones en el taller
                problema.addConstraint(lambda *asignaciones: len(set(asignaciones)) <= 2, aviones_en_taller)















    # Evitar que dos Jumbos estén en el mismo taller
    for variable in variables:
        for otra_variable in variables:
            if variable != otra_variable and variable[1] == otra_variable[1] and variable[0][1] == "JMB" and otra_variable[0][1] == "JMB":
                problema.addConstraint(lambda a,b: a!=b, (variable, otra_variable))

def realizar_problema(path):
    franjas, dimensiones, STD, SPC, PRK, aviones = leer_archivo(path)
    problema, variables = addvariables(aviones, STD, SPC, PRK, franjas)
    restricciones(problema, variables, franjas)
    soluciones = problema.getSolution()
    print(soluciones)


def main():
    realizar_problema(sys.argv[1])

if __name__ == "__main__":
    main()