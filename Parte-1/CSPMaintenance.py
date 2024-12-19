from constraint import *
import sys
import random

# La clase CSP es la encargada de realizar cualquier acción relacionada con Python Constraint
class CSP:
    def __init__(self, franjas, dimensiones, STD, SPC, PRK, aviones):
        self.franjas = franjas
        self.dimensiones = dimensiones
        self.STD = STD
        self.SPC = SPC
        self.PRK = PRK
        self.aviones = aviones
        self.problema = Problem()
        self.total = 0

    def add_variables(self):
        # Añade las variables de los aviones junto al dominio que tienen, el cual es toda la matriz
        self.variables = []
        for f in range(self.franjas):
            for avion in self.aviones:
                variable = (avion, f)
                self.problema.addVariable(variable, self.PRK+self.STD+self.SPC)
                self.variables.append(variable)

    def hasta_dos_aviones_en_taller(*res):
        # Comprobar que ningún taller atiende a más de dos aviones
        repeticiones = {}
        for valor in res[1:]:
            if valor not in repeticiones:
                repeticiones[valor] = 1
            else:
                repeticiones[valor] += 1
        for entrada in repeticiones:
            if repeticiones[entrada] > 2 and entrada[1] != "PRK":
                return False
        return True

    def no_dos_JMB_en_taller(*res):
        # Res es el valor de restriccion, que es una lista con tres valores: puntero, valor de variable1, valor de variable2
        if res[1][1] != "PRK" and res[2][1] != "PRK":
            if res[1] == res[2]:
                return False
        return True
    
    def contar_SPC(self, variables):
        # Cuenta el total de talleres SPC tiene asignado el avión
        total_SPC = 0
        for variable in variables:
            if variable[1] == "SPC":
                total_SPC += 1
        return total_SPC
    
    def ordenar_tareas(self, variables, restr, tareas_std, tareas_spc):
        # Asegura que haga primero las tareas SPC en caso de tenerlas
        if restr == "F":
            return True
        for variable in variables:
            if tareas_spc > 0:
                if variable[1] == "SPC":
                    tareas_spc -= 1
            # No comprueba las tareas STD si aún le quedan SPC
            elif tareas_std > 0:
                if variable[1] == "STD":
                    tareas_std -= 1
        return (tareas_spc + tareas_std == 0)

    def funcion_huecos_vacios(*res):
        #Guardamos todas las coordenadas ocupadas en una lista dentro de cada franja
        coordenadas_ocupadas = [(valor[0]) for valor in res[1:]]
        #Por cada epacio ocupado comprobamos los espacios adyacentes
        for fila, columna in coordenadas_ocupadas:
            adyacentes = [
                (fila - 1, columna), 
                (fila + 1, columna),  
                (fila, columna - 1), 
                (fila, columna + 1)  
            ]
            #Comprobamos que la menos un vecino no esté ocupado
            if not any((adyacente not in coordenadas_ocupadas) for adyacente in adyacentes):
                return False
        
        return True

    def no_JMB_adyacentes(self, variables):
        for variable in variables:
            if variable[1] != "PRK":
                for otra_variable in variables:
                    if otra_variable[1] != "PRK" and abs(variable[0][0]-otra_variable[0][0])+abs(variable[0][1]-otra_variable[0][1]) < 2:
                        return False
        return True

    def add_restrictions(self):
        # No hace falta hacer restricción para que cada variable tenga asignada un solo valor
        # Python Constraint ya asegura que cada variable tendrá en único valor

        # Lista para separar los aviones por la franja horaria a la que pertenecen
        variables_por_franja = []
        for franja in range(self.franjas):
            variables_por_franja.append([])
        for variable in self.variables:
            variables_por_franja[variable[1]].append(variable)

        # No puede haber más de dos aviones en un taller, ni dos JMB en el mismo
        for franja in variables_por_franja:
            self.problema.addConstraint(self.hasta_dos_aviones_en_taller, franja)
            aviones_JMB = []
            for variable in franja:
                if variable[0][1] == "JMB":
                    aviones_JMB.append(variable)
            self.problema.addConstraint(self.no_dos_JMB_en_taller, aviones_JMB)
        
        # Los aviones deben tener, como mínimo, un taller SPC por mantenimiento SPC
        for avion in self.aviones:
            mismo_avion = []
            for i in range(self.franjas):
                mismo_avion.append((avion, i))
            self.problema.addConstraint(lambda *args, spc_min=avion[4]: self.contar_SPC(args)>=spc_min, mismo_avion)
        
            # Las tareas especiales deben ejecutarse antes que las estándar
            self.problema.addConstraint(lambda *args, restr=avion[2], tareas_std=avion[3], tareas_spc=avion[4]: self.ordenar_tareas(args, restr, tareas_std, tareas_spc), mismo_avion)
        

        # Los talleres y parkings con aviones asignados en una franja horaria deben tener 
        # vacíos al menos uno de los parkings o talleres de los adyacente vertical u horizontalmente
        for franja in variables_por_franja:
             self.problema.addConstraint(self.funcion_huecos_vacios, franja)

        # No puede haber dos talleres adyacentes con avión JMB
        for franja in variables_por_franja:
            for variable in franja:
                if variable[0][1] == "JMB" and variable[1] != "PRK":
                    for otra_variable in franja:
                        if otra_variable[0][1] == "JMB" and otra_variable[1] != "PRK" and variable != otra_variable:
                            self.problema.addConstraint(lambda a,b: abs(a[0][0]-b[0][0])+abs(a[0][1]-b[0][1]) > 1, (variable, otra_variable))

    def realizar_problema(self):
        # Función para controlar el flujo de las acciones
        self.add_variables()
        self.add_restrictions()
        return self.problema.getSolutions()

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

def escribir_archivo(path, soluciones):
    archivo = open(path+".csv", "w")
    archivo.write("N. Sol: "+str(len(soluciones))+"\n")
    if len(soluciones) == 0:
        archivo.write("No se ha encontrado ninguna solución.")
        return 0
    for i in range(3):
        archivo.write("Solución "+str(i+1)+":")
        sol = random.randint(0, len(soluciones)-1)
        valores = {}
        for linea in soluciones[sol]:
            if linea[0] not in valores:
                valores[linea[0]] = [soluciones[sol][linea]]
            else:
                valores[linea[0]].insert(linea[1], soluciones[sol][linea])
        for valor in valores:
            archivo.write("\n\t")
            for subvalor in valor[:-1]:
                archivo.write(str(subvalor)+"-")
            archivo.write(str(valor[-1])+":")
            for res in valores[valor]:
                archivo.write(" "+res[1]+str(res[0]))
        archivo.write("\n")
    return 0

def main():
    path_entrada = sys.argv[1]
    # Leer el archivo de entrada
    franjas, dimensiones, STD, SPC, PRK, aviones = leer_archivo(path_entrada)
    # Definir la clase CSP y ejecutarla
    csp = CSP(franjas, dimensiones, STD, SPC, PRK, aviones)
    soluciones = csp.realizar_problema()
    # Escribir en el archivo de salida
    escribir_archivo(path_entrada, soluciones)

if __name__ == "__main__":
    main()