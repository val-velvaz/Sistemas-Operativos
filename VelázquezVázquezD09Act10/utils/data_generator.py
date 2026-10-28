import operator
import random

from config import (OPERADORES, OPERANDO_MAX, OPERANDO_MIN, TME_MAX, TME_MIN)
from models.process import Process

_OPERACIONES = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
}


def generate_random_process(process_id: int) -> Process:
    """Crea un proceso con TME y operacion aleatorios (operandos >= 1, sin division entre cero)."""
    tme = random.randint(TME_MIN, TME_MAX)
    op = random.choice(OPERADORES)
    num1 = random.randint(OPERANDO_MIN, OPERANDO_MAX)
    num2 = random.randint(OPERANDO_MIN, OPERANDO_MAX)
    return Process(id=process_id, operation=f"{num1} {op} {num2}", tme=tme)


def evaluate_operation(operation: str) -> str:
    """Resuelve una operacion con formato 'a <op> b' sin usar eval().
    Regresa el resultado redondeado a 4 decimales o 'ERROR' si no es valida."""
    try:
        a, op, b = operation.split()
        return str(round(_OPERACIONES[op](int(a), int(b)), 4))
    except (ValueError, KeyError, ZeroDivisionError):
        return "ERROR"
