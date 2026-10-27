from dataclasses import dataclass, field
from typing import List, Optional

# Tamano de pagina = tamano de marco (unidades de memoria)
FRAME_SIZE = 5


@dataclass
class Process:
    id: int
    operation: str
    tme: int
    size: int                      # Tamano del proceso (6 a 26)
    time_elapsed: int = 0
    result: Optional[str] = None
    status: str = "Nuevo"  # Nuevo, Listo, Ejecucion, Bloqueado, Terminado

    # Tiempos de planificacion
    arrival_time: Optional[int] = None
    finish_time: Optional[int] = None
    response_time: Optional[int] = None

    # Tiempo especifico para la cola de bloqueados
    blocked_time: int = 0

    # Tiempo transcurrido del quantum actual (Round-Robin)
    quantum_elapsed: int = 0

    # Tabla de paginas: frames[i] = numero de marco donde esta la pagina i
    frames: List[int] = field(default_factory=list)

    @property
    def num_pages(self) -> int:
        """Numero de paginas (marcos) que necesita el proceso."""
        return -(-self.size // FRAME_SIZE)  # division techo

    def page_usage(self, page: int) -> int:
        """Unidades realmente usadas de la pagina (la ultima puede ser menor a 5)."""
        return min(FRAME_SIZE, self.size - page * FRAME_SIZE)

    @property
    def time_remaining(self) -> int:
        return self.tme - self.time_elapsed

    @property
    def return_time(self) -> Optional[int]:
        if self.finish_time is not None and self.arrival_time is not None:
            return self.finish_time - self.arrival_time
        return None

    @property
    def service_time(self) -> int:
        # El tiempo de servicio siempre es el tiempo que estuvo ejecutandose
        return self.time_elapsed

    @property
    def waiting_time(self) -> Optional[int]:
        if self.return_time is not None:
            return self.return_time - self.service_time
        return None

    @property
    def final_status(self) -> str:
        return "Error" if self.result == "ERROR" else "Normal"
