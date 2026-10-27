#include "InputHelper.hpp"
#include <iostream>
#include <limits>

using std::cin;
using std::cout;
using std::string;

namespace InputHelper {

    int readInt(const string& prompt) {
        int value;
        while (true) {
            cout << prompt;
            if (cin >> value) {
                return value;
            }
            // Si el usuario escribio algo que no es un numero, limpiamos
            // el error y descartamos lo que haya quedado en el buffer
            // antes de volver a preguntar.
            cin.clear();
            cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            cout << "Entrada invalida. Intenta de nuevo.\n";
        }
    }

    int readEstimatedTime() {
        while (true) {
            int time = readInt("Tiempo Maximo Estimado (TME) (>0): ");
            if (time > 0) {
                return time;
            }
            cout << "Error: el TME debe ser mayor a 0.\n";
        }
    }

    Operation readOperationMenu() {
        while (true) {
            int chosen = readInt(
                "\nOperacion a realizar:\n"
                "1) +\n2) -\n3) *\n4) /\n5) % (residuo)\n6) ^ (potencia)\n"
                "Elige una opcion: "
            );
            if (chosen >= 1 && chosen <= 6) {
                return static_cast<Operation>(chosen);
            }
            cout << "Opcion invalida.\n";
        }
    }

    int readSecondOperand(Operation operation) {
        while (true) {
            int y = readInt("Valor de y: ");
            bool divisionEntreCero = (operation == Operation::Division || operation == Operation::Modulo) && y == 0;
            if (divisionEntreCero) {
                cout << "Error: no se permite division/residuo entre 0.\n";
                continue;
            }
            return y;
        }
    }

    bool idAlreadyUsed(const Process processes[], int processCount, int id) {
        for (int i = 0; i < processCount; i++) {
            if (processes[i].getId() == id) {
                return true;
            }
        }
        return false;
    }

    Process captureProcess(const Process processes[], int processCount) {
        int id;
        while (true) {
            id = readInt("Id: ");
            if (!idAlreadyUsed(processes, processCount, id)) {
                break;
            }
            cout << "Error: Id repetido. Ingresa otro.\n";
        }

        // Antes de leer una linea completa con getline hay que limpiar
        // el salto de linea que quedo pendiente del ultimo cin >>.
        cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

        cout << "Nombre de Programador: ";
        string programmerName;
        std::getline(cin, programmerName);

        int estimatedTime = readEstimatedTime();
        Operation operation = readOperationMenu();

        int x = readInt("Valor de x: ");
        int y = readSecondOperand(operation);

        int result = computeResult(operation, x, y);

        return Process(x, y, operation, result, estimatedTime, id, programmerName);
    }

}
