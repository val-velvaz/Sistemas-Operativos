import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                               QHeaderView, QInputDialog, QProgressBar, QDialog)
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QFont, QColor, QPainter, QPalette, QPen

from models.process import FRAME_SIZE
from models.simulator import SimulatorEngine, TIEMPO_BLOQUEO, TOTAL_MARCOS

ESTILO_ENCABEZADO = """
    QHeaderView::section {
        background-color: #BAE1FF; color: black; font-weight: bold; border: 1px solid #777;
    }
"""


# ----------------------------------------------------------------------
# Widget que dibuja la memoria dividida en marcos
# ----------------------------------------------------------------------
class MemoriaWidget(QWidget):
    """Dibuja los 46 marcos (0 a 45) en dos columnas, como en la figura del enunciado.
    Cada marco se rellena en proporcion a lo ocupado (fragmentacion interna visible):
    libre = sin color, S.O. = negro, Listo = azul, Ejecucion = rojo, Bloqueado = morado."""

    COLORES = {
        "SO": "#000000",
        "Listo": "#4EA5F5",
        "Ejecucion": "#E05555",
        "Bloqueado": "#A66BE0",
    }
    COLUMNAS = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.datos = []
        self.setMinimumSize(340, 520)

    def set_datos(self, datos):
        self.datos = datos
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        filas = (TOTAL_MARCOS + self.COLUMNAS - 1) // self.COLUMNAS
        alto_encabezado = 22
        alto_fila = (h - alto_encabezado) / filas
        ancho_col = w / self.COLUMNAS
        color_texto = self.palette().color(QPalette.WindowText)

        fuente = QFont(p.font())
        fuente.setBold(True)
        fuente.setPointSize(8)
        p.setFont(fuente)

        for c in range(self.COLUMNAS):
            p.setPen(color_texto)
            p.drawText(QRectF(c * ancho_col, 0, 34, alto_encabezado), Qt.AlignCenter, "No.")
            p.drawText(QRectF(c * ancho_col + 34, 0, ancho_col - 40, alto_encabezado),
                       Qt.AlignCenter, "Marco")

        for f in range(TOTAL_MARCOS):
            fila, col = f // self.COLUMNAS, f % self.COLUMNAS
            x0 = col * ancho_col
            y0 = alto_encabezado + fila * alto_fila

            # numero de marco
            p.setPen(color_texto)
            p.drawText(QRectF(x0, y0, 34, alto_fila), Qt.AlignCenter, str(f))

            # barra del marco
            barra = QRectF(x0 + 36, y0 + 2, ancho_col - 42, alto_fila - 4)
            p.setPen(QPen(QColor("#777777"), 1))
            p.setBrush(QColor("#FFFFFF"))
            p.drawRect(barra)

            if f < len(self.datos):
                estado, pid, usado = self.datos[f]
            else:
                estado, pid, usado = "Libre", None, 0

            texto = ""
            color_texto_barra = QColor("black")
            if estado in self.COLORES:
                proporcion = usado / FRAME_SIZE
                relleno = QRectF(barra.x(), barra.y(), barra.width() * proporcion, barra.height())
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(self.COLORES[estado]))
                p.drawRect(relleno)
                p.setPen(QPen(QColor("#777777"), 1))
                p.setBrush(Qt.NoBrush)
                p.drawRect(barra)
                if estado == "SO":
                    texto = "S.O."
                    color_texto_barra = QColor("white")
                else:
                    texto = f"P{pid}  {usado}/{FRAME_SIZE}"
            else:
                texto = "libre"
                color_texto_barra = QColor("#888888")

            p.setPen(color_texto_barra)
            p.drawText(barra, Qt.AlignCenter, texto)
        p.end()


