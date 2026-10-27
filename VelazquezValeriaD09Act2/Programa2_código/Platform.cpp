#include "Platform.hpp"
#include <cstdlib>

#if defined(_WIN32)
    #include <windows.h>
#else
    #include <unistd.h>
#endif

namespace Platform {

    void clearScreen() {
#if defined(_WIN32)
        system("cls");
#else
        system("clear");
#endif
    }

    void sleepOneSecond() {
#if defined(_WIN32)
        Sleep(1000); // Sleep en Windows recibe milisegundos
#else
        usleep(1000000); // usleep recibe microsegundos
#endif
    }

}
