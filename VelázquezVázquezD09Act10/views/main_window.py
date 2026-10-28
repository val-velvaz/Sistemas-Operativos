"""Ventana principal: solo dibuja el estado del motor y emite las teclas presionadas."""
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QMainWindow,
                               QProgressBar, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from config import (TECLA_BCP, TECLA_CONTINUAR, TECLA_ERROR, TECLA_IO, TECLA_NUEVO,
                    TECLA_PAUSA)
from models.simulator import SimulatorEngine
from views import styles


class MainWindow(QMainWindow):
    # Se emite con la letra (mayuscula) de cada tecla alfabetica presionada
    tecla_presionada = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de SO - Round-Robin (RR)")
        self.resize(1000, 600)
        self._indice_color_reloj = 0
        self._construir_interfaz()

        # La ventana captura las teclas directamente: necesita foco fuerte
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def _construir_interfaz(self):
        central = QWidget()
        principal = QVBoxLayout()
        principal.addLayout(self._crear_barra_superior())
        principal.addLayout(self._crear_zona_central())
        central.setLayout(principal)
        self.setCentralWidget(central)

    def _crear_barra_superior(self) -> QHBoxLayout:
        self.lbl_nuevos = QLabel("Procesos Nuevos: 0")
        self.lbl_quantum = QLabel("Quantum: -")
        self.lbl_estado = QLabel("Estado: Iniciando...")
        self.lbl_reloj = QLabel("Reloj Global: 0")

        fuente = self.lbl_reloj.font()
        fuente.setBold(True)
        fuente.setPointSize(12)
        barra = QHBoxLayout()
        for i, lbl in enumerate((self.lbl_nuevos, self.lbl_quantum, self.lbl_estado, self.lbl_reloj)):
            lbl.setFont(fuente)
            if i:
                barra.addStretch()
            barra.addWidget(lbl)
        return barra

    @staticmethod
    def _crear_tabla(columnas):
        tabla = QTableWidget(0, len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setFocusPolicy(Qt.NoFocus)
        tabla.setStyleSheet(styles.ESTILO_TABLAS)
        return tabla

    def _crear_zona_central(self) -> QHBoxLayout:
        zona = QHBoxLayout()

        # 1. Cola de listos
        col_listos = QVBoxLayout()
        col_listos.addWidget(QLabel("Cola de Listos (carrusel RR):"))
        self.tabla_listos = self._crear_tabla(["ID", "TME", "Transcurrido"])
        col_listos.addWidget(self.tabla_listos)
        zona.addLayout(col_listos)

        # 2. Centro: ejecucion, bloqueados, progreso y controles
        col_centro = QVBoxLayout()
        col_centro.addWidget(QLabel("Proceso en Ejecucion:"))
        self.lbl_ejecucion = QLabel("Ninguno")
        self.lbl_ejecucion.setAlignment(Qt.AlignTop)
        self.lbl_ejecucion.setStyleSheet(styles.ESTILO_PANEL_EJECUCION)
        col_centro.addWidget(self.lbl_ejecucion)

        col_centro.addWidget(QLabel("Cola de Bloqueados:"))
        self.tabla_bloqueados = self._crear_tabla(["ID", "TT en Bloqueado"])
        col_centro.addWidget(self.tabla_bloqueados)

        col_centro.addWidget(QLabel("Progreso General:"))
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setAlignment(Qt.AlignCenter)
        self.barra_progreso.setValue(0)
        col_centro.addWidget(self.barra_progreso)

        col_centro.addWidget(QLabel(self._texto_controles()))

        self.lbl_vim = QLabel("> _")
        self.lbl_vim.setFont(styles.fuente_monoespaciada())
        self.lbl_vim.setStyleSheet(styles.estilo_barra_vim("#00FF66"))
        col_centro.addWidget(self.lbl_vim)
        zona.addLayout(col_centro)

        # 3. Terminados
        col_term = QVBoxLayout()
        col_term.addWidget(QLabel("Procesos Terminados:"))
        self.tabla_terminados = self._crear_tabla(["ID", "Operacion", "Resultado"])
        col_term.addWidget(self.tabla_terminados)
        zona.addLayout(col_term)
        return zona

    @staticmethod
    def _texto_controles() -> str:
        def tag(color, tecla, texto):
            return f"<span style='color: {color};'>{tecla}: {texto}</span>"
        partes = [
            tag("#D5AAFF", TECLA_IO, "E/S"), tag("#FFB3BA", TECLA_ERROR, "Error"),
            tag("#FFFFBA", TECLA_PAUSA, "Pausa"), tag("#BAFFC9", TECLA_CONTINUAR, "Continuar"),
            tag("#FFDFBA", TECLA_NUEVO, "Nuevo"), tag("#E0BBE4", TECLA_BCP, "Tabla BCP"),
        ]
        return "<b>Controles (tecla directa, sin Enter):</b> " + " | ".join(partes)

    # ------------------------------------------------------------------
    # Teclado
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        tecla = event.text().upper()
        # Se ignoran teclas no imprimibles (flechas, Tab, etc.)
        if tecla and tecla.isalpha():
            self.tecla_presionada.emit(tecla)
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # API para el controlador
    # ------------------------------------------------------------------
    def set_estado(self, texto: str, color_fondo: str):
        self.lbl_estado.setText(f"Estado: {texto}")
        self.lbl_estado.setStyleSheet(styles.estilo_estado(color_fondo))

    def mostrar_tecla(self, texto: str, valida: bool = True):
        """Muestra brevemente la tecla reconocida en la barra estilo vim."""
        self.lbl_vim.setStyleSheet(styles.estilo_barra_vim("#00FF66" if valida else "#FF5555"))
        self.lbl_vim.setText(texto)
        QTimer.singleShot(900, self.reiniciar_barra_vim)

    def reiniciar_barra_vim(self):
        if self.lbl_vim.property("finalizada"):
            return
        self.lbl_vim.setStyleSheet(styles.estilo_barra_vim("#00FF66"))
        self.lbl_vim.setText("> _")

    def marcar_finalizada(self):
        self.lbl_vim.setProperty("finalizada", True)
        self.lbl_vim.setStyleSheet(styles.estilo_barra_vim("#888888"))
        self.lbl_vim.setText("> Simulacion finalizada")
        self.barra_progreso.setValue(100)

    def avanzar_color_reloj(self):
        self._indice_color_reloj = (self._indice_color_reloj + 1) % len(styles.COLORES_RELOJ)

    def render(self, engine: SimulatorEngine):
        """Dibuja el estado actual del motor (solo lectura)."""
        self.lbl_reloj.setStyleSheet(f"color: {styles.COLORES_RELOJ[self._indice_color_reloj]};")
        self.lbl_reloj.setText(f"Reloj Global: {engine.global_clock}")
        self.lbl_nuevos.setText(f"Procesos Nuevos: {len(engine.new_queue)}")

        self.lbl_quantum.setText(f"Quantum: {engine.quantum}")
        self._llenar(self.tabla_listos, [(p.id, p.tme, p.time_elapsed) for p in engine.ready_queue])
        self._resaltar_siguiente_en_turno()
        self._llenar(self.tabla_bloqueados, [(p.id, p.blocked_time) for p in engine.blocked_queue])
        self._llenar(self.tabla_terminados,
                     [(p.id, p.operation, p.result) for p in engine.terminated_queue])

        rp = engine.running_process
        if rp:
            self.lbl_ejecucion.setText(
                f"ID: {rp.id}\nOperacion: {rp.operation}\nTME: {rp.tme}\n\n"
                f"Tiempo Transcurrido: {rp.time_elapsed}\nTiempo Restante: {rp.time_remaining}\n"
                f"Quantum: {rp.quantum_elapsed} / {engine.quantum}")
        else:
            self.lbl_ejecucion.setText("Ninguno")

        porcentaje = engine.progress_percent
        self.barra_progreso.setValue(porcentaje)
        self.barra_progreso.setStyleSheet(styles.estilo_barra_progreso(porcentaje))

    def _resaltar_siguiente_en_turno(self):
        """Avance del carrusel: el primer renglon de Listos es el siguiente en usar el CPU."""
        tabla = self.tabla_listos
        if tabla.rowCount() == 0:
            return
        for col in range(tabla.columnCount()):
            item = tabla.item(0, col)
            item.setBackground(QColor("#BAFFC9"))
            item.setForeground(QColor("black"))

    @staticmethod
    def _llenar(tabla: QTableWidget, filas):
        tabla.setRowCount(0)
        for i, fila in enumerate(filas):
            tabla.insertRow(i)
            for j, valor in enumerate(fila):
                tabla.setItem(i, j, QTableWidgetItem(str(valor)))
