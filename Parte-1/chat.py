from constraint import Problem

# Definimos los parámetros
num_franjas_horarias = 5  # Número de franjas horarias
talleres = {
    "STD": [(0, 1), (1, 0), (1, 2), (2, 1)],  # Talleres estándar (coordenadas)
    "SPC": [(0, 2), (2, 0), (4, 3)],          # Talleres especialistas (coordenadas)
    "PRK": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]  # Parkings (coordenadas)
}
aviones = ["STD1", "STD2", "JMB1", "JMB2"]  # Identificadores de aviones

# Crear problema
problem = Problem()

# Variables: cada avión debe tener una posición asignada para cada franja horaria
for avion in aviones:
    for franja in range(num_franjas_horarias):
        problem.addVariable((avion, franja), talleres["STD"] + talleres["SPC"] + talleres["PRK"])

# Restricción 1: Cada avión debe ocupar un único taller o parking por franja horaria
# (implícita en la definición de variables)

# Restricción 2: Cada taller puede atender hasta 2 aviones por franja horaria,
# pero máximo un avión JUMBO en el mismo taller
for franja in range(num_franjas_horarias):
    for taller in talleres["STD"] + talleres["SPC"]:
        def taller_restriccion(*asignaciones):
            asignados = [avion for avion, pos in zip(aviones, asignaciones) if pos == taller]
            jumbos = [avion for avion in asignados if avion.startswith("JMB")]
            return len(asignados) <= 2 and len(jumbos) <= 1

        problem.addConstraint(taller_restriccion, [(avion, franja) for avion in aviones])

# Restricción 3: Taller especialista requerido para tareas de tipo 2 (JUMBOS)
def especialista_requerido(*asignaciones):
    for avion, pos in zip(aviones, asignaciones):
        if avion.startswith("JMB") and pos in talleres["STD"]:
            return False
    return True

for franja in range(num_franjas_horarias):
    problem.addConstraint(especialista_requerido, [(avion, franja) for avion in aviones])

# Restricción 4: Orden de tareas (tipo 2 antes de tipo 1 para JUMBOS)
def orden_tareas(asignaciones_previas, asignaciones_actuales):
    for avion, pos_actual, pos_previa in zip(aviones, asignaciones_actuales, asignaciones_previas):
        if avion.startswith("JMB") and pos_actual in talleres["STD"] and pos_previa in talleres["SPC"]:
            return True
        elif avion.startswith("JMB") and pos_actual in talleres["STD"]:
            return False
    return True

for franja in range(1, num_franjas_horarias):
    problem.addConstraint(orden_tareas, [(avion, franja - 1) for avion in aviones] + [(avion, franja) for avion in aviones])

# Restricción 5: Adyacencia vacía
movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
def adyacencia_vacia(*asignaciones):
    posiciones = set(asignaciones)
    for pos in posiciones:
        if pos in talleres["PRK"] + talleres["STD"] + talleres["SPC"]:
            adyacentes = [(pos[0] + dx, pos[1] + dy) for dx, dy in movimientos]
            if any(ady in posiciones for ady in adyacentes):
                return False
    return True

for franja in range(num_franjas_horarias):
    problem.addConstraint(adyacencia_vacia, [(avion, franja) for avion in aviones])

# Restricción 6: Aviones JUMBO no pueden estar en talleres adyacentes
def no_jumbo_adyacentes(*asignaciones):
    posiciones = [(avion, pos) for avion, pos in zip(aviones, asignaciones) if avion.startswith("JMB")]
    for i, (avion1, pos1) in enumerate(posiciones):
        for avion2, pos2 in posiciones[i + 1:]:
            if abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1:
                return False
    return True

for franja in range(num_franjas_horarias):
    problem.addConstraint(no_jumbo_adyacentes, [(avion, franja) for avion in aviones])

# Resolver el problema
soluciones = problem.getSolutions()

# Mostrar soluciones
print(f"Se encontraron {len(soluciones)} soluciones:")
for solucion in soluciones:
    print(solucion)
