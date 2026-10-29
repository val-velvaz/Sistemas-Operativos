from typing import List, Optional

from config import CAPACIDAD


class CircularBuffer:
    """Contenedor circular y acotado. Las casillas se numeran 0..CAPACIDAD-1
    internamente y 1..CAPACIDAD en pantalla."""

    def __init__(self, capacidad: int = CAPACIDAD):
        self.capacidad = capacidad
        self.casillas: List[Optional[str]] = [None] * capacidad
        self.entrada = 0      # siguiente casilla donde produce el productor
        self.salida = 0       # siguiente casilla de donde consume el consumidor
        self.ocupadas = 0

    @property
    def lleno(self) -> bool:
        return self.ocupadas == self.capacidad

    @property
    def vacio(self) -> bool:
        return self.ocupadas == 0

    @property
    def libres(self) -> int:
        return self.capacidad - self.ocupadas

    def poner(self, elemento: str) -> int:
        """Coloca un elemento en la casilla 'entrada' y avanza en circulo.
        Regresa el indice usado."""
        if self.lleno:
            raise RuntimeError("El contenedor esta lleno")
        i = self.entrada
        self.casillas[i] = elemento
        self.entrada = (i + 1) % self.capacidad
        self.ocupadas += 1
        return i

    def quitar(self):
        """Retira el elemento de la casilla 'salida' y avanza en circulo.
        Regresa (indice, elemento)."""
        if self.vacio:
            raise RuntimeError("El contenedor esta vacio")
        i = self.salida
        elemento = self.casillas[i]
        self.casillas[i] = None
        self.salida = (i + 1) % self.capacidad
        self.ocupadas -= 1
        return i, elemento
