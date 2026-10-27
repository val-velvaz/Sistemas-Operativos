#pragma once

#include <string>
#include "Process.hpp"

// Cada entrada del historial de "procesos terminados" puede ser dos
// cosas: o bien un proceso que ya termino de ejecutarse, o bien una
// marca separadora tipo "---- INICIO LOTE 1 ----". Se resuelve con un
// solo struct (en vez de dos tipos distintos) porque ambos casos viven
// mezclados en la misma lista y se imprimen en el mismo lugar.
struct CompletionEntry {
    bool isMarker = false;
    std::string markerText;

    int batchNumber = 0;
    int processId = 0;
    Operation operation = Operation::Addition;
    int x = 0;
    int y = 0;
    int result = 0;
};

// Crea una entrada "marcador", como "---- INICIO LOTE 2 ----".
CompletionEntry makeBatchMarker(const std::string& text);

// Crea una entrada de proceso terminado a partir del lote donde corrio
// y del proceso ya ejecutado.
CompletionEntry makeCompletionEntry(int batchNumber, const Process& process);

// Devuelve la entrada ya formateada como una sola linea de texto, lista
// para imprimirse en la columna de "terminados".
std::string completionEntryToLine(const CompletionEntry& entry);
