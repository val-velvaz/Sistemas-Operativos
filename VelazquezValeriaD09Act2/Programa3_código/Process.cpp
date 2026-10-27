#include "Process.hpp"

Process::Process()
    : x_(0), y_(0), operation_(Operation::Addition), result_(0),
      estimatedTime_(0), id_(0), programmerName_("") {}

Process::Process(int x, int y, Operation operation, int result,
                   int estimatedTime, int id, const std::string& programmerName)
    : x_(x), y_(y), operation_(operation), result_(result),
      estimatedTime_(estimatedTime), id_(id), programmerName_(programmerName) {}

int Process::getX() const { return x_; }
int Process::getY() const { return y_; }
int Process::getResult() const { return result_; }
Operation Process::getOperation() const { return operation_; }
int Process::getEstimatedTime() const { return estimatedTime_; }
int Process::getId() const { return id_; }
std::string Process::getProgrammerName() const { return programmerName_; }

void Process::setX(int x) { x_ = x; }
void Process::setY(int y) { y_ = y; }
void Process::setOperation(Operation operation) { operation_ = operation; }
void Process::setResult(int result) { result_ = result; }
void Process::setEstimatedTime(int estimatedTime) { estimatedTime_ = estimatedTime; }
void Process::setId(int id) { id_ = id; }
void Process::setProgrammerName(const std::string& programmerName) { programmerName_ = programmerName; }

int computeResult(Operation operation, int x, int y) {
    switch (operation) {
        case Operation::Addition:       return x + y;
        case Operation::Subtraction:    return x - y;
        case Operation::Multiplication: return x * y;
        case Operation::Division:       return x / y;
        case Operation::Modulo:         return x % y;
        case Operation::Power: {
            // Potencia calculada "a mano" con un ciclo, tal como en el
            // original: y multiplicaciones sucesivas de x.
            int power = 1;
            for (int i = 0; i < y; i++) {
                power *= x;
            }
            return power;
        }
        default:
            return 0; // No deberia pasar nunca si el enum se valido bien.
    }
}

std::string operationToExpression(Operation operation, int x, int y) {
    std::string symbol;
    switch (operation) {
        case Operation::Addition:       symbol = "+"; break;
        case Operation::Subtraction:    symbol = "-"; break;
        case Operation::Multiplication: symbol = "*"; break;
        case Operation::Division:       symbol = "/"; break;
        case Operation::Modulo:         symbol = "%"; break;
        case Operation::Power:          symbol = "^"; break;
        default:                        symbol = "?"; break;
    }
    return std::to_string(x) + " " + symbol + " " + std::to_string(y);
}
