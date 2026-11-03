#  DISCOS 
Los discos eran muy populares anteriormente, sin embargo se ha ido remplazado su uso a favor de otras tecnologías. Actualmente se opta más por plataformas de streaming.
Para entender este tena hay que reconocer los motivos del porque los HDD son más lentos que el SSD:

* Platos giratorios: los datos se guardan en discos magnéticos que giran a 5,400 o 7,200 RPM. Para leer algo, hay que esperar a que el plato gire hasta la posición correcta (latencia rotacional).
* Cabezal de lectura/escritura: un brazo mecánico debe moverse físicamente hasta la pista donde están los datos (tiempo de búsqueda o seek time). Esto toma varios milisegundos, mientras que un SSD accede en microsegundos.
* Acceso aleatorio deficiente: si los archivos están en lugares distintos del disco (como cuando arranca el sistema operativo o abres muchos programas), el cabezal tiene que saltar de un lado a otro constantemente. Es aquí donde la diferencia se nota más.
* Fragmentación: cuando un archivo está partido en pedazos dispersos, el cabezal tiene que recorrer más trayecto para juntarlos. 
* En un SSD esto casi no importa porque cualquier celda se accede igual de rápido.
* Un solo punto de lectura a la vez: el HDD solo puede leer desde una posición del disco en cada momento, mientras que un SSD tiene varios chips y canales que trabajan en paralelo.
* Inercia física: los platos y el brazo tardan en acelerar, frenar y estabilizarse, algo que no existe en una memoria sin partes móviles.

# CONCEPTOS DEL DISCO DURO
* Sector 512 bytes: Todos los sectores tiene la misma capacidad
* Pista: El número de sectores en una pista es uniforme
* Disco
* Cilindro
* Cara

## Capacidades de cada componente
Si quieres calcular capacidades
* Capacidad de una pista: num de sectores por pista X capacidad de un sector
* Capacidad de un cilindro: Num de pistas por cilindro X capacidad de una pista 
* Capacidad de un disco

# Parámetros de rendimiento
1. Tiempo de búsqueda: tiempo que se tarda en ubicar la cabeza en la pista
2. Retardo de giro/latencia de giro: Tiempo que tarda el comienzo del sector en llegar hasta la cabeza
3. Tiempo de acces: Suma de tiempo de búsqueda y retardo de giro
4. Capacidad de disco: Cilindro*pista*sectores¨

# Traslape y destraslape
Cuando hablamos de información
## Con Traslape
Puede generar fragmentación de memoria

10 registros, los registros son de longitud fija de 300 bytes
300 * 10 / 512 = 6 aprox

## Factor de intercalacion
Los sectores no necesariamente están continuos.
El factor de intercalación es un número que indica cuanta distancia hay entre sectores que son lógicamente continuos. La información está limitada al tamaño del buffer. Los sectores no están físicamente adyacentes

## Factor de bloque
Número de registros que caben en un bloque.

## Planificación
El SO es el responsable de usar el HW de forma eficiente. El tiempo de acceso se basa en búsqueda y latencia.

# ALGORITMOS DE PLANIFICACION
## FIFO (FCFS)
// COMPLETAR
## SSTF (PRIMERO EL MAS CORTO)
Se eligen las solicitudes de E/S a disco que requiere el menor movimiento posible del brazo del disco desde su posición actual, Puede causar inanisión

## SCAN (ASCENSOR)
El brazo solo se puede mover en un sentido, resolviendo todas las peticiones pendientes de su ruta, hasta que alcance la última pista.

## C-SCAN (ASCENSOR CICLICO)
Es una variante del ascensor, restringe el acceso en una sola dirección. Trata a los cilindros como si fuese una lista circular

## Algoritmo de prioridades
Cada proceso esta asociado a una prioridad