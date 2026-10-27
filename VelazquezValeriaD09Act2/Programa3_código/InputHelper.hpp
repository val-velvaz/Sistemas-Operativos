#pragma once

#include <string>
#include "Process.hpp"

// Aqui va TODO lo que tiene que ver con pedirle datos al usuario y
// validarlos. Separar esto del resto tiene una ventaja practica: si un
// dia cambia la forma de leer datos (por ejemplo, se pasa a leer de un
// archivo o de una interfaz grafica), solo se toca este archivo.
namespace InputHelper {

    // Pide un entero mostrando "prompt" y no suelta el control hasta que
    // el usuario escriba algo valido. Es la base de todas las demas
    // funciones de lectura.
    int readInt(const std::string& prompt);

    // Pide el Tiempo Maximo Estimado (TME) y obliga a que sea mayor a 0.
    int readEstimatedTime();

    // Muestra el menu de operaciones (+, -, *, /, %, ^) y devuelve la
    // opcion elegida ya validada.
    Operation readOperationMenu();

    // Pide el segundo operando (y). Si la operacion es division o
    // modulo, no permite que valga 0 (para evitar la clasica division
    // entre cero).
    int readSecondOperand(Operation operation);

    // Revisa si un id ya fue usado por algun proceso ya capturado.
    bool idAlreadyUsed(const Process processes[], int processCount, int id);

    // Junta todas las preguntas necesarias para armar un Process
    // completo: id, nombre del programador, TME, operacion y operandos.
    // "processes" y "processCount" se usan solo para validar que el id
    // no se repita.
    Process captureProcess(const Process processes[], int processCount);

}
