from typing import List, Optional

from config import MAX_PROCESOS_MEMORIA, TIEMPO_BLOQUEO
from models.process import Estado, Process
from utils.data_generator import evaluate_operation, generate_random_process


class SimulatorEngine:
    """Motor de la simulacion: planificador a largo plazo (Nuevos -> Listos) y a corto
    plazo con Round-Robin. No conoce nada de la interfaz grafica."""

    def __init__(self, total_jobs: int, quantum: int):
        self.global_clock: int = 0
        self.is_paused: bool = False
        self.quantum: int = quantum

        # Total de procesos creados (lote inicial + los generados con la tecla N)
        self.total_generated: int = total_jobs

        # Colas de los 5 estados
        self.new_queue: List[Process] = []
        self.ready_queue: List[Process] = []
        self.blocked_queue: List[Process] = []
        self.terminated_queue: List[Process] = []
        self.running_process: Optional[Process] = None

        for i in range(1, total_jobs + 1):
            self.new_queue.append(generate_random_process(i))
        self._admit_new_processes()
        self._dispatch()

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def get_memory_count(self) -> int:
        """Procesos actualmente en memoria (Listos + Bloqueados + Ejecucion)."""
        return len(self.ready_queue) + len(self.blocked_queue) + (1 if self.running_process else 0)

    def get_all_processes(self) -> List[Process]:
        """Todos los procesos del sistema (cualquier estado), ordenados por ID."""
        procesos = (self.new_queue + self.ready_queue + self.blocked_queue
                    + self.terminated_queue)
        if self.running_process:
            procesos.append(self.running_process)
        return sorted(procesos, key=lambda p: p.id)

    def is_finished(self) -> bool:
        return (not self.running_process and not self.ready_queue
                and not self.blocked_queue and not self.new_queue)

    @property
    def progress_percent(self) -> int:
        total = self.total_generated or 1
        return int(len(self.terminated_queue) / total * 100)

    # ------------------------------------------------------------------
    # Planificador a largo plazo
    # ------------------------------------------------------------------
    def _admit_new_processes(self) -> None:
        """Nuevos -> Listos mientras haya cupo en memoria."""
        while self.get_memory_count() < MAX_PROCESOS_MEMORIA and self.new_queue:
            process = self.new_queue.pop(0)
            process.status = Estado.LISTO
            process.arrival_time = self.global_clock
            self.ready_queue.append(process)

    def request_new_process(self) -> None:
        """Tecla N: crea un proceso aleatorio en Nuevos; el planificador a largo plazo
        decide si entra de inmediato o espera a que se libere memoria."""
        self.total_generated += 1
        self.new_queue.append(generate_random_process(self.total_generated))
        self._admit_new_processes()
        self._dispatch()

    # ------------------------------------------------------------------
    # Planificador a corto plazo: Round-Robin
    # ------------------------------------------------------------------
    def _dispatch(self) -> None:
        """Si el procesador esta libre, toma el primero de la cola de listos (carrusel)."""
        if self.running_process is None and self.ready_queue:
            proc = self.ready_queue.pop(0)
            proc.status = Estado.EJECUCION
            proc.quantum_elapsed = 0
            if proc.response_time is None:
                proc.response_time = self.global_clock - proc.arrival_time
            self.running_process = proc

    def tick(self) -> bool:
        """Avanza una unidad de tiempo. Regresa False cuando la simulacion termino."""
        if self.is_paused:
            return True

        self._admit_new_processes()
        self._dispatch()
        if self.is_finished():
            return False

        self.global_clock += 1
        self._advance_blocked()
        self._run_cpu()

        # El procesador nunca queda ocioso si hay procesos listos
        self._admit_new_processes()
        self._dispatch()
        return True

    def _advance_blocked(self) -> None:
        """Suma una unidad a cada bloqueado y regresa a Listos los que cumplen su tiempo."""
        for p in self.blocked_queue:
            p.blocked_time += 1
        liberados = [p for p in self.blocked_queue if p.blocked_time >= TIEMPO_BLOQUEO]
        for p in liberados:
            self.blocked_queue.remove(p)
            p.status = Estado.LISTO
            p.blocked_time = 0
            self.ready_queue.append(p)

    def _run_cpu(self) -> None:
        """Ejecuta una unidad del proceso actual. Si termina, sale como Terminado (tiene
        prioridad sobre el fin de quantum); si agota el quantum, va al final de Listos."""
        rp = self.running_process
        if not rp:
            return
        rp.time_elapsed += 1
        rp.quantum_elapsed += 1
        if rp.time_elapsed >= rp.tme:
            self._finish_current_process(with_error=False)
        elif rp.quantum_elapsed >= self.quantum:
            rp.status = Estado.LISTO
            rp.quantum_elapsed = 0
            self.ready_queue.append(rp)
            self.running_process = None

    def _finish_current_process(self, with_error: bool = False) -> None:
        rp = self.running_process
        if not rp:
            return
        rp.finish_time = self.global_clock
        rp.status = Estado.TERMINADO
        rp.quantum_elapsed = 0
        rp.result = "ERROR" if with_error else evaluate_operation(rp.operation)
        self.terminated_queue.append(rp)
        self.running_process = None
        # Al liberar memoria, el planificador a largo plazo admite uno nuevo
        self._admit_new_processes()

    # ------------------------------------------------------------------
    # Acciones de teclado
    # ------------------------------------------------------------------
    def handle_interrupt_io(self) -> None:
        """Interrupcion de E/S: el proceso en ejecucion pasa a Bloqueados (conserva su
        lugar en memoria) y el procesador se asigna al siguiente de la cola de listos."""
        rp = self.running_process
        if rp:
            rp.status = Estado.BLOQUEADO
            rp.blocked_time = 0
            rp.quantum_elapsed = 0
            self.blocked_queue.append(rp)
            self.running_process = None
            self._dispatch()

    def handle_error(self) -> None:
        """Error: el proceso en ejecucion termina con ERROR, libera memoria y el
        procesador pasa al siguiente."""
        if self.running_process:
            self._finish_current_process(with_error=True)
            self._dispatch()

    def pause(self) -> None:
        self.is_paused = True

    def resume(self) -> None:
        self.is_paused = False
