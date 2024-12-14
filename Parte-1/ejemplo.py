from constraint import *
import csv
import sys
import random


def leer_archivo(path):
    with open(path, 'r', newline='') as archivo:
        archivo = csv.reader(archivo)
        valores = []
        for fila in archivo:
            valores.append(fila[0])

    dimensiones = [valores[0][0], valores[0][2]]
    plazas = []
    for fila in range(int(dimensiones[0])):
        # plazas.append([])
        fila_str = str(fila+1)+"."
        for columna in range(int(dimensiones[1])):
            # plazas[fila].append("-")
            plazas.append(fila_str+str(columna+1))

    pe = []
    for valor in range((len(valores[1])-3)//5):
        coordenada1 = int(valores[1][4+valor*5])
        coordenada2 = int(valores[1][6+valor*5])
        # plazas[coordenada1-1][coordenada2-1] = "pe"
        # pe.append([coordenada1, coordenada2])
        pe.append(str(coordenada1)+"."+str(coordenada2))

    ambulancias = []
    for fila in range(len(valores)-2):
        # tipo = valores[fila+2][2:5]
        # congelador = valores[fila+2][6]
        # ambulancias.append([tipo, congelador])
        ambulancias.append(valores[fila+2])

    return plazas, pe, ambulancias, dimensiones

def escribir_archivo(soluciones, dimensiones):
    # with open(lectura_parking + "_solucion.csv", newline='') as archivo:
    #     escritor = csv.writer(archivo, quotechar='"', quoting=csv.QUOTE_ALL, delimiter=',')
    
    # escritor.writerow([])

    datos = []
    datos.append(["'N. sol:'",len(soluciones)])
    if len(soluciones) > 0:
        for i in range(3):
            datos.append(["solucion "+str(i+1)+":"])
            if len(soluciones) > 1:
                sol1 = random.randint(1, len(soluciones)-1)
            else:
                sol1 = 0
            parking = []
            for fila in range(int(dimensiones[0])):
                parking.append([])
                for columna in range(int(dimensiones[1])):
                    parking[fila].append("'-'")
            for entrada in soluciones[sol1]:
                parking[int(soluciones[sol1][entrada][0])-1][int(soluciones[sol1][entrada][2])-1] = "'"+entrada+"'"
            for fila in parking:
                datos.append(fila)

    with open("csv/solucion.csv", mode='w', newline='') as archivo:
        # Create a CSV writer object
        csv_writer = csv.writer(archivo)
    
        # Write the data to the CSV file
        csv_writer.writerows(datos)

def addvariables(ambulancias, plazas, pe):
    problema = Problem()
    for ambulancia in ambulancias:
        if ambulancia[6] == "C":
            problema.addVariable(ambulancia, pe)
        else:
            problema.addVariable(ambulancia, plazas)
    return problema

def delante(ambulancia, otra_ambulancia):
    if ambulancia[0] == otra_ambulancia[0]:
        if ambulancia[2] > otra_ambulancia[2]:
            return True
        else:
            return False
    return True

def laterales(a, b, c, dimensiones):
    if int(b[0]) == int(a[0])-1 and b[2] == a[2] and int(c[0]) == int(a[0])+1 and c[2] == a[2]:
        return False
    if a[0] == "1" and int(c[0]) == int(a[0])+1 and c[2] == a[2]:
        return False
    if a[0] == str(dimensiones[0]) and int(b[0]) == int(a[0])-1 and b[2] == a[2]:
        return False
    return True

def restricciones(problema: Constraint, ambulancias, dimensiones):

    # Dos ambulancias no pueden ocupar una misma casilla
    for ambulancia in ambulancias:
        for otra_ambulancia in ambulancias:
            if ambulancia != otra_ambulancia:
                problema.addConstraint(lambda a,b: a != b, (ambulancia, otra_ambulancia))
    
    # Un TSU no puede tener delante a un TNU
    for ambulancia in ambulancias:
        if ambulancia[3] == "S":
            for otra_ambulancia in ambulancias:
                if otra_ambulancia[3] == "N":
                    problema.addConstraint(lambda a,b: delante(a,b), (ambulancia, otra_ambulancia))
    
    # Debe haber una plaza libre a izquierda o derecha
    for ambulancia1 in ambulancias:
        for ambulancia2 in ambulancias:
            for ambulancia3 in ambulancias:
                problema.addConstraint(lambda a, b, c: laterales(a, b, c, dimensiones), (ambulancia1, ambulancia2, ambulancia3))

def main():
    path = sys.argv[1]
    plazas, pe, ambulancias, dimensiones = leer_archivo(path)
    problema = addvariables(ambulancias, plazas, pe)
    restricciones(problema, ambulancias, dimensiones)
    soluciones = problema.getSolutions()
    escribir_archivo(soluciones, dimensiones)

main()


# python CSPParking.py csv/archivo.csv