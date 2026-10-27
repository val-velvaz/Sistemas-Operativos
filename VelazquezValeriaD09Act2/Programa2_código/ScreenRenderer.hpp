#pragma once

#include <string>
#include "Process.hpp"
#include "CompletionLog.hpp"

// Agrupa todo lo relacionado con "pintar" el estado actual de la
// simulacion en la consola, en tres columnas: lote en ejecucion,
// proceso en ejecucion, y procesos terminados. Al vivir en su propia
// clase, si mas adelante se quiere cambiar el look (otra libreria de
// consola, una interfaz grafica, etc) solo hay que tocar este archivo.
class ScreenRenderer {
public:
    // snapshot es simplemente "todo lo que se necesita saber para
    // dibujar la pantalla en este instante". Se agrupa en un struct para
    // no tener que pasar diez parametros sueltos de un lado a otro.
    struct Snapshot {
        const Process* processes;
        int totalProcesses;

        int currentBatch;
        int pendingBatches;
        int batchStartIndex;
        int batchEndIndex;
        int currentProcessIndex; // -1 si no hay proceso corriendo ahora

        int elapsedTime;
        int remainingTime;
        int globalCounter;

        const CompletionEntry* completed;
        int totalCompleted;
    };

    static void render(const Snapshot& snapshot);

private:
    static const int MAX_ROWS = 25;
    static const int COLUMN_1_WIDTH = 30;
    static const int COLUMN_2_WIDTH = 45;
    static const int COLUMN_3_WIDTH = 55;

    static void buildPendingBatchColumn(const Snapshot& snapshot, std::string rows[], int& rowCount);
    static void buildCurrentProcessColumn(const Snapshot& snapshot, std::string rows[], int& rowCount);
    static void buildCompletedColumn(const Snapshot& snapshot, std::string rows[], int& rowCount);
    static void printHeader();
    static void printRows(const std::string col1[], const std::string col2[], const std::string col3[]);
};
