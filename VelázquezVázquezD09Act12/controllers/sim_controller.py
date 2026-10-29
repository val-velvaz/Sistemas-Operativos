"""Controlador: avanza la simulacion con un QTimer y termina con ESC."""
from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

from config import INTERVALO_MS
from models.simulation import ProducerConsumer
from views.main_window import MainWindow


class SimController(QObject):
    def __init__(self, sim: ProducerConsumer, view: MainWindow):
        super().__init__()
        self.sim = sim
        self.view = view
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._ciclo)
        self.view.esc_presionado.connect(self.terminar)

    def iniciar(self):
        self.view.render(self.sim)
        self.timer.start(INTERVALO_MS)

    def _ciclo(self):
        self.sim.tick()
        self.view.render(self.sim)

    def terminar(self):
        """Tecla ESC: detiene la simulacion y cierra el programa."""
        self.timer.stop()
        self.view.mostrar_fin()
        QApplication.quit()
