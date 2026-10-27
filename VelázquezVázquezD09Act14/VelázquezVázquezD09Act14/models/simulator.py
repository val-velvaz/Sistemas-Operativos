from typing import List, Optional
from models.process import Process, FRAME_SIZE
from utils.data_generator import generate_random_process

MEMORIA_TOTAL = 230                          # Tamano de la memoria
TOTAL_MARCOS = MEMORIA_TOTAL // FRAME_SIZE   # 46 marcos de 5
MARCOS_SO = 5                                # Marcos ocupados por el S.O. (41 a 45)
MARCOS_DISPONIBLES = TOTAL_MARCOS - MARCOS_SO  # 41 marcos para procesos
TIEMPO_BLOQUEO = 6     # Tiempo fijo que un proceso permanece en la cola de Bloqueados


class SimulatorEngine:
    def __init__(self, total_jobs: int, quantum: int):
        self.global_clock: int = 0
        self.is_paused: bool = False
        self.quantum: int = quantum

        # Contador total de procesos creados (lote inicial + los generados con la tecla "N")
        self.total_generated: int = total_jobs

        # Estructuras de colas (5 Estados)
        self.new_queue: List[Process] = []
        self.ready_queue: List[Process] = []
        self.blocked_queue: List[Process] = []
        self.terminated_queue: List[Process] = []
        self.running_process: Optional[Process] = None

        # Memoria: frame_owner[f] = None (libre), "SO" o el ID del proceso dueno del marco
        self.frame_owner: list = [None] * MARCOS_DISPONIBLES + ["SO"] * MARCOS_SO

        # Generar todos los procesos inicialmente en la cola de Nuevos
        for i in range(1, total_jobs + 1):
            self.new_queue.append(generate_random_process(i))

        self._admit_new_processes()

    # ------------------------------------------------------------------
    # Planificador a largo plazo
    # ------------------------------------------------------------------
    def get_free_frames(self) -> List[int]:
        """Numeros de los marcos libres (ordenados)."""
        return [f for f, owner in enumerate(self.frame_owner) if owner is None]

    def get_memory_count(self) -> int:
        """Procesos actualmente en memoria (Listos + Bloqueados + Ejecucion)."""
        return len(self.ready_queue) + len(self.blocked_queue) + (1 if self.running_process else 0)

    def _admit_new_processes(self) -> None:
        """Paginacion simple: el siguiente proceso de Nuevos entra a Listos solo si hay
        marcos libres para TODAS sus paginas. Si no caben, espera (se respeta el orden
        de llegada y no se salta al siguiente)."""
        while self.new_queue:
            process = self.new_queue[0]
            libres = self.get_free_frames()
            if len(libres) < process.num_pages:
                break
            self.new_queue.pop(0)
            # Las paginas no tienen que ser contiguas: se toman los primeros marcos libres
            process.frames = libres[:process.num_pages]
            for f in process.frames:
                self.frame_owner[f] = process.id
            process.status = "Listo"
            process.arrival_time = self.global_clock
            self.ready_queue.append(process)

    def _release_frames(self, process: Process) -> None:
        """Libera los marcos del proceso (al terminar normal o por error)."""
        for f in process.frames:
            self.frame_owner[f] = None
        process.frames = []

    def _active_processes(self) -> List[Process]:
        activos = list(self.ready_queue) + list(self.blocked_queue)
        if self.running_process:
            activos.append(self.running_process)
        return sorted(activos, key=lambda p: p.id)

    def get_frame_table(self):
        """Por cada marco (0..45): (estado, id_proceso, unidades_usadas).
        estado: Libre, SO, Listo, Ejecucion o Bloqueado."""
        activos = {p.id: p for p in self._active_processes()}
        tabla = []
        for f, owner in enumerate(self.frame_owner):
            if owner is None:
                tabla.append(("Libre", None, 0))
            elif owner == "SO":
                tabla.append(("SO", None, FRAME_SIZE))
            else:
                p = activos[owner]
                tabla.append((p.status, p.id, p.page_usage(p.frames.index(f))))
        return tabla

    def get_page_tables(self):
        """Tabla de paginas de cada proceso en memoria: (id, tamano, estado, [(pagina, marco)])."""
        return [(p.id, p.size, p.status, list(enumerate(p.frames))) for p in self._active_processes()]

    def request_new_process(self) -> None:
        """Tecla N: crea un proceso con datos aleatorios en la cola de Nuevos; el
        planificador a largo plazo decide si entra de inmediato a memoria."""
        self.total_generated += 1
        self.new_queue.append(generate_random_process(self.total_generated))
        self._admit_new_processes()

    # ------------------------------------------------------------------
    # Planificador a corto plazo: Round-Robin
    # ------------------------------------------------------------------
    def _dispatch(self) -> None:
        """Si el procesador esta libre, toma el primero de la cola de listos."""
        if self.running_process is None and self.ready_queue:
            proc = self.ready_queue.pop(0)
            proc.status = "Ejecucion"
            proc.quantum_elapsed = 0
            if proc.response_time is None:
                proc.response_time = self.global_clock - proc.arrival_time
            self.running_process = proc

    def is_finished(self) -> bool:
        return (not self.running_process and not self.ready_queue
                and not self.blocked_queue and not self.new_queue)

    def tick(self) -> bool:
        """Avanza 1 unidad de tiempo. Regresa False cuando la simulacion termino."""
        if self.is_paused:
            return True

        # Asegurar que haya memoria libre y proceso en CPU si es posible
        self._admit_new_processes()
        self._dispatch()

        if self.is_finished():
            return False

        # 1. Avanzar reloj global
        self.global_clock += 1

        # 2. Cola de bloqueados (8 unidades de tiempo)
        desbloqueados = []
        for p in self.blocked_queue:
            p.blocked_time += 1
            if p.blocked_time >= TIEMPO_BLOQUEO:
                desbloqueados.append(p)
        for p in desbloqueados:
            self.blocked_queue.remove(p)
            p.status = "Listo"
            p.blocked_time = 0
            self.ready_queue.append(p)

        # 3. Proceso en ejecucion
        if self.running_process:
            rp = self.running_process
            rp.time_elapsed += 1
            rp.quantum_elapsed += 1

            if rp.time_elapsed >= rp.tme:
                # Termino normalmente (tiene prioridad sobre el fin de quantum)
                self._finish_current_process(with_error=False)
            elif rp.quantum_elapsed >= self.quantum:
                # Se agoto el quantum: vuelve al final de la cola de listos
                rp.status = "Listo"
                rp.quantum_elapsed = 0
                self.ready_queue.append(rp)
                self.running_process = None

        # 4. Dejar el procesador ocupado de inmediato (evita ticks "vacios")
        self._admit_new_processes()
        self._dispatch()

        return True

    def _finish_current_process(self, with_error: bool = False) -> None:
        if not self.running_process:
            return

        self.running_process.finish_time = self.global_clock
        self.running_process.status = "Terminado"
        self.running_process.quantum_elapsed = 0
        self._release_frames(self.running_process)

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

        # Al liberar memoria, el planificador a largo plazo admite uno nuevo
        self._admit_new_processes()

    # ------------------------------------------------------------------
    # Teclas
    # ------------------------------------------------------------------
    def handle_interrupt_io(self) -> None:
        """Tecla I: el proceso en ejecucion pasa a Bloqueados 8 unidades (no libera memoria)."""
        if self.running_process:
            rp = self.running_process
            rp.status = "Bloqueado"
            rp.blocked_time = 0
            rp.quantum_elapsed = 0
            self.blocked_queue.append(rp)
            self.running_process = None
            self._dispatch()

    def handle_error(self) -> None:
        """Tecla E: el proceso en ejecucion termina por error y libera memoria."""
        if self.running_process:
            self._finish_current_process(with_error=True)
            self._dispatch()

    def pause(self) -> None:
        self.is_paused = True

    def resume(self) -> None:
        self.is_paused = False
