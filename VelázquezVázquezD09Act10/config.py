"""Constantes de configuracion del simulador (Programa 5, Round-Robin).

Todos los "numeros magicos" del programa viven aqui para poder ajustarlos
sin tocar la logica del motor ni de la interfaz.
"""

# --- Reglas de la simulacion ---------------------------------------------
MAX_PROCESOS_MEMORIA = 5      # Maximo de procesos en memoria (Listos + Ejecucion + Bloqueados)
TIEMPO_BLOQUEO = 8            # Unidades de tiempo que un proceso permanece en Bloqueados
INTERVALO_RELOJ_MS = 1000     # Duracion real de una unidad de tiempo (ms)

# --- Generacion aleatoria de procesos ------------------------------------
TME_MIN = 5
TME_MAX = 20
OPERANDO_MIN = 1
OPERANDO_MAX = 100
OPERADORES = ("+", "-", "*", "/", "%")

# --- Configuracion inicial -----------------------------------------------
PROCESOS_INICIALES_DEFECTO = 10
PROCESOS_INICIALES_MAX = 100
QUANTUM_DEFECTO = 4
QUANTUM_MIN = 1
QUANTUM_MAX = 100

# --- Teclas (tecla -> descripcion mostrada en la barra estilo vim) ------
# Segun el enunciado en PDF: E = interrupcion de E/S y W = error. Si tu profesora usa
# otra asignacion (por ejemplo I para E/S y E para error) basta con cambiarla aqui.
TECLA_IO = "E"
TECLA_ERROR = "W"
TECLA_PAUSA = "P"
TECLA_CONTINUAR = "C"
TECLA_NUEVO = "N"
TECLA_BCP = "B"

TECLAS_VALIDAS = {
    TECLA_IO: "Interrupcion E/S",
    TECLA_ERROR: "Error",
    TECLA_PAUSA: "Pausa",
    TECLA_CONTINUAR: "Continuar",
    TECLA_NUEVO: "Nuevo proceso",
    TECLA_BCP: "Tabla de procesos (BCP)",
}
