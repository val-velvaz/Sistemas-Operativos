"""Constantes del Programa 6: Productor-Consumidor."""

CAPACIDAD = 18                 # Casillas del contenedor (buffer circular acotado)
MIN_ELEMENTOS = 3              # Elementos minimos por entrada al contenedor
MAX_ELEMENTOS = 6              # Elementos maximos por entrada al contenedor
SUENO_MIN = 3                  # Unidades de tiempo minimas dormido
SUENO_MAX = 10                 # Unidades de tiempo maximas dormido
INTERVALO_MS = 600             # Duracion real de una unidad de tiempo (ms)

# Productos posibles: letras, numeros y caracteres especiales
PRODUCTOS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "0123456789"
             "#$%&*+?!@=<>")

MAX_MENSAJES = 200             # Mensajes que se conservan en la bitacora
