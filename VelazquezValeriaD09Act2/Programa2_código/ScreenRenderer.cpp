#include "ScreenRenderer.hpp"
#include "Platform.hpp"
#include <iostream>
#include <iomanip>

using std::cout;
using std::string;
using std::setw;
using std::left;

void ScreenRenderer::render(const Snapshot& snapshot) {
    Platform::clearScreen();

    printHeader();

    string col1[MAX_ROWS];
    string col2[MAX_ROWS];
    string col3[MAX_ROWS];
    int col1Count = 0;
    int col2Count = 0;
    int col3Count = 0;

    buildPendingBatchColumn(snapshot, col1, col1Count);
    buildCurrentProcessColumn(snapshot, col2, col2Count);
    buildCompletedColumn(snapshot, col3, col3Count);

    printRows(col1, col2, col3);
}

void ScreenRenderer::printHeader() {
    cout << left
         << setw(COLUMN_1_WIDTH) << "LOTE EN EJECUCION"
         << setw(COLUMN_2_WIDTH) << "PROCESO EN EJECUCION"
         << setw(COLUMN_3_WIDTH) << "PROCESOS TERMINADOS"
         << "\n";

    cout << left
         << setw(COLUMN_1_WIDTH) << "Nombre | TME"
         << setw(COLUMN_2_WIDTH) << "Detalle"
         << setw(COLUMN_3_WIDTH) << "Lote | Id | Operacion | Resultado"
         << "\n";

    cout << string(COLUMN_1_WIDTH + COLUMN_2_WIDTH + COLUMN_3_WIDTH, '-') << "\n";
}

void ScreenRenderer::buildPendingBatchColumn(const Snapshot& snapshot, string rows[], int& rowCount) {
    rowCount = 0;
    rows[rowCount++] = "Lotes pendientes: " + std::to_string(snapshot.pendingBatches);
    rows[rowCount++] = "Lote en ejecucion: " + std::to_string(snapshot.currentBatch);
    rows[rowCount++] = "";

    // Los procesos "pendientes" del lote son los que van despues del que
    // esta corriendo ahora mismo, hasta el final del lote.
    int firstPendingIndex = snapshot.currentProcessIndex + 1;
    if (firstPendingIndex < snapshot.batchStartIndex) {
        firstPendingIndex = snapshot.batchStartIndex;
    }

    for (int i = firstPendingIndex;
         i <= snapshot.batchEndIndex && i < snapshot.totalProcesses && rowCount < MAX_ROWS;
         i++) {
        const Process& p = snapshot.processes[i];
        rows[rowCount++] = p.getProgrammerName() + " | " + std::to_string(p.getEstimatedTime());
    }
}

void ScreenRenderer::buildCurrentProcessColumn(const Snapshot& snapshot, string rows[], int& rowCount) {
    rowCount = 0;

    bool hayProcesoCorriendo = snapshot.currentProcessIndex >= 0 &&
                                snapshot.currentProcessIndex < snapshot.totalProcesses;

    if (!hayProcesoCorriendo) {
        rows[rowCount++] = "Sin proceso en ejecucion.";
        rows[rowCount++] = "Contador global: " + std::to_string(snapshot.globalCounter);
        return;
    }

    const Process& p = snapshot.processes[snapshot.currentProcessIndex];
    rows[rowCount++] = "ID: " + std::to_string(p.getId());
    rows[rowCount++] = "Nombre: " + p.getProgrammerName();
    rows[rowCount++] = "Operacion: " + operationToExpression(p.getOperation(), p.getX(), p.getY());
    rows[rowCount++] = "TME: " + std::to_string(p.getEstimatedTime());
    rows[rowCount++] = "Tiempo transcurrido: " + std::to_string(snapshot.elapsedTime);
    rows[rowCount++] = "Tiempo restante: " + std::to_string(snapshot.remainingTime);
    rows[rowCount++] = "Contador global: " + std::to_string(snapshot.globalCounter);

    if (snapshot.remainingTime == 0) {
        rows[rowCount++] = "Resultado: " + std::to_string(p.getResult());
    } else {
        rows[rowCount++] = "Resultado: (pendiente)";
    }
}

void ScreenRenderer::buildCompletedColumn(const Snapshot& snapshot, string rows[], int& rowCount) {
    rowCount = 0;

    // Como la columna solo tiene MAX_ROWS lugares, si ya hay mas
    // entradas terminadas que espacio disponible, simplemente mostramos
    // las mas recientes (nos "recorremos" hacia el final de la lista).
    int start = 0;
    if (snapshot.totalCompleted > (MAX_ROWS - 1)) {
        start = snapshot.totalCompleted - (MAX_ROWS - 1);
    }

    for (int i = start; i < snapshot.totalCompleted && rowCount < MAX_ROWS; i++) {
        rows[rowCount++] = completionEntryToLine(snapshot.completed[i]);
    }
}

void ScreenRenderer::printRows(const string col1[], const string col2[], const string col3[]) {
    for (int row = 0; row < MAX_ROWS; row++) {
        cout << left
             << setw(COLUMN_1_WIDTH) << col1[row]
             << setw(COLUMN_2_WIDTH) << col2[row]
             << setw(COLUMN_3_WIDTH) << col3[row]
             << "\n";
    }
}
