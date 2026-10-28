"""Controlador: conecta el motor (modelo) con la ventana (vista).

Es el unico que conoce a los dos: maneja el temporizador, interpreta las teclas
y decide cuando pausar, reanudar o mostrar las tablas.
"""
from PySide6.QtCore import QObject, QTimer

import config
from models.simulator import SimulatorEngine
from views import styles
from views.dialogs import TablaBCPFinalWindow, TablaBCPLiveWindow
from views.main_window import MainWindow


class SimController(QObject):
    def __init__(self, engine: SimulatorEngine, view: MainWindow):
        super().__init__()
        self.engine = engine
        self.view = view
        self.comandos_habilitados = True   # se desactiva al terminar la simulacion

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._ciclo)
        self.view.tecla_presionada.connect(self._on_tecla)

        # Tecla -> accion
        self._acciones = {
            config.TECLA_IO: self._interrupcion_io,
            config.TECLA_ERROR: self._error,
            config.TECLA_PAUSA: self._pausar,
            config.TECLA_CONTINUAR: self._continuar,
            config.TECLA_NUEVO: self._nuevo_proceso,
            config.TECLA_BCP: self._mostrar_bcp,
        }

    def iniciar(self):
        self.view.render(self.engine)
        self._reanudar_timer()

    # ------------------------------------------------------------------
    # Reloj de la simulacion
    # ------------------------------------------------------------------
    def _reanudar_timer(self):
        self.view.set_estado("Ejecutando", styles.COLOR_EJECUTANDO)
        self.timer.start(config.INTERVALO_RELOJ_MS)

    def _ciclo(self):
        sigue_activo = self.engine.tick()
        if not self.engine.is_paused:
            self.view.avanzar_color_reloj()
        self.view.render(self.engine)

        if sigue_activo:
            if not self.engine.is_paused:
                self.view.set_estado("Ejecutando", styles.COLOR_EJECUTANDO)
            return
        self._finalizar()

    def _finalizar(self):
        self.timer.stop()
        self.comandos_habilitados = False
        self.view.set_estado("Terminado", styles.COLOR_TERMINADO)
        self.view.marcar_finalizada()
        # BCP final con todos los procesos (la ventana mantiene la pantalla para observar)
        procesos = sorted(self.engine.terminated_queue, key=lambda p: p.id)
        TablaBCPFinalWindow(procesos, self.view).exec()

    # ------------------------------------------------------------------
    # Teclado
    # ------------------------------------------------------------------
    def _on_tecla(self, tecla: str):
        if not self.comandos_habilitados:
            return
        if tecla not in config.TECLAS_VALIDAS:
            self.view.mostrar_tecla(f"> {tecla}  (tecla no valida)", valida=False)
            return
        self.view.mostrar_tecla(f"> {tecla}  -  {config.TECLAS_VALIDAS[tecla]}", valida=True)
        self._acciones[tecla]()

    def _interrupcion_io(self):
        if not self.engine.is_paused:
            self.engine.handle_interrupt_io()
            self.view.set_estado("Interrupcion E/S", styles.COLOR_IO)
            self.view.render(self.engine)

    def _error(self):
        if not self.engine.is_paused:
            self.engine.handle_error()
            self.view.set_estado("Error", styles.COLOR_ERROR)
            self.view.render(self.engine)

    def _pausar(self):
        self.engine.pause()
        self.timer.stop()
        self.view.set_estado("Pausado", styles.COLOR_PAUSADO)

    def _continuar(self):
        if self.engine.is_paused:
            self.engine.resume()
            self._reanudar_timer()

    def _nuevo_proceso(self):
        self.engine.request_new_process()
        self.view.set_estado("Nuevo proceso generado", styles.COLOR_NUEVO)
        self.view.render(self.engine)

    def _mostrar_bcp(self):
        """Tecla B: pausa, muestra el BCP de todos los procesos y, al cerrarlo con C,
        reanuda solo si la simulacion no estaba ya pausada con P."""
        estaba_pausado = self.engine.is_paused
        if not estaba_pausado:
            self.engine.pause()
            self.timer.stop()
        self.view.set_estado("Mostrando tabla de procesos (BCP)", styles.COLOR_BCP)

        TablaBCPLiveWindow(self.engine.get_all_processes(),
                           self.engine.global_clock, self.view).exec()

        if estaba_pausado:
            self.view.set_estado("Pausado", styles.COLOR_PAUSADO)
        else:
            self.engine.resume()
            self._reanudar_timer()
