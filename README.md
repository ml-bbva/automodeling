<!-- README FO GIT HUB TODO: Actualizar para kubernetes TODO: Translate to english -->
# Lanzador de Stacks

Este proyecto servirá para las tareas de ml-modeling. El objetivo actual es lanzar varias instancias de varios stacks registrados en el catalogo de rancher con diferentes configuraciones que se darán mediante una lista.

Este repositorio tiene dos partes diferenciadas:
* Carpeta service: donde se aloja el script de python y su correspondiente dockerizacion.
* Carpeta templates: la carpeta que añadirá este proyecto como stack del catalogo de rancher para que se pueda lanzar desde ahi.


## Getting Started

El programa esta pensado para ser lanzado como un stack de rancher desde el catalogo.
En primer lugar debemos añadir a nuestro rancher como catalogo este repositorio. De esta forma tendremos acceso al servicio desde el catalogo.
A continuación, entraremos en nuestro catalogo y seleccionamos este stack. Debemos elegir la version (version actual: v0.1) y se solicitará, además del la clave de acceso (Access-Key) y la clave secreta (Secret-Key) de la API a la que se va a acceder, la URL donde se encuentran los parámetros de configuración, en formato YAML, con los que se desea arrancar el servicio. Estos parámetros son:

1. time_stop: tiempo de vida de los stacks que va a lanzar el servicio
2. limit_stacks: número máximo de stacks que deben estar ejecutandose al mismo tiempo
3. stacks_catalog: lista YAML en la que se deben insertar cada uno de los stacks de catalogo que se desee ejecutar

Dentro de cada uno de los stacks de catalogo a lanzar, se deben especificar los siguientes parámetros:

1. CATALOG1: a sustituir por el nombre que queramos darle al stack
2. URL_API: dirección de la API del stack a arrancar, donde se encuentra el docker compose. Debe tener la siguiente forma: `http://url_de_ejemlo_donde_este_tu_rancher/v1-catalog/templates/nombre_del_catalogo:nobre_del_servicio:0`
3. URL_RANCHER: dirección base de rancher
4. PARAMS: lista YAML donde se especifican los parametros que se van a usar

Dentro de PARAMS, se debe registrar una lista con el nombre de los parametros y el rango de valores a lanzar, señalando lo siguiente:

1. param1: a sustituir por el nombre del parametro del stack concreto a lanzar
2. type: tipo de dato (absolute o lineal)
3. param: lista con el rango de parámetros del param1

Un modelo de YAML de configuración sería el siguiente:

	time_stop: 30.0
	limit_stacks: 4
	stacks_catalog:
	  CATALOG1:
	    URL_API: http://200.95.5.6:8080/v1-catalog/templates/impresionParams:app:0
	    URL_RANCHER: http://200.95.5.6:8080/
	    PARAMS:
	      param1:
	          type: absolute
	          param:
	            - Hola
	            - Buenos Dias
	      param2:
	          type: lineal
	          initial-value: 0
	          final-value: 4
	          interval: 2


#### NOTA IMPORTANTE: Hay que tener en cuenta que las url del rancher y del stack del catalogo tienen que ser accesibles desde nuestro host.

Tras esto ya se puede lanzar nuestro stack

## Dockerizacion python script

En la carpeta service tenemos la dockerizacion del script en python con todo lo necesario para convertirlo en un container independiente que lance servicios. La carpeta contiene tando el programa python como el Dockerfile que se usa para construir la imagen. En la carpeta exec se encuentran los ejecutables del rancherCLI y el rancher-compose. Estos son los de la version para linux.

### Pruebas del script individuales

Si se quiere probar el funcionamiento del script individualmente se debe tener en cuenta que este recibe un dos argumentos:
* La url de las entradas.
* El Acces-Key
* El Secret-Key
El comando tendría la siguiente forma:

```
python lanzadorServicios.py http://iibanezm.neocities.org/modeloYAML.txt anlsdjghq89tqjnjnad ertyuikmnbvgchQWG1394141423jndfkcnq
```

## Template para el catalogo

En la carpeta service es donde almacenamos todo lo referente al catalogo que saldrá en nuestro rancher. Tendremos que agregar este repositorio al nuestro rancher y saldrá el servicio de ml-modeling-experiments. Contiene todo lo necesario para que se muestre correctamente.
