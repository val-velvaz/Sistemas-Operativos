"""Programa 6: Productor-Consumidor (buffer circular acotado de 18 casillas)."""
import sys

from PySide6.QtWidgets import QApplication

from controllers.sim_controller import SimController
from models.simulation import ProducerConsumer
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    ventana = MainWindow()
    controlador = SimController(ProducerConsumer(), ventana)
    ventana.show()
    controlador.iniciar()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
