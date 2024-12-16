from constraint import *
import sys

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
        self.variables = []
        for f in range(self.franjas):
            for avion in self.aviones:
                variable = (avion, f)
                self.problema.addVariable(variable, self.SPC+self.PRK+self.STD)
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
        total_SPC = 0
        for variable in variables:
            if variable[1] == "SPC":
                total_SPC += 1
        return total_SPC
    
    def ordenar_tareas(self, variables, restr, tareas_std, tareas_spc):
        if restr == "F":
            return True
        for variable in variables:
            if tareas_spc > 0:
                if variable[1] == "SPC":
                    tareas_spc -= 1
            elif tareas_std > 0:
                if variable[1] == "STD":
                    tareas_std -= 1
        return (tareas_spc + tareas_std == 0)

    def funcion_huecos_vacios(self, *res):
        # Res es el valor de restriccion, que es una lista con un puntero y el valor de las variables
        for i, valor in enumerate(res):
            print(i, valor, res[i-1], res[i])
            if valor in self.PRK + self.STD + self.SPC:
                #comprobación en los talleres y parking en horizontal
                if (i > 0 and res[i-1] in self.PRK + self.STD + self.SPC) or (i < len(res)-1 and res[i+1] in self.PRK + self.STD + self.SPC):
                    print('ok', res[i-1])
                    return False

                #comprobación en los talleres y parking en vertical    
                '''''fila_actual = int(valor[0][0])
                columna_actual = int(valor[0][1])
                if (fila_actual > 0 and any(res[j][0][0] == str(fila_actual - 1) and res[j][0][1] == columna_actual for j in range(len(res)))) or \
                (fila_actual < self.dimensiones[0] - 1 and any(res[j][0][0] == str(fila_actual + 1) and res[j][0][1] == columna_actual for j in range(len(res)))):
                    return False'''
        return True


    def add_restrictions(self):
        variables_por_franja = []
        for franja in range(self.franjas):
            variables_por_franja.append([])
        for variable in self.variables:
            variables_por_franja[variable[1]].append(variable)

        # No puede haber más de dos aviones en un taller, ni dos JMB en el mismo
        for franja in variables_por_franja:
            aviones_JMB = []
            self.problema.addConstraint(self.hasta_dos_aviones_en_taller, franja)
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
        

        #Los talleres y parkings con aviones asignados en una franja horaria deben tener 
        # vacíos al menos uno de los parkings o talleres de los adyacente vertical u horizontalmente
        # for franja in variables_por_franja:
        #     self.problema.addConstraint(self.funcion_huecos_vacios, franja)
        ''' 
        for avion1 in self.aviones:
            for avion2 in self.aviones:
                for avion3 in self.aviones:
                    problema.addConstraint(lambda a, b, c: laterales(a, b, c, dimensiones), (avion1, avion2, avion3))
        
        

        '''

        # No puede haber dos talleres adyacentes con avión JMB
        # for franja in variables_por_franja:
        #     aviones_JMB = []
        #     for variable in franja:
        #         if variable[0][1] == "JMB":
        #             aviones_JMB.append(variable)
        #     self.problema.addConstraint(lambda a,b: )

    def realizar_problema(self):
        self.add_variables()
        self.add_restrictions()
        return self.problema.getSolution()

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
    csp = CSP(franjas, dimensiones, STD, SPC, PRK, aviones)
    solucion = csp.realizar_problema()
    for llave in solucion:
        print(llave, solucion[llave])

if __name__ == "__main__":
    main()