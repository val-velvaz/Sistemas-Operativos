# Programa 6 - Productor-Consumidor

Un productor y un consumidor comparten un contenedor circular de 18 casillas.
Duermen tiempos aleatorios; al despertar intentan entrar. Solo uno puede estar
dentro a la vez; el productor necesita espacio y el consumidor necesita producto.
En cada entrada procesan de 3 a 6 elementos, en orden y dando la vuelta de la casilla 18 a la 1.

## Ejecutar
    pip install -r requirements.txt
    python main.py

ESC termina el programa.

## Estructura
    main.py                         Punto de entrada
    config.py                       Capacidad, rangos de elementos y de sueño, productos
    models/buffer.py                Contenedor circular acotado
    models/simulation.py            Estados de productor y consumidor, exclusión mutua
    views/container_widget.py       Dibujo del contenedor numerado
    views/main_window.py            Paneles, mensajes y tecla ESC
    controllers/sim_controller.py   Reloj (QTimer) y fin con ESC
    tests/test_simulation.py        Pruebas del modelo

## Pruebas
    python -m unittest discover -s tests -t .
