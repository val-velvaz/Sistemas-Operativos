"""Ventana principal del Programa 6."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QMainWindow, QVBoxLayout, QWidget)
from PySide6.QtGui import QColor

from config import CAPACIDAD
from views import styles
from views.container_widget import ContainerWidget


class AgentePanel(QFrame):
    """Panel con la informacion de un agente (productor o consumidor)."""

    def __init__(self, titulo: str, color: str, verbo: str):
        super().__init__()
        self.verbo = verbo
        self.setStyleSheet(styles.estilo_panel(color))
        layout = QGridLayout(self)
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        self.lbl_estado = QLabel()
        self.lbl_detalle = QLabel()
        self.lbl_detalle.setWordWrap(True)
        self.lbl_entrada = QLabel()
        self.lbl_total = QLabel()
        layout.addWidget(lbl_titulo, 0, 0)
        layout.addWidget(self.lbl_estado, 0, 1, alignment=Qt.AlignRight)
        layout.addWidget(self.lbl_detalle, 1, 0, 1, 2)
        layout.addWidget(self.lbl_entrada, 2, 0)
        layout.addWidget(self.lbl_total, 2, 1, alignment=Qt.AlignRight)

    def actualizar(self, agente):
        self.lbl_estado.setText(agente.estado)
        self.lbl_estado.setStyleSheet(styles.estilo_badge(styles.COLOR_ESTADO[agente.estado]))
        self.lbl_detalle.setText(agente.detalle)
        if agente.estado == "Trabajando":
            hechos = agente.procesados_entrada
            meta = hechos + agente.por_procesar
            self.lbl_entrada.setText(f"Esta entrada: {hechos} de {meta} elementos")
        else:
            self.lbl_entrada.setText("Esta entrada: -")
        self.lbl_total.setText(f"Total {self.verbo}: {agente.total}")


class MainWindow(QMainWindow):
    esc_presionado = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programa 6 - Productor-Consumidor")
        self.resize(1150, 720)
        self.setStyleSheet(styles.ESTILO_VENTANA)

        central = QWidget(objectName="central")
        principal = QVBoxLayout(central)

        # Barra superior
        barra = QHBoxLayout()
        self.lbl_reloj = QLabel()
        self.lbl_ocupacion = QLabel()
        self.lbl_dentro = QLabel()
        for lbl in (self.lbl_reloj, self.lbl_ocupacion, self.lbl_dentro):
            lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        barra.addWidget(self.lbl_reloj)
        barra.addStretch()
        barra.addWidget(self.lbl_dentro)
        barra.addStretch()
        barra.addWidget(self.lbl_ocupacion)
        principal.addLayout(barra)

        # Contenedor
        principal.addWidget(QLabel(
            f"<b>Contenedor (buffer circular de {CAPACIDAD} casillas)</b> &nbsp; "
            "<span style='color:#FFB3BA'>P</span> = siguiente casilla del productor &nbsp; "
            "<span style='color:#D5AAFF'>C</span> = siguiente casilla del consumidor"))
        self.contenedor = ContainerWidget(CAPACIDAD)
        principal.addWidget(self.contenedor, 3)

        # Paneles de agentes
        agentes = QHBoxLayout()
        self.panel_productor = AgentePanel("Productor", styles.COLOR_PRODUCTOR, "producidos")
        self.panel_consumidor = AgentePanel("Consumidor", styles.COLOR_CONSUMIDOR, "consumidos")
        agentes.addWidget(self.panel_productor)
        agentes.addWidget(self.panel_consumidor)
        principal.addLayout(agentes)

        # Bitacora de mensajes
        principal.addWidget(QLabel("<b>Mensajes</b> (presiona ESC para terminar)"))
        self.lista = QListWidget()
        self.lista.setFocusPolicy(Qt.NoFocus)
        principal.addWidget(self.lista, 2)

        self.setCentralWidget(central)
        self.setFocusPolicy(Qt.StrongFocus)
        self._mostrados = 0

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.esc_presionado.emit()
        else:
            super().keyPressEvent(event)

    def render(self, sim):
        self.lbl_reloj.setText(f"Tiempo: {sim.reloj}")
        b = sim.buffer
        self.lbl_ocupacion.setText(f"Ocupadas: {b.ocupadas}/{b.capacidad}   Libres: {b.libres}")
        if sim.dentro:
            self.lbl_dentro.setText(f"En el contenedor: {sim.dentro}")
        else:
            self.lbl_dentro.setText("En el contenedor: nadie")
        self.contenedor.actualizar(sim)
        self.panel_productor.actualizar(sim.productor)
        self.panel_consumidor.actualizar(sim.consumidor)

        # Bitacora: solo agrega los mensajes nuevos
        n = min(self._pendientes(sim), len(sim.mensajes))
        nuevos = sim.mensajes[-n:] if n > 0 else []
        for m in nuevos:
            color = styles.COLOR_PRODUCTOR if m.agente == "Productor" else styles.COLOR_CONSUMIDOR
            item = QListWidgetItem(f"[t={m.tiempo:>4}] {m.agente:<10} {m.texto}")
            item.setForeground(QColor(color))
            self.lista.addItem(item)
        while self.lista.count() > 200:
            self.lista.takeItem(0)
        self.lista.scrollToBottom()

    def _pendientes(self, sim) -> int:
        """Numero de mensajes que aun no se agregaron a la lista."""
        total = sim.total_mensajes
        n = total - self._mostrados
        self._mostrados = total
        return n

    def mostrar_fin(self):
        self.lbl_dentro.setText("Simulacion terminada (ESC)")
