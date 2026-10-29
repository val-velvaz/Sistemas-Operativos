"""Dibuja el contenedor: 18 casillas numeradas, su contenido y la posicion
del productor (P) y del consumidor (C)."""
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from views import styles


class ContainerWidget(QWidget):
    COLUMNAS = 9

    def __init__(self, capacidad: int, parent=None):
        super().__init__(parent)
        self.capacidad = capacidad
        self.casillas = [None] * capacidad
        self.pos_productor = 0
        self.pos_consumidor = 0
        self.dentro = None
        self.ultima_productor = None
        self.ultima_consumidor = None
        self.setMinimumHeight(260)

    def actualizar(self, sim):
        b = sim.buffer
        self.casillas = list(b.casillas)
        self.pos_productor = b.entrada
        self.pos_consumidor = b.salida
        self.dentro = sim.dentro
        self.ultima_productor = sim.productor.ultima_casilla if sim.dentro == "Productor" else None
        self.ultima_consumidor = sim.consumidor.ultima_casilla if sim.dentro == "Consumidor" else None
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        filas = (self.capacidad + self.COLUMNAS - 1) // self.COLUMNAS
        margen = 10
        alto_marca = 22
        ancho = (self.width() - 2 * margen) / self.COLUMNAS
        alto_fila = (self.height() - 2 * margen) / filas
        lado = min(ancho, alto_fila - 2 * alto_marca) - 8

        f_num = QFont(p.font()); f_num.setPointSize(9); f_num.setBold(True)
        f_elem = QFont(p.font()); f_elem.setPointSize(int(max(10, lado / 3.2))); f_elem.setBold(True)
        f_marca = QFont(p.font()); f_marca.setPointSize(9); f_marca.setBold(True)

        for i in range(self.capacidad):
            fila, col = divmod(i, self.COLUMNAS)
            cx = margen + col * ancho + ancho / 2
            y0 = margen + fila * alto_fila + alto_marca
            caja = QRectF(cx - lado / 2, y0, lado, lado)

            lleno = self.casillas[i] is not None
            p.setPen(QPen(QColor("#777777"), 2))
            p.setBrush(QColor(styles.COLOR_CASILLA_LLENA if lleno else styles.COLOR_CASILLA_VACIA))
            if i == self.ultima_productor:
                p.setPen(QPen(QColor(styles.COLOR_PRODUCTOR), 4))
            if i == self.ultima_consumidor:
                p.setPen(QPen(QColor(styles.COLOR_CONSUMIDOR), 4))
            p.drawRoundedRect(caja, 6, 6)

            # numero de casilla (1..18)
            p.setFont(f_num)
            p.setPen(QColor("#CCCCCC"))
            p.drawText(QRectF(caja.x(), caja.bottom() + 2, lado, alto_marca - 4),
                       Qt.AlignCenter, str(i + 1))

            # contenido
            if lleno:
                p.setFont(f_elem)
                p.setPen(QColor("black"))
                p.drawText(caja, Qt.AlignCenter, self.casillas[i])

            # marcas de posicion: P = siguiente casilla del productor, C = del consumidor
            p.setFont(f_marca)
            marcas = []
            if i == self.pos_productor:
                marcas.append(("P", styles.COLOR_PRODUCTOR))
            if i == self.pos_consumidor:
                marcas.append(("C", styles.COLOR_CONSUMIDOR))
            for k, (txt, color) in enumerate(marcas):
                w = 20
                x = cx - (len(marcas) * w) / 2 + k * w
                r = QRectF(x, y0 - alto_marca + 1, w - 2, alto_marca - 4)
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(color))
                p.drawRoundedRect(r, 4, 4)
                p.setPen(QColor("black"))
                p.drawText(r, Qt.AlignCenter, txt)
        p.end()
