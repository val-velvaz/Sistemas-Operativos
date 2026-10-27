#pragma once

#include <string>

// Representa cada una de las operaciones aritmeticas que un proceso puede
// pedir. Usar un enum en vez de numeros sueltos (1, 2, 3...) evita el
// clasico "numero magico" y hace que el codigo se explique solo:
// Operation::Addition es mucho mas claro que un simple "1".
enum class Operation {
    Addition       = 1,
    Subtraction    = 2,
    Multiplication = 3,
    Division       = 4,
    Modulo         = 5,
    Power          = 6
};

// Un Process es la unidad basica que el simulador maneja: guarda los
// datos que el usuario capturo (operandos, operacion, tiempo estimado)
// y el resultado ya calculado.
class Process {
public:
    Process();
    Process(int x, int y, Operation operation, int result,
             int estimatedTime, int id, const std::string& programmerName);

    // --- Getters ---
    int getX() const;
    int getY() const;
    int getResult() const;
    Operation getOperation() const;
    int getEstimatedTime() const;
    int getId() const;
    std::string getProgrammerName() const;

    // --- Setters ---
    void setX(int x);
    void setY(int y);
    void setOperation(Operation operation);
    void setResult(int result);
    void setEstimatedTime(int estimatedTime);
    void setId(int id);
    void setProgrammerName(const std::string& programmerName);

private:
    int x_;
    int y_;
    Operation operation_;
    int result_;
    int estimatedTime_;
    int id_;
    std::string programmerName_;
};

// Calcula el resultado de aplicar "operation" sobre x e y. Se separa de la
// clase Process porque es una operacion pura (no necesita estado interno),
// asi que tiene mas sentido como funcion libre que como metodo.
int computeResult(Operation operation, int x, int y);

// Devuelve la operacion como texto legible, por ejemplo "5 + 3".
// Sirve tanto para mostrar el proceso en pantalla como en el historial
// de terminados.
std::string operationToExpression(Operation operation, int x, int y);
