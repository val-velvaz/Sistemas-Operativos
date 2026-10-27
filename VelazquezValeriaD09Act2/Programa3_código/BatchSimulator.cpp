#include "BatchSimulator.hpp"
#include "ScreenRenderer.hpp"
#include "Platform.hpp"
#include <algorithm>

BatchSimulator::BatchSimulator(const Process processes[], int totalProcesses)
    : processes_(processes), totalProcesses_(totalProcesses),
      totalCompleted_(0), globalCounter_(0) {}

void BatchSimulator::run() {
    // Ceil de totalProcesses_ / BATCH_SIZE, para saber cuantos lotes de
    // 5 hacen falta en total (el ultimo lote puede quedar incompleto).
    int totalBatches = (totalProcesses_ + BATCH_SIZE - 1) / BATCH_SIZE;

    for (int batch = 1; batch <= totalBatches; batch++) {
        runBatch(batch, totalBatches);
    }
}

void BatchSimulator::runBatch(int batchNumber, int totalBatches) {
    int batchStartIndex = (batchNumber - 1) * BATCH_SIZE;
    int batchEndIndex = std::min(batchStartIndex + BATCH_SIZE - 1, totalProcesses_ - 1);
    int pendingBatches = totalBatches - batchNumber;

    logCompletion(makeBatchMarker("---- INICIO LOTE " + std::to_string(batchNumber) + " ----"));

    for (int i = batchStartIndex; i <= batchEndIndex; i++) {
        runSingleProcess(i, batchNumber, pendingBatches, batchStartIndex, batchEndIndex);
    }

    logCompletion(makeBatchMarker("---- FIN LOTE " + std::to_string(batchNumber) + " ----"));

    // Redibujo final del lote, ya sin ningun proceso "activo", para que
    // se vea el resumen antes de pasar al siguiente lote.
    draw(batchNumber, totalBatches - batchNumber, batchStartIndex, batchEndIndex, -1, 0, 0);
}

void BatchSimulator::runSingleProcess(int processIndex, int batchNumber, int pendingBatches,
                                        int batchStartIndex, int batchEndIndex) {
    const Process& process = processes_[processIndex];
    int elapsedTime = 0;
    int remainingTime = process.getEstimatedTime();

    // Primer dibujo: el proceso arranca, todavia no paso ni un segundo.
    draw(batchNumber, pendingBatches, batchStartIndex, batchEndIndex,
         processIndex, elapsedTime, remainingTime);

    for (int second = 0; second < process.getEstimatedTime(); second++) {
        Platform::sleepOneSecond();
        globalCounter_++;
        elapsedTime++;
        remainingTime--;

        draw(batchNumber, pendingBatches, batchStartIndex, batchEndIndex,
             processIndex, elapsedTime, remainingTime);
    }

    logCompletion(makeCompletionEntry(batchNumber, process));

    // Redibujo extra para que se alcance a ver el resultado final antes
    // de pasar al siguiente proceso del lote.
    draw(batchNumber, pendingBatches, batchStartIndex, batchEndIndex,
         processIndex, process.getEstimatedTime(), 0);
}

void BatchSimulator::logCompletion(const CompletionEntry& entry) {
    if (totalCompleted_ < MAX_COMPLETED_ENTRIES) {
        completed_[totalCompleted_++] = entry;
    }
    // Si se llega al limite simplemente dejamos de agregar mas
    // entradas; no tiene sentido tronar el programa por esto ya que es
    // solo el historial visual.
}

void BatchSimulator::draw(int batchNumber, int pendingBatches, int batchStartIndex, int batchEndIndex,
                            int currentProcessIndex, int elapsedTime, int remainingTime) const {
    ScreenRenderer::Snapshot snapshot{
        processes_, totalProcesses_,
        batchNumber, pendingBatches,
        batchStartIndex, batchEndIndex,
        currentProcessIndex,
        elapsedTime, remainingTime,
        globalCounter_,
        completed_, totalCompleted_
    };
    ScreenRenderer::render(snapshot);
}
