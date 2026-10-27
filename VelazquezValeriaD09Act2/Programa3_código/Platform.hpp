#pragma once

// Esta capa existe por una sola razon: el codigo original dependia
// directamente de <windows.h> (Sleep, system("cls")), lo que lo dejaba
// atado a Windows. Aqui aislamos esas dos operaciones "sucias" (borrar
// pantalla y esperar un segundo) para que el resto del programa no tenga
// que saber en que sistema operativo esta corriendo.
namespace Platform {

    // Limpia la pantalla de la consola (cls en Windows, clear en Unix).
    void clearScreen();

    // Duerme el hilo actual exactamente un segundo. Se usa para simular
    // el paso del tiempo mientras un proceso "se ejecuta".
    void sleepOneSecond();

}