# ----------------------------------------------------------------------
# Ventanas emergentes (se cierran unicamente con la tecla C)
# ----------------------------------------------------------------------
class TablaBCPWindow(QDialog):
    """BCP final con todos los tiempos (al terminar la simulacion)"""
    def __init__(self, procesos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabla de Control de Procesos (BCP) - Final")
        self.resize(1100, 400)

        layout = QVBoxLayout()
        tabla = QTableWidget(len(procesos), 12)
        tabla.setHorizontalHeaderLabels([
            "ID", "Operacion", "Resultado", "TME", "Tamano", "Llegada",
            "Finalizacion", "Retorno", "Respuesta", "Espera", "Servicio", "Terminacion"
        ])
        tabla.setStyleSheet(ESTILO_ENCABEZADO)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        for i, p in enumerate(procesos):
            valores = [p.id, p.operation, p.result, p.tme, p.size, p.arrival_time,
                       p.finish_time, p.return_time, p.response_time, p.waiting_time,
                       p.service_time, p.final_status]
            for j, v in enumerate(valores):
                tabla.setItem(i, j, QTableWidgetItem(str(v)))

        tabla.resizeColumnsToContents()
        layout.addWidget(tabla)
        self.setLayout(layout)


class TablaProcesosLiveWindow(QDialog):
    """Tecla B: BCP de TODOS los procesos que existen en ese momento. Se reanuda con C."""

    COLUMNAS = ["ID", "Estado", "Detalle de Estado", "Operacion y Datos", "Tamano", "Resultado",
                "T. Llegada", "T. Finalizacion", "T. Retorno", "T. Espera (al momento)",
                "T. Servicio (al momento)", "T. Restante en CPU", "T. Respuesta"]

    def __init__(self, procesos, reloj_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Tabla de Procesos (BCP) - Reloj: {reloj_actual}  |  Presiona 'C' para continuar")
        self.resize(1350, 420)
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout()
        aviso = QLabel("<b>Simulacion en pausa.</b> Presiona la tecla 'C' para continuar donde quedo.")
        aviso.setStyleSheet("color: #FFFFBA; padding: 4px;")
        layout.addWidget(aviso)

        tabla = QTableWidget(len(procesos), len(self.COLUMNAS))
        tabla.setHorizontalHeaderLabels(self.COLUMNAS)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setStyleSheet(ESTILO_ENCABEZADO)

        for fila, p in enumerate(procesos):
            valores = [
                p.id, p.status, self._detalle_estado(p), p.operation, p.size,
                p.result if p.result is not None else "-",
                self._o_guion(p.arrival_time), self._o_guion(p.finish_time),
                self._o_guion(p.return_time), self._o_guion(self._espera_actual(p, reloj_actual)),
                p.service_time, "-" if p.status == "Terminado" else p.time_remaining,
                self._o_guion(p.response_time),
            ]
            for col, v in enumerate(valores):
                tabla.setItem(fila, col, QTableWidgetItem(str(v)))

        tabla.resizeColumnsToContents()
        layout.addWidget(tabla)
        self.setLayout(layout)

    @staticmethod
    def _o_guion(valor):
        return "-" if valor is None else str(valor)

    @staticmethod
    def _detalle_estado(p) -> str:
        if p.status == "Nuevo":
            return "-"
        if p.status == "Bloqueado":
            return f"Restante en E/S: {TIEMPO_BLOQUEO - p.blocked_time}"
        if p.status == "Terminado":
            return p.final_status
        return "-"

    @staticmethod
    def _espera_actual(p, reloj_actual):
        if p.arrival_time is None:
            return None
        if p.finish_time is not None:
            return p.waiting_time
        return (reloj_actual - p.arrival_time) - p.service_time

    def keyPressEvent(self, event):
        if event.text().upper() == 'C':
            self.accept()


class TablaPaginasWindow(QDialog):
    """Tecla T: tabla de paginas de cada proceso en memoria (una entrada por proceso)
    y relacion de marcos libres. Se reanuda con C."""

    def __init__(self, tablas, marcos_libres, reloj_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Tabla de Paginas - Reloj: {reloj_actual}  |  Presiona 'C' para continuar")
        self.resize(900, 460)
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout()
        aviso = QLabel("<b>Simulacion en pausa.</b> Presiona la tecla 'C' para continuar donde quedo.")
        aviso.setStyleSheet("color: #FFFFBA; padding: 4px;")
        layout.addWidget(aviso)

        tabla = QTableWidget(len(tablas), 5)
        tabla.setHorizontalHeaderLabels(["Proceso", "Tamano", "Estado", "No. paginas",
                                         "Tabla de paginas (pagina -> marco)"])
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setStyleSheet(ESTILO_ENCABEZADO)
        for fila, (pid, tam, estado, paginas) in enumerate(tablas):
            relacion = ",  ".join(f"{pag} -> {marco}" for pag, marco in paginas)
            for col, v in enumerate([f"Proceso {pid}", tam, estado, len(paginas), relacion]):
                tabla.setItem(fila, col, QTableWidgetItem(str(v)))
        tabla.resizeColumnsToContents()
        tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(tabla)

        libres = ", ".join(str(m) for m in marcos_libres) if marcos_libres else "ninguno"
        lbl = QLabel(f"<b>Marcos libres ({len(marcos_libres)}):</b> {libres}")
        lbl.setWordWrap(True)
        lbl.setStyleSheet("padding: 6px;")
        layout.addWidget(lbl)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.text().upper() == 'C':
            self.accept()


# ----------------------------------------------------------------------
# Ventana principal
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    TECLAS_VALIDAS = {
        'I': "Interrupcion E/S",
        'E': "Error",
        'P': "Pausa",
        'C': "Continuar",
        'N': "Nuevo proceso",
        'B': "Tabla de procesos (BCP)",
        'T': "Tabla de paginas",
    }

    def __init__(self, total_jobs: int, quantum: int):
        super().__init__()
        self.engine = SimulatorEngine(total_jobs, quantum)
        self.comandos_habilitados = True  # se desactiva al terminar la simulacion

        self.setWindowTitle("Simulador de SO - Round-Robin con Paginacion Simple")
        self.resize(1400, 780)

        self.colores_reloj = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"]
        self.indice_color_reloj = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.ciclo_simulacion)

        self.configurar_interfaz()
        self.actualizar_pantalla()

        self.cambiar_estado("Ejecutando", "#BAFFC9")
        self.timer.start(1000)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def configurar_interfaz(self):
        widget_central = QWidget()
        layout_principal = QVBoxLayout()

        # --- SECCION SUPERIOR ---
        layout_superior = QHBoxLayout()
        self.lbl_reloj = QLabel("Reloj Global: 0")
        self.lbl_nuevos = QLabel("Procesos Nuevos: 0")
        self.lbl_quantum = QLabel(f"Quantum: {self.engine.quantum}")
        self.lbl_estado = QLabel("Estado: Iniciando...")

        font = self.lbl_reloj.font()
        font.setBold(True)
        font.setPointSize(12)
        for lbl in (self.lbl_nuevos, self.lbl_quantum, self.lbl_estado, self.lbl_reloj):
            lbl.setFont(font)

        layout_superior.addWidget(self.lbl_nuevos)
        layout_superior.addStretch()
        layout_superior.addWidget(self.lbl_quantum)
        layout_superior.addStretch()
        layout_superior.addWidget(self.lbl_estado)
        layout_superior.addStretch()
        layout_superior.addWidget(self.lbl_reloj)
        layout_principal.addLayout(layout_superior)

        # Proximo proceso por ingresar a Listos (ID, tamano y marcos necesarios)
        self.lbl_proximo = QLabel("")
        self.lbl_proximo.setStyleSheet("padding: 3px 6px; border: 1px solid #777; border-radius: 3px;")
        layout_principal.addWidget(self.lbl_proximo)

        estilo_tablas = """
            QHeaderView::section { background-color: #E0BBE4; color: black; font-weight: bold; border: 1px solid #777; }
            QTableCornerButton::section { background-color: #E0BBE4; border: 1px solid #777; }
        """

        # --- SECCION CENTRAL ---
        layout_central = QHBoxLayout()

        # 0. Memoria dividida en marcos
        layout_memoria = QVBoxLayout()
        layout_memoria.addWidget(QLabel("Memoria (46 marcos de 5):"))
        self.memoria_widget = MemoriaWidget()
        layout_memoria.addWidget(self.memoria_widget, 1)
        leyenda = QLabel(
            "<span style='background-color:#000000; color:white;'>&nbsp;S.O.&nbsp;</span> "
            "<span style='background-color:#4EA5F5;'>&nbsp;Listo&nbsp;</span> "
            "<span style='background-color:#E05555;'>&nbsp;Ejecucion&nbsp;</span> "
            "<span style='background-color:#A66BE0;'>&nbsp;Bloqueado&nbsp;</span> "
            "Sin color: libre")
        layout_memoria.addWidget(leyenda)
        layout_central.addLayout(layout_memoria, 3)

        # 1. Tabla de Listos
        layout_listos = QVBoxLayout()
        layout_listos.addWidget(QLabel("Cola de Listos (carrusel RR):"))
        self.tabla_listos = QTableWidget(0, 4)
        self.tabla_listos.setHorizontalHeaderLabels(["ID", "TME", "Transcurrido", "Tamano"])
        self.tabla_listos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_listos.setFocusPolicy(Qt.NoFocus)
        self.tabla_listos.setStyleSheet(estilo_tablas)
        layout_listos.addWidget(self.tabla_listos)
        layout_central.addLayout(layout_listos, 2)

        # 2. Centro: Ejecucion, Bloqueados y controles
        layout_centro = QVBoxLayout()
        layout_centro.addWidget(QLabel("Proceso en Ejecucion:"))

        self.lbl_ejecucion_datos = QLabel("Ninguno")
        self.lbl_ejecucion_datos.setAlignment(Qt.AlignTop)
        self.lbl_ejecucion_datos.setStyleSheet("border: 1px solid #555; padding: 10px; background-color: #2b2b2b; color: white;")
        layout_centro.addWidget(self.lbl_ejecucion_datos)

        layout_centro.addWidget(QLabel("Cola de Bloqueados:"))
        self.tabla_bloqueados = QTableWidget(0, 2)
        self.tabla_bloqueados.setHorizontalHeaderLabels(["ID", "TT en Bloqueado"])
        self.tabla_bloqueados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_bloqueados.setFocusPolicy(Qt.NoFocus)
        self.tabla_bloqueados.setStyleSheet(estilo_tablas)
        layout_centro.addWidget(self.tabla_bloqueados)

        layout_centro.addWidget(QLabel("Progreso General:"))
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setAlignment(Qt.AlignCenter)
        self.barra_progreso.setValue(0)
        layout_centro.addWidget(self.barra_progreso)

        texto_controles = (
            "<b>Controles (tecla directa):</b> "
            "<span style='color: #D5AAFF;'>I: E/S</span> | "
            "<span style='color: #FFB3BA;'>E: Error</span> | "
            "<span style='color: #FFFFBA;'>P: Pausa</span> | "
            "<span style='color: #BAFFC9;'>C: Continuar</span> | "
            "<span style='color: #FFDFBA;'>N: Nuevo</span> | "
            "<span style='color: #E0BBE4;'>B: BCP</span> | "
            "<span style='color: #BAE1FF;'>T: Tabla de paginas</span>"
        )
        lbl_controles = QLabel(texto_controles)
        lbl_controles.setWordWrap(True)
        layout_centro.addWidget(lbl_controles)

        self.lbl_vim_status = QLabel("> _")
        self.lbl_vim_status.setFont(self._fuente_monoespaciada())
        self.lbl_vim_status.setStyleSheet(self._estilo_barra_vim("#00FF66"))
        layout_centro.addWidget(self.lbl_vim_status)

        layout_central.addLayout(layout_centro, 3)

        # 3. Tabla de Procesos Terminados
        layout_terminados = QVBoxLayout()
        layout_terminados.addWidget(QLabel("Procesos Terminados (rojo = ERROR):"))
        self.tabla_terminados = QTableWidget(0, 3)
        self.tabla_terminados.setHorizontalHeaderLabels(["ID", "Operacion", "Resultado"])
        self.tabla_terminados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_terminados.setFocusPolicy(Qt.NoFocus)
        self.tabla_terminados.setStyleSheet(estilo_tablas)
        layout_terminados.addWidget(self.tabla_terminados)
        layout_central.addLayout(layout_terminados, 2)

        layout_principal.addLayout(layout_central)
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

    @staticmethod
    def _fuente_monoespaciada() -> QFont:
        fuente = QFont("Consolas")
        fuente.setStyleHint(QFont.Monospace)
        fuente.setPointSize(10)
        return fuente

    @staticmethod
    def _estilo_barra_vim(color_texto: str) -> str:
        return (
            f"background-color: black; color: {color_texto}; padding: 4px 8px; "
            "border: 1px solid #444; border-radius: 3px;"
        )

    def cambiar_estado(self, texto, color_fondo):
        self.lbl_estado.setText(f"Estado: {texto}")
        self.lbl_estado.setStyleSheet(
            f"background-color: {color_fondo}; color: black; padding: 4px 10px; border-radius: 5px;"
        )

    # ------------------------------------------------------------------
    # Captura de teclado directa
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if not self.comandos_habilitados:
            return super().keyPressEvent(event)

        tecla = event.text().upper()
        if not tecla or not tecla.isalpha():
            return super().keyPressEvent(event)

        if tecla not in self.TECLAS_VALIDAS:
            self._mostrar_en_barra_vim(f"> {tecla}  (tecla no valida)", valida=False)
            return

        self._mostrar_en_barra_vim(f"> {tecla}  -  {self.TECLAS_VALIDAS[tecla]}", valida=True)
        self.ejecutar_comando(tecla)

    def _mostrar_en_barra_vim(self, texto: str, valida: bool = True):
        color = "#00FF66" if valida else "#FF5555"
        self.lbl_vim_status.setStyleSheet(self._estilo_barra_vim(color))
        self.lbl_vim_status.setText(texto)
        QTimer.singleShot(900, self._resetear_barra_vim)

    def _resetear_barra_vim(self):
        if not self.comandos_habilitados:
            return
        self.lbl_vim_status.setStyleSheet(self._estilo_barra_vim("#00FF66"))
        self.lbl_vim_status.setText("> _")

    def ejecutar_comando(self, tecla: str):
        if tecla == 'I' and not self.engine.is_paused:
            self.engine.handle_interrupt_io()
            self.cambiar_estado("Interrupcion E/S", "#D5AAFF")
            self.actualizar_pantalla()

        elif tecla == 'E' and not self.engine.is_paused:
            self.engine.handle_error()
            self.cambiar_estado("Error", "#FFB3BA")
            self.actualizar_pantalla()

        elif tecla == 'P':
            self.engine.pause()
            self.timer.stop()
            self.cambiar_estado("Pausado", "#FFFFBA")

        elif tecla == 'C':
            if self.engine.is_paused:
                self.engine.resume()
                self.timer.start(1000)
                self.cambiar_estado("Ejecutando", "#BAFFC9")

        elif tecla == 'N':
            self.engine.request_new_process()
            self.cambiar_estado("Nuevo proceso generado", "#FFDFBA")
            self.actualizar_pantalla()

        elif tecla == 'B':
            self.mostrar_tabla_procesos()

        elif tecla == 'T':
            self.mostrar_tabla_paginas()

    def _mostrar_dialogo_en_pausa(self, crear_dialogo, texto_estado, color):
        """Pausa la simulacion, muestra la ventana y, al cerrarla con C, la reanuda
        solo si no estaba pausada previamente con P."""
        estaba_pausado = self.engine.is_paused
        if not estaba_pausado:
            self.engine.pause()
            self.timer.stop()
        self.cambiar_estado(texto_estado, color)

        crear_dialogo().exec()

        if not estaba_pausado:
            self.engine.resume()
            self.timer.start(1000)
            self.cambiar_estado("Ejecutando", "#BAFFC9")
        else:
            self.cambiar_estado("Pausado", "#FFFFBA")

    def mostrar_tabla_procesos(self):
        """Tecla B: BCP de todos los procesos actuales."""
        e = self.engine
        procesos = (list(e.new_queue) + list(e.ready_queue)
                    + ([e.running_process] if e.running_process else [])
                    + list(e.blocked_queue) + list(e.terminated_queue))
        procesos.sort(key=lambda p: p.id)
        self._mostrar_dialogo_en_pausa(
            lambda: TablaProcesosLiveWindow(procesos, e.global_clock, self),
            "Mostrando tabla de procesos (BCP)", "#E0BBE4")

    def mostrar_tabla_paginas(self):
        """Tecla T: tabla de paginas de cada proceso y marcos libres."""
        e = self.engine
        tablas = e.get_page_tables()
        libres = e.get_free_frames()
        self._mostrar_dialogo_en_pausa(
            lambda: TablaPaginasWindow(tablas, libres, e.global_clock, self),
            "Mostrando tabla de paginas", "#BAE1FF")

    # ------------------------------------------------------------------
    def ciclo_simulacion(self):
        sigue_activo = self.engine.tick()

        if not self.engine.is_paused:
            self.indice_color_reloj = (self.indice_color_reloj + 1) % 5

        self.actualizar_pantalla()

        if not sigue_activo:
            self.timer.stop()
            self.cambiar_estado("Terminado", "#BAE1FF")
            self.comandos_habilitados = False
            self.lbl_vim_status.setStyleSheet(self._estilo_barra_vim("#888888"))
            self.lbl_vim_status.setText("> Simulacion finalizada")
            self.barra_progreso.setValue(100)

            # Tabla final de BCP (la ventana mantiene la pantalla para observar)
            dialogo = TablaBCPWindow(sorted(self.engine.terminated_queue, key=lambda p: p.id), self)
            dialogo.exec()
        else:
            if not self.engine.is_paused:
                self.cambiar_estado("Ejecutando", "#BAFFC9")

    def actualizar_pantalla(self):
        e = self.engine
        color_actual = self.colores_reloj[self.indice_color_reloj]
        self.lbl_reloj.setStyleSheet(f"color: {color_actual};")
        self.lbl_reloj.setText(f"Reloj Global: {e.global_clock}")

        # Procesos en estado Nuevo y proximo en ingresar (ID, tamano y marcos requeridos)
        self.lbl_nuevos.setText(f"Procesos Nuevos: {len(e.new_queue)}")
        libres = len(e.get_free_frames())
        if e.new_queue:
            nx = e.new_queue[0]
            self.lbl_proximo.setText(
                f"Nuevos: {len(e.new_queue)}   |   Por ingresar a Listos:  ID {nx.id}   Tam {nx.size}"
                f"   ({nx.num_pages} marcos necesarios)   |   Marcos libres: {libres}")
        else:
            self.lbl_proximo.setText(f"Nuevos: 0   |   Sin procesos en espera   |   Marcos libres: {libres}")

        # Memoria por marcos
        self.memoria_widget.set_datos(e.get_frame_table())

        # Cola de listos
        self.tabla_listos.setRowCount(0)
        for i, p in enumerate(e.ready_queue):
            self.tabla_listos.insertRow(i)
            for col, v in enumerate([p.id, p.tme, p.time_elapsed, p.size]):
                self.tabla_listos.setItem(i, col, QTableWidgetItem(str(v)))
            if i == 0:  # siguiente en recibir el procesador (avance del carrusel)
                for col in range(4):
                    self.tabla_listos.item(i, col).setBackground(QColor("#BAFFC9"))
                    self.tabla_listos.item(i, col).setForeground(QColor("black"))

        # Cola de bloqueados
        self.tabla_bloqueados.setRowCount(0)
        for i, p in enumerate(e.blocked_queue):
            self.tabla_bloqueados.insertRow(i)
            self.tabla_bloqueados.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.tabla_bloqueados.setItem(i, 1, QTableWidgetItem(str(p.blocked_time)))

        # Proceso en ejecucion
        if e.running_process:
            rp = e.running_process
            marcos = ", ".join(str(m) for m in rp.frames)
            texto = (f"ID: {rp.id}\n"
                     f"Operacion: {rp.operation}\n"
                     f"TME: {rp.tme}\n"
                     f"Tamano: {rp.size}  ({rp.num_pages} paginas)\n"
                     f"Marcos: {marcos}\n\n"
                     f"Tiempo Transcurrido: {rp.time_elapsed}\n"
                     f"Tiempo Restante: {rp.time_remaining}\n"
                     f"Quantum: {rp.quantum_elapsed} / {e.quantum}")
            self.lbl_ejecucion_datos.setText(texto)
        else:
            self.lbl_ejecucion_datos.setText("Ninguno")

        # Terminados (los que terminaron con error se marcan en rojo)
        self.tabla_terminados.setRowCount(0)
        for i, item in enumerate(e.terminated_queue):
            self.tabla_terminados.insertRow(i)
            for col, v in enumerate([item.id, item.operation, item.result]):
                celda = QTableWidgetItem(str(v))
                if item.result == "ERROR":
                    celda.setBackground(QColor("#FFB3BA"))
                    celda.setForeground(QColor("black"))
                self.tabla_terminados.setItem(i, col, celda)

        # Barra de progreso (total dinamico por la tecla N)
        total = e.total_generated if e.total_generated else 1
        porcentaje = int((len(e.terminated_queue) / total) * 100)
        self.barra_progreso.setValue(porcentaje)

        if porcentaje <= 20: color_barra = "#FFB3BA"
        elif porcentaje <= 40: color_barra = "#FFDFBA"
        elif porcentaje <= 60: color_barra = "#FFFFBA"
        elif porcentaje <= 80: color_barra = "#BAE1FF"
        else: color_barra = "#BAFFC9"

        self.barra_progreso.setStyleSheet(
            f"QProgressBar {{ border: 1px solid #777; border-radius: 5px; text-align: center; color: white; background-color: #2b2b2b; }}"
            f"QProgressBar::chunk {{ background-color: {color_barra}; border-radius: 4px; }}"
        )


def main():
    app = QApplication(sys.argv)
    num_procesos, ok = QInputDialog.getInt(None, "Configuracion", "Numero de procesos (N):", value=10, minValue=1, maxValue=100)
    if not ok:
        return

    quantum, ok = QInputDialog.getInt(None, "Configuracion", "Valor del Quantum:", value=4, minValue=1, maxValue=100)
    if ok:
        ventana = MainWindow(num_procesos, quantum)
        ventana.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
