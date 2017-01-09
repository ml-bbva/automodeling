<!-- README FOR DOCKER HUB -->
#ML-MODELING

This is a image used in the ml-modeling tasks. This images will launch several experiments in rancher for a catalog template with different configurations. It is based in the oficial python 3.5.2 image

##Usage

This images is designed to work with rancher so it is easier to manage. However for testing this image you can run it on its own.

To create the a simple container do:
```

```
Then you will need the following things:
1. Url de los parametros de configuración
2. Acces key del rancher
3. Secret key del rancher
4. Url del rancher:
5. Url del stack del catalogo de rancher a lanzar. Esta url hace referencia a la API de rancher. Tendremos que buscar en esta el stack que queremos lanzar en la API. Tendrá la siguiente forma:
`http://url_de_ejemlo_donde_este_tu_rancher/v1-catalog/templates/nombre_del_catalogo:nobre_del_servicio:0`

<!-- TODO: Completar este readme. No es importante por ahora. -->
