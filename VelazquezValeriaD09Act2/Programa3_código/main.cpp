#include <iostream>
#include <limits>
#include "Process.hpp"
#include "InputHelper.hpp"
#include "BatchSimulator.hpp"

using std::cin;
using std::cout;

namespace {
    const int MAX_PROCESSES = 50;
}

int main() {
    Process processes[MAX_PROCESSES];

    int numberOfProcesses = InputHelper::readInt("Ingresa el numero de procesos: ");

    if (numberOfProcesses < 1) {
        cout << "Debe haber al menos 1 proceso.\n";
        return 0;
    }
    if (numberOfProcesses > MAX_PROCESSES) {
        cout << "Maximo permitido: " << MAX_PROCESSES << ". Se ajustara a " << MAX_PROCESSES << ".\n";
        numberOfProcesses = MAX_PROCESSES;
    }

    // Se capturan todos los procesos primero, en el orden en que el
    // usuario los va ingresando.
    for (int i = 0; i < numberOfProcesses; i++) {
        cout << "\n=== Captura del Proceso " << (i + 1) << " ===\n";
        processes[i] = InputHelper::captureProcess(processes, i); // i = ya capturados hasta ahora
    }

    // Con los procesos listos, el BatchSimulator se encarga de correr
    // toda la simulacion por lotes de 5.
    BatchSimulator simulator(processes, numberOfProcesses);
    simulator.run();

    cout << "\nSimulacion terminada. Contador global final: "
         << simulator.getGlobalCounter() << "s\n";

    cout << "Presiona ENTER para salir...";
    cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    cin.get();

    return 0;
}
