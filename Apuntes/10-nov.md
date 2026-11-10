# Explicación del Programa 8
Se realizó una modificación del programa en moodle.
* Practicar a los procesos suspendidos. Se caracterizaon por no estar en la memoria principal sino en el disco.
* En el lado de bloqueados vamos a agregar dos teclas más S y R, Suspendido y 
* Suspendido: Solo va a hacer algo si tengo procesos bloqueados previamente, sino no pasa nada. Se necesita tener procesos bloqueados. Por cada S que presione uno de bloqueado se va a suspendido. Hay que revisar si entra en nuevo. Sacarlos, los frames que ocupaban se limpian.
    * A dónde se van: Representamos esta parte con un archivo que se va al disco y que cuando quiera abrirlo se pueda. Pausar el programa y que el archivo esté ahí con los datos actualizados, con que tenga el ID del proceso suspendido, idealmente toda la información del proceso. Porque se supone que la información del proceso ya no está en memoria, sino en el disco, por lo que debería de mostrar toda la información necesaria. El archivo debe de estar acorde a la información en pantalla. 
* Hay que agregar el tamaño del siguiente a ingresar, esto aplica también a los nuevos procesos. Tenemos en pantalla toda la memoria ya trazada, pero en los frames pueden estar disponibles, y puede quedar la pregunta de ¿porque están vacíos si tengo frames disponibles?. Lo mismo aplica para los suspendidos, a un lado del suspendido hay que poner el tamaño del siguiente
* R es para regresar, hay que verificar si existen los frames necesarios para que regrese.
* Visualmente del programa 7 al 8, lo único que cambia es la etiqueta de suspendidos, y las teclas S y R.
*  Ese archivo debe de estar actualizandose.
* El manejo de archivos puede ser libre con la condición de que se pueda abrir.
* Desplegar el número de procesos en suspendido
* Con la tecla T (lo que no mostraste en la tabla de páginas), aquí los suspendidos habría de mostrarse con esa etiqueta de suspendido, lo mismo pasa con la tecla B, muestras todos los tiempos al momento y lo que aplique, hay que mostrar los datos de los suspendidos que apliquen.
* Mostrar el tiempo que se está incrementando -> Espera
* Lllegada + Espera + Servicio = Contador global
* Programa termina cuando todos los procesos hayan finalizado 

# Fechas
* 11 de dic fecha limite de ordinario
* Esta materia no tiene extraordinario
* Este programa máximo inicios de diciembre
* El examen es aprox el 27 de nov