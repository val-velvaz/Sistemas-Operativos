from dataclasses import dataclass
from typing import Optional

@dataclass
class Process:
    id: int
    operation: str
    tme: int
    time_elapsed: int = 0
    result: Optional[str] = None
    status: str = "Nuevo" # Nuevo, Listo, Ejecucion, Bloqueado, Terminado

    # Tiempos de planificacion
    arrival_time: Optional[int] = None
    finish_time: Optional[int] = None
    response_time: Optional[int] = None

    # Tiempo especifico para la cola de bloqueados
    blocked_time: int = 0

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