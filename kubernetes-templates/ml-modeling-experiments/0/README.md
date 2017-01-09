<!-- README FOR RANCHER CATALOG -->
# Lanzador de stacks

### Info:

 Esta template lanza en diferentes stacks los otras plantillas del catalogo. 

### Usage

 Selecciona este stack del catalogo.
 Selecciona la version
 Introduce el parametro en las preguntas:
- **Url de los parametros de configuración**: una url donde se encuentren los parametros de configuracion para las preguntas del stack sobre el que lanzar los experimentos. Debe estar en formato yaml
- **Access-key**: clave de acceso de la API de rancher
- **Secret-key**: clave secreta de la API de rancher

**NOTA IMPORTANTE: Hay que tener en cuenta que las url del rancher y del stack del catalogo tienen que ser accesibles desde nuestro host.**
