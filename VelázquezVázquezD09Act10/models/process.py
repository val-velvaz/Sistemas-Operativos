from dataclasses import dataclass
from typing import Optional

from config import TIEMPO_BLOQUEO


class Estado:
    """Los 5 estados del modelo de procesos."""
    NUEVO = "Nuevo"
    LISTO = "Listo"
    EJECUCION = "Ejecucion"
    BLOQUEADO = "Bloqueado"
    TERMINADO = "Terminado"


@dataclass
class Process:
    """Bloque de Control de Proceso (BCP)."""
    id: int
    operation: str
    tme: int
    time_elapsed: int = 0
    result: Optional[str] = None
    status: str = Estado.NUEVO

    # Tiempos de planificacion
    arrival_time: Optional[int] = None
    finish_time: Optional[int] = None
    response_time: Optional[int] = None

    # Tiempo transcurrido en la cola de bloqueados
    blocked_time: int = 0

    # Tiempo transcurrido del quantum actual (Round-Robin)
    quantum_elapsed: int = 0

    # ---- Propiedades derivadas ------------------------------------------
    @property
    def time_remaining(self) -> int:
        return self.tme - self.time_elapsed

    @property
    def blocked_remaining(self) -> int:
        """Tiempo que le falta al proceso en la cola de bloqueados."""
        return TIEMPO_BLOQUEO - self.blocked_time

    @property
    def return_time(self) -> Optional[int]:
        if self.finish_time is not None and self.arrival_time is not None:
            return self.finish_time - self.arrival_time
        return None

    @property
    def service_time(self) -> int:
        # El tiempo de servicio es el tiempo que el proceso estuvo ejecutandose
        return self.time_elapsed

    @property
    def waiting_time(self) -> Optional[int]:
        """Tiempo de espera final (retorno - servicio). None si aun no termina."""
        if self.return_time is not None:
            return self.return_time - self.service_time
        return None

    def waiting_time_at(self, reloj: int) -> Optional[int]:
        """Tiempo de espera 'al momento': None si aun no llega al sistema, el valor
        final si ya termino, o (reloj - llegada) - servicio si sigue en el sistema."""
        if self.arrival_time is None:
            return None
        if self.finish_time is not None:
            return self.waiting_time
        return (reloj - self.arrival_time) - self.service_time

    @property
    def final_status(self) -> str:
        return "Error" if self.result == "ERROR" else "Normal"
