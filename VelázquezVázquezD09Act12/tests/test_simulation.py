import random
import unittest

from config import CAPACIDAD, MAX_ELEMENTOS, MIN_ELEMENTOS
from models.buffer import CircularBuffer
from models.simulation import Estado, ProducerConsumer


class PruebasBuffer(unittest.TestCase):
    def test_circular_regresa_a_la_casilla_1(self):
        b = CircularBuffer()
        for _ in range(CAPACIDAD):
            b.poner("x")
        self.assertTrue(b.lleno)
        self.assertEqual(b.entrada, 0)
        for _ in range(3):
            b.quitar()
        self.assertEqual(b.poner("y"), 0)      # vuelve a la casilla 1
        self.assertEqual(b.salida, 3)

    def test_no_produce_lleno_ni_consume_vacio(self):
        b = CircularBuffer()
        with self.assertRaises(RuntimeError):
            b.quitar()
        for _ in range(CAPACIDAD):
            b.poner("x")
        with self.assertRaises(RuntimeError):
            b.poner("x")


class PruebasSimulacion(unittest.TestCase):
    def correr(self, semilla, pasos=3000):
        s = ProducerConsumer(random.Random(semilla))
        for _ in range(pasos):
            p_antes, c_antes = s.productor.total, s.consumidor.total
            s.tick()
            # nunca trabajan los dos a la vez
            ambos = (s.productor.estado == Estado.TRABAJANDO and
                     s.consumidor.estado == Estado.TRABAJANDO)
            self.assertFalse(ambos)
            # a lo mas un elemento por unidad de tiempo y solo quien esta dentro
            dp, dc = s.productor.total - p_antes, s.consumidor.total - c_antes
            self.assertLessEqual(dp + dc, 1)
            # invariantes del buffer
            b = s.buffer
            self.assertEqual(b.ocupadas, sum(x is not None for x in b.casillas))
            self.assertEqual(b.ocupadas, s.productor.total - s.consumidor.total)
            self.assertEqual((b.salida + b.ocupadas) % b.capacidad, b.entrada)
        return s

    def test_invariantes_varias_semillas(self):
        for semilla in range(30):
            self.correr(semilla)

    def test_ambos_trabajan_y_el_buffer_da_vueltas(self):
        s = self.correr(1, 4000)
        self.assertGreater(s.productor.total, CAPACIDAD * 2)
        self.assertGreater(s.consumidor.total, CAPACIDAD * 2)

    def test_elementos_por_entrada_entre_3_y_6(self):
        s = ProducerConsumer(random.Random(5))
        for _ in range(3000):
            s.tick()
        for m in s.mensajes:
            if "entra al contenedor" in m.texto:
                n = int(m.texto.split()[-2])
                self.assertTrue(MIN_ELEMENTOS <= n <= MAX_ELEMENTOS)

    def test_consume_en_el_mismo_orden_en_que_se_produjo(self):
        s = ProducerConsumer(random.Random(9))
        producidos, consumidos = [], []
        orig_poner, orig_quitar = s.buffer.poner, s.buffer.quitar
        def poner(e):
            producidos.append(e); return orig_poner(e)
        def quitar():
            i, e = orig_quitar(); consumidos.append(e); return i, e
        s.buffer.poner, s.buffer.quitar = poner, quitar
        for _ in range(3000):
            s.tick()
        self.assertGreater(len(consumidos), 50)
        self.assertEqual(consumidos, producidos[:len(consumidos)])   # FIFO

    def test_productor_no_entra_lleno_y_consumidor_no_entra_vacio(self):
        s = ProducerConsumer(random.Random(0))
        s.consumidor.estado = Estado.INTENTANDO
        s._avanzar(s.consumidor)
        self.assertEqual(s.consumidor.estado, Estado.DORMIDO)
        for _ in range(CAPACIDAD):
            s.buffer.poner("x")
        s.productor.estado = Estado.INTENTANDO
        s._avanzar(s.productor)
        self.assertEqual(s.productor.estado, Estado.DORMIDO)

    def test_exclusion_mutua_al_intentar(self):
        s = ProducerConsumer(random.Random(0))
        s.buffer.poner("a")
        s.dentro = "Productor"
        s.productor.estado = Estado.TRABAJANDO
        s.consumidor.estado = Estado.INTENTANDO
        s._avanzar(s.consumidor)
        self.assertEqual(s.consumidor.estado, Estado.DORMIDO)
        self.assertIn("productor esta dentro", s.mensajes[-2].texto)


if __name__ == "__main__":
    unittest.main()
