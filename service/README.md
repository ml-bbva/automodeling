<!-- README FOR DOCKER HUB -->

# Automodeling

This is a image used in the ml-modeling tasks. This images will launch several experiments in kubernetes and rancher for a catalog template with different configurations. It is based in the official python 3.5.2 image

## Usage

This images is designed to work with rancher so it is easier to manage. However for testing this image you can run it on its own.

You can create a container, and execute the following command. The first parameter for 'lanzadorServicios.py' is the url with the parameters to test, the second one is the rancher access key, and the last one the secret key:
```
python lanzadorServicios.py http://url_parameters.text access-key secret-key
```


### Parameters File

It is necessary select properly the parameters in the configuration yaml file. This file could be in any source in internet. It has the following format:
```
   time_out: 30.0
   limit_stacks: 4
   stacks_catalog:
     CATALOG1:
       URL_API: http://your-rancher-url/v1-catalog/templates/your-catalog:kubernetes*your-service:0
       URL_RANCHER: https://your-rancher-url:80/r/projects/1a8238/kubernetes
       PARAMS:
         param1:
             type: absolute
             param:
               - Hello
               - Good Morning
         param2:
             type: lineal
             initial-value: 0
             final-value: 4
             interval: 2
```

You have to specified the following parameters:
- **time_out**: The time limit for the experiments to run.
- **limit_stacks**: The limit for the maximum amount of experiments running at the same time.
- **stacks_catalog**: Here you have to specify the different services to launch and the parameters for the services. First you gave a name to the catalog to launch. In this example we set this as CATALOG1, but it can be anything. Then you specified for that catalog the following parameters:
   - **URL_API**: This is the url in which is located the template of the service to launch. You have to seek this url in the Rancher API. It should have this form: `http://your-rancher-url/v1-catalog/templates/your-catalog:kubernetes*your-service:0`
   - **URL_RANCHER**: This is the url where your rancher is located. In that rancher direction is where the experiments is going to be launched. This should have the following form: `https://your-rancher-url:80/r/projects/1a8238/kubernetes`
   - **PARAMS**: here you have to specify the parameters for the experiment to try and launch. Notice that this service will try all the combinations possible between the parameters. Also is very important that the names of this parameters are exactly the same as they are in the service's rancher-compose file. Otherwise it won't work. You can specified different two different types of parameters. In the example you can see both of these types:
       - lineal: for lineal increments
       - absolute: for a concrete values or strings

**IMPORTANT NOTE: The URL_API and de URL_RANCHER has to be accessible from our host.**
