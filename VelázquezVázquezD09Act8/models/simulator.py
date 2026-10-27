from typing import List, Optional
from models.process import Process
from utils.data_generator import generate_random_process

class SimulatorEngine:
    def __init__(self, total_jobs: int):
        self.global_clock: int = 0
        self.is_paused: bool = False

        # Contador total de procesos creados (lote inicial + los generados con la tecla "N")
        self.total_generated: int = total_jobs

        # Estructuras de colas (5 Estados)
        self.new_queue: List[Process] = []
        self.ready_queue: List[Process] = []
        self.blocked_queue: List[Process] = []
        self.terminated_queue: List[Process] = []
        self.running_process: Optional[Process] = None

        # Generar todos los procesos inicialmente en la cola de Nuevos
        for i in range(1, total_jobs + 1):
            self.new_queue.append(generate_random_process(i))

        self._admit_new_processes()

    def get_memory_count(self) -> int:
        """Calcula cuantos procesos hay actualmente en memoria (Listos + Bloqueados + Ejecucion)"""
        return len(self.ready_queue) + len(self.blocked_queue) + (1 if self.running_process else 0)

    def _admit_new_processes(self) -> None:
        """Admite procesos de la cola de Nuevos a Listos hasta llenar la memoria (max 5)"""
        while self.get_memory_count() < 5 and self.new_queue:
            process = self.new_queue.pop(0)
            process.status = "Listo"
            process.arrival_time = self.global_clock
            self.ready_queue.append(process)

    def request_new_process(self) -> None:
        """Tecla N: crea un proceso con datos aleatorios y lo agrega a la cola de Nuevos.
        El planificador a largo plazo (_admit_new_processes) decide si ingresa de inmediato
        a memoria (si hay cupo, respetando el maximo de 5 procesos) o si debe esperar en
        la cola de Nuevos hasta que se libere espacio."""
        self.total_generated += 1
        nuevo_proceso = generate_random_process(self.total_generated)
        self.new_queue.append(nuevo_proceso)
        self._admit_new_processes()

    def tick(self) -> bool:
        if self.is_paused:
            return True

        # 1. Asignar proceso al procesador si esta libre (FCFS)
        if not self.running_process:
            if self.ready_queue:
                self.running_process = self.ready_queue.pop(0)
                self.running_process.status = "Ejecucion"
                # Si es la primera vez que entra al procesador, calcular tiempo de respuesta
                if self.running_process.response_time is None:
                    self.running_process.response_time = self.global_clock - self.running_process.arrival_time
            elif not self.blocked_queue and not self.new_queue:
                # No hay procesos listos, ni bloqueados, ni nuevos: FIN
                return False

        # 2. Avanzar Reloj Global
        self.global_clock += 1

        # 3. Procesar cola de Bloqueados
        unblocked_this_tick = []
        for p in self.blocked_queue:
            p.blocked_time += 1
            if p.blocked_time == 8: # Tiempo estricto en E/S
                unblocked_this_tick.append(p)

        for p in unblocked_this_tick:
            self.blocked_queue.remove(p)
            p.status = "Listo"
            p.blocked_time = 0
            self.ready_queue.append(p)

        # 4. Procesar el trabajo en Ejecucion
        if self.running_process:
            self.running_process.time_elapsed += 1
            if self.running_process.time_elapsed >= self.running_process.tme:
                self._finish_current_process(with_error=False)

        return True

    def _finish_current_process(self, with_error: bool = False) -> None:
        if not self.running_process:
            return

        self.running_process.finish_time = self.global_clock
        self.running_process.status = "Terminado"

        if with_error:
            self.running_process.result = "ERROR"
        else:
            try:
                res = eval(self.running_process.operation)
                self.running_process.result = str(round(res, 4))
            except Exception:
                self.running_process.result = "ERROR"

        self.terminated_queue.append(self.running_process)
        self.running_process = None

        # Al liberar memoria, intentamos admitir un nuevo proceso
        self._admit_new_processes()

    def handle_interrupt_io(self) -> None:
        """Tecla E: Pasa a Bloqueados (No libera memoria, sigue dentro de los 5 maximos)"""
        if self.running_process:
            self.running_process.status = "Bloqueado"
            self.running_process.blocked_time = 0
            self.blocked_queue.append(self.running_process)
            self.running_process = None

    def handle_error(self) -> None:
        """Tecla W: Termina por error y libera memoria"""
        if self.running_process:
            self._finish_current_process(with_error=True)

    def pause(self) -> None:
        self.is_paused = True

    def resume(self) -> None:
        self.is_paused = False