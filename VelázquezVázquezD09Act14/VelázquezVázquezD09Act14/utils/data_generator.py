import random
from models.process import Process


def generate_random_process(process_id: int) -> Process:
    # TME entre 6 y 20
    tme = random.randint(6, 20)

    # Tamano del proceso entre 6 y 26
    size = random.randint(6, 26)

    # Operacion matematica valida (los operandos son >= 1, no hay division entre cero)
    op = random.choice(['+', '-', '*', '/', '%'])
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)

    return Process(id=process_id, operation=f"{num1} {op} {num2}", tme=tme, size=size)
