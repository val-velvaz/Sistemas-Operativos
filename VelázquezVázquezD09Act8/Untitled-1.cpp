// VARIABLES GLOBALES (Memoria Compartida)
// Estas banderas indican si un hilo (thread) específico tiene la intención
// de entrar a su "sección crítica" (el área de código donde se usan recursos compartidos).
// Además, se agrega una variable de turno para resolver empates sin generar bloqueos.
int favouredthread = 1; // Indica de quién es el turno de prioridad (Hilo 1 o Hilo 2)
boolean thread1wantstoenter = false; // Indica si el Hilo 1 quiere entrar
boolean thread2wantstoenter = false; // Indica si el Hilo 2 quiere entrar

// FUNCIÓN PRINCIPAL (Punto de entrada)
Main() {
    // Inicialmente, se le da la prioridad al Hilo 1 y ningún hilo quiere entrar a la sección crítica.
    favouredthread = 1;
    thread1wantstoenter = false;
    thread2wantstoenter = false;

    // Se lanzan ambos hilos para que comiencen a ejecutarse de manera concurrente (al mismo tiempo).
    startThreads();
}

// HILO 1
Thread1() {
    // El hilo se ejecutará continuamente en este ciclo hasta que una condición externa (completed) sea verdadera.
    do {
        // SECCIÓN DE ENTRADA: El Hilo 1 "levanta la mano" indicando que quiere usar el recurso compartido.
        thread1wantstoenter = true;
        
        // COMPROBACIÓN (Espera Activa): Verifica si el Hilo 2 también quiere entrar al mismo tiempo.
        while (thread2wantstoenter == true) {
            
            // DESEMPATE: Si el Hilo 2 también quiere entrar, verificamos de quién es el turno oficial.
            if (favouredthread == 2) {
                // Si es el turno del Hilo 2, el Hilo 1 es educado y "baja la mano" para ceder el paso...
                thread1wantstoenter = false;
                
                // ...y se queda esperando aquí pasivamente hasta que sea su turno otra vez.
                while (favouredthread == 2);
                
                // Una vez que el Hilo 2 termina y le devuelve el turno, vuelve a "levantar la mano" pidiendo entrar.
                thread1wantstoenter = true;
            }
        }
        
        // SECCIÓN CRÍTICA
        // Si el Hilo 1 llega aquí, significa que el Hilo 2 no quería entrar o que el Hilo 1 ganó el desempate.
        // Puede usar el recurso compartido con total seguridad.
        
        // SECCIÓN DE SALIDA: El Hilo 1 termina su tarea. 
        // Como acto de cortesía, le cede el turno al Hilo 2 y "baja la mano".
        favouredthread = 2;
        thread1wantstoenter = false;
        
    // El ciclo se repite mientras la variable 'completed' sea falsa.
    } while (completed == false)
}

// HILO 2: refleja el comportamiento del Hilo 1
Thread2() {
    do {
        // SECCIÓN DE ENTRADA: El Hilo 2 indica que quiere entrar a la sección crítica.
        thread2wantstoenter = true;
        
        // COMPROBACIÓN: Verifica si el Hilo 1 también quiere entrar.
        while (thread1wantstoenter == true) {
            
            // DESEMPATE: Si el Hilo 1 también quiere entrar, verificamos el turno oficial.
            if (favouredthread == 1) {
                // Si es el turno del Hilo 1, el Hilo 2 baja su bandera temporalmente...
                thread2wantstoenter = false;
                
                // ...y se queda esperando hasta que el Hilo 1 desocupe el recurso.
                while (favouredthread == 1);
                
                // Vuelve a subir la bandera cuando sea su turno.
                thread2wantstoenter = true;
            }
        }
        
        // SECCIÓN CRÍTICA DEL HILO 2
        // Puede usar el recurso compartido con total seguridad.
        
        // SECCIÓN DE SALIDA: El Hilo 2 termina de usar el recurso, le devuelve el turno al Hilo 1 y baja su bandera.
        favouredthread = 1;
        thread2wantstoenter = false;
        
    } while (completed == false)
}