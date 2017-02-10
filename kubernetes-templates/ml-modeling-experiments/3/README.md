<!-- README FOR RANCHER CATALOG -->

# Automodeling

**QUIET MODE VERSION**: Only warnings and errors will be printed

### Info:

 This service deploys automatically services from the kubernetes catalog with different combinations specified in a yaml file. The service will launch all the combinations of parameters possible.

### Usage

 It is necessary select properly the parameters in the configuration yaml file. This file has the following format:
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

This configuration yaml file could be in any source in internet. Then we set the parameters for rancher:
- **Url entries**: the url where the config file is located
- **Access-key**: access key for rancher
- **Secret-key**: secret key for rancher
