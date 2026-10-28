"""Punto de entrada: Simulador de SO - Programa 5 (Round-Robin)."""
import sys

from PySide6.QtWidgets import QApplication, QInputDialog

import config
from controllers.sim_controller import SimController
from models.simulator import SimulatorEngine
from views.main_window import MainWindow


def pedir_numero_de_procesos():
    n, ok = QInputDialog.getInt(
        None, "Configuracion", "Numero de procesos (N):",
        value=config.PROCESOS_INICIALES_DEFECTO, minValue=1,
        maxValue=config.PROCESOS_INICIALES_MAX)
    return n if ok else None


def pedir_quantum():
    q, ok = QInputDialog.getInt(
        None, "Configuracion", "Valor del Quantum:",
        value=config.QUANTUM_DEFECTO, minValue=config.QUANTUM_MIN,
        maxValue=config.QUANTUM_MAX)
    return q if ok else None


def main():
    app = QApplication(sys.argv)
    n = pedir_numero_de_procesos()
    if n is None:
        return

    quantum = pedir_quantum()
    if quantum is None:
        return

    engine = SimulatorEngine(n, quantum)
    ventana = MainWindow()
    controlador = SimController(engine, ventana)   # referencia viva mientras corre la app
    ventana.show()
    controlador.iniciar()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
