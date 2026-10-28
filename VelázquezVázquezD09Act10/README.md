# Simulador de SO - Programa 5 (Round-Robin)

Modelo de 5 estados con planificación Round-Robin, máximo 5 procesos en memoria y bloqueo de 8 unidades.
Al iniciar se pide el número de procesos y el valor del Quantum.

## Ejecutar
    pip install -r requirements.txt
    python main.py

## Teclas (captura directa, sin Enter; configurables en config.py)
| Tecla | Acción |
|-------|--------|
| E | Interrupción de E/S: el proceso en ejecución pasa a Bloqueados 8 unidades |
| W | Error: el proceso en ejecución termina con ERROR |
| P / C | Pausa / Continuar |
| N | Nuevo proceso aleatorio |
| B | Tabla de procesos (BCP); se cierra con C |

## Estructura (MVC)
    main.py                        Punto de entrada (pide N y Quantum)
    config.py                      Constantes: memoria, bloqueo, rangos, Quantum, teclas
    models/process.py              BCP (Process) y estados
    models/simulator.py            Motor: planificador a largo plazo y Round-Robin
    utils/data_generator.py        Procesos aleatorios y evaluación segura de operaciones
    views/main_window.py           Ventana principal (dibuja y emite teclas)
    views/dialogs.py               BCP en vivo (tecla B) y BCP final
    views/styles.py                Colores y estilos
    controllers/sim_controller.py  Temporizador, teclas y coordinación
    tests/test_simulator.py        Pruebas del motor (sin interfaz)

## Pruebas
    python -m unittest discover -s tests -t .
