import random
import unittest

from config import MAX_PROCESOS_MEMORIA, TIEMPO_BLOQUEO
from models.process import Estado
from models.simulator import SimulatorEngine
from utils.data_generator import evaluate_operation


def correr(engine, limite=10000):
    n = 0
    while engine.tick():
        n += 1
        assert n < limite, "la simulacion no termina"
    return n


class PruebasMotor(unittest.TestCase):
    def setUp(self):
        random.seed(7)

    def test_memoria_maxima_cinco(self):
        e = SimulatorEngine(12, 4)
        self.assertEqual(e.get_memory_count(), MAX_PROCESOS_MEMORIA)
        self.assertEqual(len(e.new_queue), 12 - MAX_PROCESOS_MEMORIA)
        while e.tick():
            self.assertLessEqual(e.get_memory_count(), MAX_PROCESOS_MEMORIA)

    def test_reloj_final_es_suma_de_tme(self):
        e = SimulatorEngine(8, 3)
        total = sum(p.tme for p in e.new_queue + e.ready_queue + [e.running_process])
        correr(e)
        self.assertEqual(e.global_clock, total)   # el CPU nunca queda ocioso

    def test_quantum_saca_al_proceso_al_final_de_listos(self):
        e = SimulatorEngine(3, 2)
        primero = e.running_process
        e.tick(); e.tick()                       # agota el quantum de 2
        self.assertNotEqual(e.running_process.id, primero.id)
        self.assertEqual(e.ready_queue[-1].id, primero.id)
        self.assertEqual(primero.status, Estado.LISTO)
        self.assertEqual(primero.time_elapsed, 2)

    def test_nadie_usa_mas_del_quantum_seguido(self):
        e = SimulatorEngine(6, 3)
        while e.tick():
            if e.running_process:
                self.assertLessEqual(e.running_process.quantum_elapsed, 3)

    def test_proceso_que_termina_al_agotar_quantum_no_regresa_a_listos(self):
        e = SimulatorEngine(2, 5)
        e.running_process.tme = 5                # termina justo al cumplir el quantum
        pid = e.running_process.id
        for _ in range(5):
            e.tick()
        self.assertIn(pid, [p.id for p in e.terminated_queue])
        self.assertNotIn(pid, [p.id for p in e.ready_queue])

    def test_quantum_grande_se_comporta_como_fcfs(self):
        e = SimulatorEngine(5, 1000)
        correr(e)
        self.assertEqual([p.id for p in e.terminated_queue], [1, 2, 3, 4, 5])

    def test_interrupcion_io_bloquea_8_unidades_y_pasa_el_cpu(self):
        e = SimulatorEngine(3, 4)
        e.tick()
        pid = e.running_process.id
        e.handle_interrupt_io()
        self.assertEqual(e.blocked_queue[0].id, pid)
        self.assertIsNotNone(e.running_process)
        self.assertNotEqual(e.running_process.id, pid)
        for _ in range(TIEMPO_BLOQUEO - 1):
            e.tick()
        self.assertIn(pid, [p.id for p in e.blocked_queue])
        e.tick()
        self.assertNotIn(pid, [p.id for p in e.blocked_queue])

    def test_error_termina_con_error_y_libera_memoria(self):
        e = SimulatorEngine(7, 4)
        e.tick()
        pid = e.running_process.id
        antes = len(e.new_queue)
        e.handle_error()
        self.assertEqual(e.terminated_queue[-1].id, pid)
        self.assertEqual(e.terminated_queue[-1].result, "ERROR")
        self.assertEqual(len(e.new_queue), antes - 1)

    def test_tecla_n_incrementa_total_y_termina(self):
        e = SimulatorEngine(3, 4)
        e.request_new_process()
        self.assertEqual(e.total_generated, 4)
        correr(e)
        self.assertEqual(len(e.terminated_queue), 4)
        self.assertEqual(e.progress_percent, 100)

    def test_pausa_congela_el_reloj(self):
        e = SimulatorEngine(3, 4)
        e.tick()
        e.pause()
        reloj = e.global_clock
        e.tick()
        self.assertEqual(e.global_clock, reloj)
        e.resume()
        e.tick()
        self.assertEqual(e.global_clock, reloj + 1)

    def test_get_all_processes_incluye_todos_los_estados(self):
        e = SimulatorEngine(9, 4)
        e.tick()
        e.handle_interrupt_io()
        self.assertEqual([p.id for p in e.get_all_processes()], list(range(1, 10)))
        estados = {p.status for p in e.get_all_processes()}
        self.assertTrue({Estado.NUEVO, Estado.LISTO, Estado.BLOQUEADO, Estado.EJECUCION} <= estados)

    def test_evaluate_operation(self):
        self.assertEqual(evaluate_operation("10 + 5"), "15")
        self.assertEqual(evaluate_operation("10 / 4"), "2.5")
        self.assertEqual(evaluate_operation("10 % 4"), "2")
        self.assertEqual(evaluate_operation("10 / 0"), "ERROR")


if __name__ == "__main__":
    unittest.main()
