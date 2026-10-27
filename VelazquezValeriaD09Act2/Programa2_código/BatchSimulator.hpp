#pragma once

#include "Process.hpp"
#include "CompletionLog.hpp"

// Esta clase es la que "orquesta" la simulacion: agarra la lista de
// procesos ya capturados y los va corriendo de a lotes de 5, dibujando
// la pantalla en cada segundo que pasa. Es basicamente el ciclo
// principal que antes vivia suelto dentro de main().
class BatchSimulator {
public:
    BatchSimulator(const Process processes[], int totalProcesses);

    // Corre la simulacion completa, lote por lote, hasta terminar todos
    // los procesos.
    void run();

    // Cuantos segundos en total paso corriendo toda la simulacion.
    // Sirve para el mensaje final que se muestra al usuario.
    int getGlobalCounter() const { return globalCounter_; }

private:
    static const int MAX_COMPLETED_ENTRIES = 200;
    static const int BATCH_SIZE = 5;

    const Process* processes_;
    int totalProcesses_;

    CompletionEntry completed_[MAX_COMPLETED_ENTRIES];
    int totalCompleted_;
    int globalCounter_;

    // Corre un lote completo (hasta 5 procesos).
    void runBatch(int batchNumber, int totalBatches);

    // Corre un solo proceso dentro de un lote, segundo a segundo,
    // redibujando la pantalla en cada tick.
    void runSingleProcess(int processIndex, int batchNumber, int pendingBatches,
                           int batchStartIndex, int batchEndIndex);

    // Agrega una entrada al historial de terminados (proceso o marca de
    // inicio/fin de lote), cuidando no pasarse del limite del arreglo.
    void logCompletion(const CompletionEntry& entry);

    // Arma el snapshot que necesita el ScreenRenderer y lo manda a
    // dibujar. Evita repetir la construccion del struct en cada punto
    // donde se necesita refrescar pantalla.
    void draw(int batchNumber, int pendingBatches, int batchStartIndex, int batchEndIndex,
              int currentProcessIndex, int elapsedTime, int remainingTime) const;
};
