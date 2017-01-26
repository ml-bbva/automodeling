<!-- README FO GIT HUB -->

# Automodeling

This project aim to achive automodeling for neural networks. The current goal is launch several instances of a service in Rancher from the catalog with diferents configurations to try which is the better one.

The estructure of this projects has two different parts:
* Service directory: where the script and the dockerfile to build the image is located.
* Templates directory: which is intended to be added as templates to the catalog so we can launch this from the catalog itself.

## Getting Started

This project is intended to be launched as a template from the Rancher catalog. So the first step is add this repository to the rancher catalog. You can copy the directory ml-modeling-experiments to your catalog repository too.

Then you can access to the template experiment-launcher. Before you can launch the experiments, you have to specify in a yaml file the different parameters for the launcher to try out.
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
   - **PARAMS**: here you have to specify the parameters for the experiment to try and launch. Notice that this service will try all the combinations possible between the parameters. Also is very important that the names of this parameters are exactly the same as they are in the service's rancher-compose file. Otherwise it won't work. You can specified two different types of parameters. In the example you can see both of these types:
	   - lineal: for lineal increments
	   - absolute: for a concrete values or strings

**IMPORTANT NOTE: The URL_API and de URL_RANCHER has to be accessible from our host.**

This configuration yaml file could be in any source in internet. Then we set the parameters for rancher:
- **Url entries**: the url where the config file is located
- **Access-key**: access key for rancher
- **Secret-key**: secret key for rancher


## Python script dockerization

In the Service directory we have the dockerfile to convert our script in a docker image. It's important to note that the template for the kubernetes catalog in rancher is configured to select our configuration of the image.  If you want to build your own image and launched in kubernetes from the catalog, you have to change the experiment-launcher-rc.yml

<!-- TODO: Update this if we change the config file setings to take the environment-->
Also, here we store the template for the config file to setup the kubectl. This config is nowdays setup to work in the environment 'ml-kube'. So if you want to work in another environment you have to change this. One easy way to do this is to take the config file generated by the Rancher in the kubectl section, and then remove the corresponding sections in the file.

Also in this directory we have the exec directory to store the executables for rancher-compose, rancherCLI and kubectl.

### Individual test for the script

You can create a container, and execute the following command. The first parameter for 'lanzadorServicios.py' is the url with the parameters to test, the second one is the rancher access key, and the last one the secret key:
```
python lanzadorServicios.py http://url_parameters.text access-key secret-key
```

## Kubernetes Templates

This directory has everything necessary for launch the experiments from the catalog in Rancher. We have also another template to try out which just print a couple of parameters that we give.
You can add this repository to you rancher catalog or copy the directory ml-modeling-experiments to your catalog repository too.
