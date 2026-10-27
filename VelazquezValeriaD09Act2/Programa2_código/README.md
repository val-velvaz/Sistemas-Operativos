# Simulador de Procesos por Lotes

Reescritura del simulador original, dividida en modulos con una sola
responsabilidad cada uno.

## Estructura

```
include/            Headers (.hpp) de cada modulo
  Platform.hpp       Aisla lo que depende del sistema operativo (Sleep, cls)
  Process.hpp        La clase Process y la logica de operaciones aritmeticas
  InputHelper.hpp     Todo lo relacionado a leer y validar datos del usuario
  CompletionLog.hpp  Representa el historial de procesos terminados
  ScreenRenderer.hpp Dibuja el estado actual en la consola (3 columnas)
  BatchSimulator.hpp Orquesta la ejecucion por lotes de 5 procesos

src/                 Implementacion (.cpp) de cada header
  main.cpp           Punto de entrada: solo captura procesos y arranca la simulacion
```

## Por que esta division

- **Process**: sabe representar un proceso y calcular su resultado, nada mas.
- **InputHelper**: concentra toda la validacion de entradas (ids repetidos,
  division entre cero, opciones fuera de rango, etc). Si un dia cambia la
  forma de capturar datos, solo se toca este archivo.
- **CompletionLog**: modela una entrada del historial (proceso terminado o
  marca de inicio/fin de lote) sin saber nada de como se dibuja en pantalla.
- **ScreenRenderer**: solo sabe pintar. Recibe un `Snapshot` con todo lo que
  necesita mostrar y no toca la logica de la simulacion.
- **BatchSimulator**: es el "director de orquesta": decide el orden de
  ejecucion, avisa cuando un proceso termina, y le pide a ScreenRenderer que
  dibuje en cada momento clave.
- **Platform**: el original dependia directo de `<windows.h>` (Sleep,
  `system("cls")`), lo que ataba el programa a Windows. Aqui se aislan esas
  dos operaciones para que el resto del codigo no dependa del sistema
  operativo; en Windows usa `Sleep`/`cls`, en Linux/Mac usa `usleep`/`clear`.

## Compilar

En Windows (con MinGW o similar) o Linux/Mac:

```bash
g++ -std=c++17 -Wall -Wextra -Iinclude src/*.cpp -o simulador
./simulador          # o simulador.exe en Windows
```
