"""Simulacion del problema Productor-Consumidor por unidades de tiempo.

Cada agente (productor o consumidor) pasa por los estados:

    DORMIDO --(se acaba su tiempo)--> INTENTANDO --(puede entrar)--> TRABAJANDO
       ^                                   |                              |
       +------(no puede entrar)------------+                              |
       +-------------(termina sus 3 a 6 elementos o ya no puede)----------+

Solo un agente puede estar dentro del contenedor a la vez (exclusion mutua),
el productor necesita espacio libre y el consumidor necesita producto.
"""
import random
from dataclasses import dataclass, field
from typing import List, Optional

from config import (MAX_ELEMENTOS, MAX_MENSAJES, MIN_ELEMENTOS, PRODUCTOS,
                    SUENO_MAX, SUENO_MIN)
from models.buffer import CircularBuffer


class Estado:
    DORMIDO = "Dormido"
    INTENTANDO = "Intentando entrar"
    TRABAJANDO = "Trabajando"


@dataclass
class Agente:
    nombre: str                       # "Productor" o "Consumidor"
    estado: str = Estado.DORMIDO
    sueno_restante: int = 0           # unidades que le faltan dormido
    por_procesar: int = 0             # elementos que le faltan en esta entrada
    procesados_entrada: int = 0       # elementos ya procesados en esta entrada
    total: int = 0                    # elementos producidos/consumidos en total
    detalle: str = ""                 # ultima accion, para mostrar en pantalla
    ultima_casilla: Optional[int] = None


@dataclass
class Mensaje:
    tiempo: int
    agente: str
    texto: str


class ProducerConsumer:
    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()
        self.buffer = CircularBuffer()
        self.reloj = 0
        self.dentro: Optional[str] = None     # agente que tiene el contenedor (mutex)
        self.productor = Agente("Productor")
        self.consumidor = Agente("Consumidor")
        self.mensajes: List[Mensaje] = []
        self.total_mensajes = 0                # mensajes generados desde el inicio
        for a in (self.productor, self.consumidor):
            self._dormir(a, "inicia dormido")

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _log(self, agente: str, texto: str):
        self.mensajes.append(Mensaje(self.reloj, agente, texto))
        self.total_mensajes += 1
        if len(self.mensajes) > MAX_MENSAJES:
            del self.mensajes[0]

    def _dormir(self, a: Agente, motivo: str):
        a.estado = Estado.DORMIDO
        a.sueno_restante = self.rng.randint(SUENO_MIN, SUENO_MAX)
        a.por_procesar = 0
        a.procesados_entrada = 0
        a.detalle = f"Dormido {a.sueno_restante} u.t. ({motivo})"
        self._log(a.nombre, f"se duerme {a.sueno_restante} u.t.: {motivo}")

    def _puede_entrar(self, a: Agente) -> Optional[str]:
        """None si puede entrar; si no, el motivo."""
        if self.dentro is not None and self.dentro != a.nombre:
            return f"el {self.dentro.lower()} esta dentro del contenedor"
        if a is self.productor and self.buffer.lleno:
            return "el contenedor esta lleno"
        if a is self.consumidor and self.buffer.vacio:
            return "el contenedor esta vacio"
        return None

    # ------------------------------------------------------------------
    # Ciclo
    # ------------------------------------------------------------------
    def tick(self):
        """Avanza una unidad de tiempo para ambos agentes."""
        self.reloj += 1
        # El orden se alterna para no favorecer siempre al mismo agente
        orden = [self.productor, self.consumidor]
        if self.reloj % 2 == 0:
            orden.reverse()
        for a in orden:
            self._avanzar(a)

    def _avanzar(self, a: Agente):
        if a.estado == Estado.DORMIDO:
            a.sueno_restante -= 1
            if a.sueno_restante <= 0:
                a.estado = Estado.INTENTANDO
                a.detalle = "Desperto e intenta entrar al contenedor"
                self._log(a.nombre, "despierta e intenta entrar al contenedor")
            else:
                a.detalle = f"Dormido, despierta en {a.sueno_restante} u.t."
            return

        if a.estado == Estado.INTENTANDO:
            motivo = self._puede_entrar(a)
            if motivo:
                self._log(a.nombre, f"no pudo entrar: {motivo}")
                self._dormir(a, f"no pudo entrar, {motivo}")
                return
            self.dentro = a.nombre
            a.estado = Estado.TRABAJANDO
            a.por_procesar = self.rng.randint(MIN_ELEMENTOS, MAX_ELEMENTOS)
            a.procesados_entrada = 0
            a.ultima_casilla = None
            verbo = "producir" if a is self.productor else "consumir"
            a.detalle = f"Entro al contenedor: va a {verbo} {a.por_procesar} elementos"
            self._log(a.nombre, f"entra al contenedor para {verbo} {a.por_procesar} elementos")
            return

        if a.estado == Estado.TRABAJANDO:
            self._trabajar(a)

    def _trabajar(self, a: Agente):
        """Procesa un elemento por unidad de tiempo."""
        if a is self.productor:
            if self.buffer.lleno:
                return self._salir(a, "el contenedor se lleno")
            elemento = self.rng.choice(PRODUCTOS)
            i = self.buffer.poner(elemento)
            a.detalle = f"Produjo '{elemento}' en la casilla {i + 1}"
            texto = f"produjo '{elemento}' en la casilla {i + 1}"
        else:
            if self.buffer.vacio:
                return self._salir(a, "el contenedor se vacio")
            i, elemento = self.buffer.quitar()
            a.detalle = f"Consumio '{elemento}' de la casilla {i + 1}"
            texto = f"consumio '{elemento}' de la casilla {i + 1}"
        a.ultima_casilla = i
        a.total += 1
        a.procesados_entrada += 1
        a.por_procesar -= 1
        self._log(a.nombre, texto)
        if a.por_procesar == 0:
            self._salir(a, f"termino sus {a.procesados_entrada} elementos")

    def _salir(self, a: Agente, motivo: str):
        self.dentro = None
        self._log(a.nombre, f"sale del contenedor ({motivo})")
        self._dormir(a, motivo)
