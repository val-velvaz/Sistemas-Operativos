#include "CompletionLog.hpp"

CompletionEntry makeBatchMarker(const std::string& text) {
    CompletionEntry entry;
    entry.isMarker = true;
    entry.markerText = text;
    return entry;
}

CompletionEntry makeCompletionEntry(int batchNumber, const Process& process) {
    CompletionEntry entry;
    entry.isMarker = false;
    entry.batchNumber = batchNumber;
    entry.processId = process.getId();
    entry.operation = process.getOperation();
    entry.x = process.getX();
    entry.y = process.getY();
    entry.result = process.getResult();
    return entry;
}

std::string completionEntryToLine(const CompletionEntry& entry) {
    if (entry.isMarker) {
        return entry.markerText;
    }

    return "L" + std::to_string(entry.batchNumber) +
           " | Id " + std::to_string(entry.processId) +
           " | " + operationToExpression(entry.operation, entry.x, entry.y) +
           " | " + std::to_string(entry.result);
}
