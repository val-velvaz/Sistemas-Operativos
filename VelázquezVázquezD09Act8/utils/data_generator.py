 
import random
from models.process import Process

def generate_random_process(process_id: int) -> Process:
    # Generar TME entre 5 y 20
    tme = random.randint(5, 20)
    
    # Generar operación matemática válida
    operators = ['+', '-', '*', '/', '%']
    op = random.choice(operators)
    
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    
    # Validar división o residuo entre cero
    if op in ['/', '%'] and num2 == 0:
        num2 = 1 
        
    operation_str = f"{num1} {op} {num2}"
    
    return Process(id=process_id, operation=operation_str, tme=tme)