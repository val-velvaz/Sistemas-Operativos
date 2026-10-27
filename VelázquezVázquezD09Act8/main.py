import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                               QHeaderView, QInputDialog, QMessageBox,
                               QProgressBar, QDialog)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from models.simulator import SimulatorEngine


class TablaBCPWindow(QDialog):
    """Ventana emergente que muestra el BCP final con todos los tiempos (al terminar la simulacion)"""
    def __init__(self, procesos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabla de Control de Procesos (BCP) - Final")
        self.resize(1000, 400)

        layout = QVBoxLayout()
        tabla = QTableWidget(len(procesos), 11)
        tabla.setHorizontalHeaderLabels([
            "ID", "Operacion", "Resultado", "TME", "Llegada",
            "Finalizacion", "Retorno", "Respuesta", "Espera", "Servicio", "Terminacion"
        ])

        estilo = """
            QHeaderView::section {
                background-color: #BAE1FF; color: black; font-weight: bold; border: 1px solid #777;
            }
        """
        tabla.setStyleSheet(estilo)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        for i, p in enumerate(procesos):
            tabla.setItem(i, 0, QTableWidgetItem(str(p.id)))
            tabla.setItem(i, 1, QTableWidgetItem(p.operation))
            tabla.setItem(i, 2, QTableWidgetItem(p.result))
            tabla.setItem(i, 3, QTableWidgetItem(str(p.tme)))
            tabla.setItem(i, 4, QTableWidgetItem(str(p.arrival_time)))
            tabla.setItem(i, 5, QTableWidgetItem(str(p.finish_time)))
            tabla.setItem(i, 6, QTableWidgetItem(str(p.return_time)))
            tabla.setItem(i, 7, QTableWidgetItem(str(p.response_time)))
            tabla.setItem(i, 8, QTableWidgetItem(str(p.waiting_time)))
            tabla.setItem(i, 9, QTableWidgetItem(str(p.service_time)))
            tabla.setItem(i, 10, QTableWidgetItem(p.final_status))

        layout.addWidget(tabla)
        self.setLayout(layout)


class TablaProcesosLiveWindow(QDialog):
    """Tecla B: muestra el BCP de TODOS los procesos que existen en ese momento
    (Nuevo, Listo, Ejecucion, Bloqueado y Terminado), con los campos que pide el
    requerimiento 4. Se pausa la simulacion mientras esta abierta y, tal como pide
    el enunciado, unicamente se reanuda (y se cierra la ventana) con la tecla C."""

    COLUMNAS = ["ID", "Estado", "Detalle de Estado", "Operacion y Datos", "Resultado",
                "T. Llegada", "T. Finalizacion", "T. Retorno", "T. Espera (al momento)",
                "T. Servicio (al momento)", "T. Restante en CPU", "T. Respuesta"]

    def __init__(self, procesos, reloj_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Tabla de Procesos (BCP) - Reloj: {reloj_actual}  |  Presiona 'C' para continuar")
        self.resize(1250, 420)
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout()
        aviso = QLabel("<b>Simulacion en pausa.</b> Presiona la tecla 'C' para continuar donde quedo.")
        aviso.setStyleSheet("color: #FFFFBA; padding: 4px;")
        layout.addWidget(aviso)

        tabla = QTableWidget(len(procesos), len(self.COLUMNAS))
        tabla.setHorizontalHeaderLabels(self.COLUMNAS)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setStyleSheet("""
            QHeaderView::section {
                background-color: #BAE1FF; color: black; font-weight: bold; border: 1px solid #777;
            }
        """)

        for fila, p in enumerate(procesos):
            tabla.setItem(fila, 0, QTableWidgetItem(str(p.id)))
            tabla.setItem(fila, 1, QTableWidgetItem(p.status))
            tabla.setItem(fila, 2, QTableWidgetItem(self._detalle_estado(p)))
            tabla.setItem(fila, 3, QTableWidgetItem(p.operation))
            tabla.setItem(fila, 4, QTableWidgetItem(p.result if p.result is not None else "-"))
            tabla.setItem(fila, 5, QTableWidgetItem(self._o_guion(p.arrival_time)))
            tabla.setItem(fila, 6, QTableWidgetItem(self._o_guion(p.finish_time)))
            tabla.setItem(fila, 7, QTableWidgetItem(self._o_guion(p.return_time)))
            tabla.setItem(fila, 8, QTableWidgetItem(self._o_guion(self._espera_actual(p, reloj_actual))))
            tabla.setItem(fila, 9, QTableWidgetItem(str(p.service_time)))
            tabla.setItem(fila, 10, QTableWidgetItem("-" if p.status == "Terminado" else str(p.time_remaining)))
            tabla.setItem(fila, 11, QTableWidgetItem(self._o_guion(p.response_time)))

        tabla.resizeColumnsToContents()
        layout.addWidget(tabla)
        self.setLayout(layout)

    @staticmethod
    def _o_guion(valor):
        return "-" if valor is None else str(valor)

    @staticmethod
    def _detalle_estado(p) -> str:
        """b. Estado del proceso: nulo si es Nuevo, tiempo restante si esta Bloqueado,
        y Normal/Error si esta Terminado."""
        if p.status == "Nuevo":
            return "-"
        if p.status == "Bloqueado":
            return f"Restante en E/S: {8 - p.blocked_time}"
        if p.status == "Terminado":
            return p.final_status
        return "-"

    @staticmethod
    def _espera_actual(p, reloj_actual):
        """g. Tiempo de Espera (al momento): si ya termino, se usa el tiempo de espera final;
        si aun no llega, no aplica; si ya llego pero sigue en el sistema, es el tiempo
        transcurrido desde su llegada menos lo que ya alcanzo a ejecutarse."""
        if p.arrival_time is None:
            return None
        if p.finish_time is not None:
            return p.waiting_time
        return (reloj_actual - p.arrival_time) - p.service_time

    def keyPressEvent(self, event):
        # Tal como pide el enunciado, unicamente la tecla "C" reanuda la simulacion.
        if event.text().upper() == 'C':
            self.accept()
        # Cualquier otra tecla se ignora mientras se observa la tabla.


class MainWindow(QMainWindow):
    # Teclas validas para el simulador -> descripcion mostrada en la barra "vim"
    TECLAS_VALIDAS = {
        'E': "Interrupcion E/S",
        'W': "Error",
        'P': "Pausa",
        'C': "Continuar",
        'N': "Nuevo proceso",
        'B': "Tabla de procesos (BCP)",
    }

    def __init__(self, total_jobs: int):
        super().__init__()
        self.engine = SimulatorEngine(total_jobs)
        self.comandos_habilitados = True  # se desactiva al terminar la simulacion

        self.setWindowTitle("Simulador de SO - Modelo de 5 Estados")
        self.resize(1000, 600)

        self.colores_reloj = ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF"]
        self.indice_color_reloj = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.ciclo_simulacion)

        self.configurar_interfaz()
        self.actualizar_pantalla()

        self.cambiar_estado("Ejecutando", "#BAFFC9")
        self.timer.start(1000)

        # La ventana principal es quien captura las teclas directamente,
        # por eso necesita foco fuerte y ningun otro widget debe robarlo.
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def configurar_interfaz(self):
        widget_central = QWidget()
        layout_principal = QVBoxLayout()

        # --- SECCION SUPERIOR ---
        layout_superior = QHBoxLayout()
        self.lbl_reloj = QLabel("Reloj Global: 0")
        self.lbl_nuevos = QLabel("Procesos Nuevos: 0")
        self.lbl_estado = QLabel("Estado: Iniciando...")

        font = self.lbl_reloj.font()
        font.setBold(True)
        font.setPointSize(12)
        self.lbl_nuevos.setFont(font)
        self.lbl_estado.setFont(font)
        self.lbl_reloj.setFont(font)

        layout_superior.addWidget(self.lbl_nuevos)
        layout_superior.addStretch()
        layout_superior.addWidget(self.lbl_estado)
        layout_superior.addStretch()
        layout_superior.addWidget(self.lbl_reloj)
        layout_principal.addLayout(layout_superior)

        estilo_tablas = """
            QHeaderView::section { background-color: #E0BBE4; color: black; font-weight: bold; border: 1px solid #777; }
            QTableCornerButton::section { background-color: #E0BBE4; border: 1px solid #777; }
        """

        # --- SECCION CENTRAL ---
        layout_central = QHBoxLayout()

        # 1. Tabla de Listos
        layout_listos = QVBoxLayout()
        layout_listos.addWidget(QLabel("Cola de Listos:"))
        self.tabla_listos = QTableWidget(0, 3)
        self.tabla_listos.setHorizontalHeaderLabels(["ID", "TME", "Transcurrido"])
        self.tabla_listos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_listos.setFocusPolicy(Qt.NoFocus)
        self.tabla_listos.setStyleSheet(estilo_tablas)
        layout_listos.addWidget(self.tabla_listos)
        layout_central.addLayout(layout_listos)

        # 2. Centro: Ejecucion, Controles y Bloqueados
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
            "<b>Controles (tecla directa, sin Enter):</b> "
            "<span style='color: #D5AAFF;'>E: E/S</span> | "
            "<span style='color: #FFB3BA;'>W: Error</span> | "
            "<span style='color: #FFFFBA;'>P: Pausa</span> | "
            "<span style='color: #BAFFC9;'>C: Continuar</span> | "
            "<span style='color: #FFDFBA;'>N: Nuevo</span> | "
            "<span style='color: #E0BBE4;'>B: Tabla BCP</span>"
        )
        layout_centro.addWidget(QLabel(texto_controles))

        # --- Barra estilo "vim": muestra la ultima tecla registrada ---
        self.lbl_vim_status = QLabel("> _")
        self.lbl_vim_status.setFont(self._fuente_monoespaciada())
        self.lbl_vim_status.setStyleSheet(self._estilo_barra_vim("#00FF66"))
        layout_centro.addWidget(self.lbl_vim_status)

        layout_central.addLayout(layout_centro)

        # 3. Tabla de Procesos Terminados
        layout_terminados = QVBoxLayout()
        layout_terminados.addWidget(QLabel("Procesos Terminados:"))
        self.tabla_terminados = QTableWidget(0, 3)
        self.tabla_terminados.setHorizontalHeaderLabels(["ID", "Operacion", "Resultado"])
        self.tabla_terminados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_terminados.setFocusPolicy(Qt.NoFocus)
        self.tabla_terminados.setStyleSheet(estilo_tablas)
        layout_terminados.addWidget(self.tabla_terminados)
        layout_central.addLayout(layout_terminados)

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
    # Captura de teclado directa (sin QLineEdit ni Enter, estilo vim)
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if not self.comandos_habilitados:
            return super().keyPressEvent(event)

        tecla = event.text().upper()

        # Ignorar teclas de control/no imprimibles (flechas, Tab, etc.)
        if not tecla or not tecla.isalpha():
            return super().keyPressEvent(event)

        if tecla not in self.TECLAS_VALIDAS:
            # Solo se permiten los estados definidos: E, W, P, C, N, B
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
        """Aplica el efecto de la tecla ya validada sobre el motor de simulacion."""
        if tecla == 'E' and not self.engine.is_paused:
            self.engine.handle_interrupt_io()
            self.cambiar_estado("Interrupcion E/S", "#D5AAFF")
            self.actualizar_pantalla()

        elif tecla == 'W' and not self.engine.is_paused:
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

    def mostrar_tabla_procesos(self):
        """Tecla B: pausa la simulacion (si no lo estaba ya) y muestra el BCP de todos
        los procesos actuales. Con la tecla C dentro de la ventana emergente se cierra
        y la simulacion continua exactamente donde se quedo."""
        estaba_pausado = self.engine.is_paused
        if not estaba_pausado:
            self.engine.pause()
            self.timer.stop()
        self.cambiar_estado("Mostrando tabla de procesos (BCP)", "#E0BBE4")

        procesos = (
            list(self.engine.new_queue)
            + list(self.engine.ready_queue)
            + ([self.engine.running_process] if self.engine.running_process else [])
            + list(self.engine.blocked_queue)
            + list(self.engine.terminated_queue)
        )
        procesos.sort(key=lambda p: p.id)

        dialogo = TablaProcesosLiveWindow(procesos, self.engine.global_clock, self)
        dialogo.exec()

        if not estaba_pausado:
            self.engine.resume()
            self.timer.start(1000)
            self.cambiar_estado("Ejecutando", "#BAFFC9")
        else:
            self.cambiar_estado("Pausado", "#FFFFBA")

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

            # Mostrar la tabla final de BCP (requisito 7)
            dialogo = TablaBCPWindow(self.engine.terminated_queue, self)
            dialogo.exec()

        else:
            if not self.engine.is_paused:
                self.cambiar_estado("Ejecutando", "#BAFFC9")

    def actualizar_pantalla(self):
        color_actual = self.colores_reloj[self.indice_color_reloj]
        self.lbl_reloj.setStyleSheet(f"color: {color_actual};")
        self.lbl_reloj.setText(f"Reloj Global: {self.engine.global_clock}")

        # Requisito 5a: numero de procesos en estado Nuevo (se actualiza al pasar a
        # Listos o al generarse uno nuevo con la tecla "N")
        self.lbl_nuevos.setText(f"Procesos Nuevos: {len(self.engine.new_queue)}")

        self.tabla_listos.setRowCount(0)
        for i, p in enumerate(self.engine.ready_queue):
            self.tabla_listos.insertRow(i)
            self.tabla_listos.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.tabla_listos.setItem(i, 1, QTableWidgetItem(str(p.tme)))
            self.tabla_listos.setItem(i, 2, QTableWidgetItem(str(p.time_elapsed)))

        self.tabla_bloqueados.setRowCount(0)
        for i, p in enumerate(self.engine.blocked_queue):
            self.tabla_bloqueados.insertRow(i)
            self.tabla_bloqueados.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.tabla_bloqueados.setItem(i, 1, QTableWidgetItem(str(p.blocked_time)))

        if self.engine.running_process:
            rp = self.engine.running_process
            texto = (f"ID: {rp.id}\n"
                     f"Operacion: {rp.operation}\n"
                     f"TME: {rp.tme}\n\n"
                     f"Tiempo Transcurrido: {rp.time_elapsed}\n"
                     f"Tiempo Restante: {rp.time_remaining}")
            self.lbl_ejecucion_datos.setText(texto)
        else:
            self.lbl_ejecucion_datos.setText("Ninguno")

        self.tabla_terminados.setRowCount(0)
        for i, item in enumerate(self.engine.terminated_queue):
            self.tabla_terminados.insertRow(i)
            self.tabla_terminados.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.tabla_terminados.setItem(i, 1, QTableWidgetItem(item.operation))
            self.tabla_terminados.setItem(i, 2, QTableWidgetItem(item.result))

        # El total ahora es dinamico: crece cada vez que se genera un proceso con "N"
        total = self.engine.total_generated if self.engine.total_generated else 1
        porcentaje = int((len(self.engine.terminated_queue) / total) * 100)
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

    if ok:
        ventana = MainWindow(num_procesos)
        ventana.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()