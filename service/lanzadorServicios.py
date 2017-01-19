# coding=utf-8
import json
import sys
import requests
import itertools
from subprocess import call, Popen, PIPE
import threading
import yaml
import numpy
import logging
import os
import fileinput

# import argparse or click
# TODO: Set up del logger en condiciones. Ahora todo esta a critical. Puede que
# interese que escriba en algun lado
# logger = logging.getLogger('services_launcher')

def rm_nameSpace(nameSpace):
    #Borra el nameSpace con el nombre dado y obtiene los logs
    #get_logs_container(
    #    name_stack=name_stack, url=url,
    #    access_key=access_key, secret_key=secret_key)
    global nameSpaces_running
    os.system('./exec/kubectl delete namespace ' + nameSpace)
    nameSpaces_running -= 1

def create_nameSpace(nameSpace):
    #Crea un nameSpace con el nombre dado
    global nameSpaces_running
    os.system('./exec/kubectl create namespace ' + nameSpace)
    nameSpaces_running += 1

def start_service(nameSpace, serviceFile):
    logging.critical('Lanzando servicio ' + serviceFile + ' en el nameSpace ' + nameSpace)
    os.system('./exec/kubectl --namespace=' + nameSpace + ' create -f ' + serviceFile)

def get_params(parametros_yml):
    #Obtiene los parametros para un stack del catalogo
    parametros_nombre=[]
    parametros=[]
    logging.critical(parametros_yml)
    #Las distintas formas que se consideran son: parametroNombre->n
    #1. [valorInicial:valorFinal:Salto] -> Lineal
    #2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
    #3. [un String]
    for parametro in parametros_yml:
        logging.critical(parametro)
        parametros_nombre.append(parametro)
        opcion = parametros_yml[parametro]['type'] #parametro[parametro.index("{"):parametro.index("}")]
        if(opcion=='lineal'):
            valorInicial = parametros_yml[parametro]['initial-value']
            valorFinal = parametros_yml[parametro]["final-value"]
            valorSalto = parametros_yml[parametro]["interval"]
            opcionesParametro = numpy.arange(valorInicial, valorFinal, valorSalto)
            parametros.append(opcionesParametro.tolist())
        elif(opcion==2):
            #opcionesParametro
            pass
        elif(opcion=="absolute"):
            parametros.append(parametros_yml[parametro]["param"])
        else:
            logging.critical('ERROR: FORMATO DE PARAMETROS INCORRECTO')
            raise SyntaxError('Parametros en el yml de entradas incorectos')

    parametros_nombre = parametros_nombre[::-1]
    parametros = parametros[::-1]
    logging.critical('Obtenida la lista de posibles parametros')

    return (parametros_nombre, parametros)

def get_configuration(configuration, access_key, secret_key):
    #Extrae de un yaml toda la configuracion para el lanzador de stacks y la organiza

    # Peticion a la API para obtener el dockercompose
    url_catalog = configuration["URL_API"]
    url_rancher = configuration["URL_RANCHER"]
    auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
    r = requests.get(url=url_catalog, auth=auth)
    content_all = r.json()
    logging.critical('Obtenido el objeto JSON de la API')

    # Obtención de los ficheros de los servicios que hay que arrancar
    files = content_all['files']

    # En esta parte, se obtienen de la API todos los ficheros que se van a arrancar
    # Se guardan en la carpeta ./files, que se ha creado antes
    for file in files:
        if(file != 'rancher-compose.yml'):
            name_file = file
            with open('./files/' + name_file, 'w') as file_service:
                file_service.write(str(content_all['files'][name_file]))

    return (files, url_rancher, url_catalog)


def configurate_kubectl (rancher_url, access_key, secret_key):
    # TODO: Dejar configurable los parametros que llevan el nombre ml-kube
    # Configuramos kubectl

    # calculo de la ruta relativa donde se encuentra la carpeta .kube
    basepath = os.path.dirname(__file__) # __file__ es lo mismo que sys.argv[0]
    # TODO: Comprobar cual es la ruta relativa a kubectl -> "..", "..", "..", "root/.kube/config"
    filepath = os.path.abspath(os.path.join(basepath, "..","..","..", ".kube/config"))

    # Obtenemos la plantilla para el config
    with open('config', 'r') as f:
        t = f.read()
        kubeConfig = yaml.load(t)

    # rancher_url = https://rancher.default.svc.cluster.local:80/r/projects/1a8238/kubernetes
    kubeConfig['clusters'][0]['cluster']['server'] = rancher_url
    kubeConfig['users'][0]['user']['username'] = access_key
    kubeConfig['users'][0]['user']['password'] = secret_key

    with open(filepath, 'w') as f:
        yaml.dump(kubeConfig, f)


def launch_experiments(files, catalog_name, parametros, parametros_nombre):
    #Iteracion para lanzar las combinaciones entre los parametros de entrada
    global nameSpaces_running
    cont = 0
    threads = []
    # Se guardan los parametros en el fichero answers.txt
    for param in itertools.product(*parametros):
        #Substitucion de las variables en los ficheros
        # TODO: Check -> Los nombres de los paramentros deben ser exactamente los mismos que en los ficheros. Engorro para configura

        # TODO: Format string with ${} in python. Need a dictionary: parametros_nombre:param
        # TODO: Set always the NAMESPACE even if there is no parameter for it

        for index in range(len(parametros_nombre)):
            logging.critical(parametros_nombre[index] + '=' + str(param[index])+'\n')
            for file in files:
                if(file != 'rancher-compose.yml'):
                    with fileinput.FileInput('./files/' + file, inplace=True, backup='.bak') as file:
                        for line in file:
                            print(line.replace('${'+parametros_nombre[index]+'}', str(param[index])), end='')
                            print(line.replace('${' + 'NAMESPACE' + '}', str(param[index])), end='')


        # El namespace no admite mayusculas
        nameSpace = ''.join([catalog_name,'model{num}'.format(num=cont)])

        logging.critical('Preparado para lanzar nameSpaces')

        while(nameSpaces_running>=nameSpaces_limit):
            continue

        #Llamadas a kubectl
        # Se crea un nameSpace por cada combinacion
        create_nameSpace(nameSpace)
        # Por cada fichero en ./files, se lanza un start_service dentro de un nameSpace
        for file in files:
            if(file != 'rancher-compose.yml'):
                start_service(nameSpace, './files/' + file)

        threads.append(threading.Timer(time_out, rm_nameSpace, args=[nameSpace]))
        threads[cont].start()

        nameSpaces_running += 1
        cont = cont + 1


logging.critical('COMIENZA PROCESO DE LANZAMIENTO EXPERIMENTOS')

parametros_nombre=[] # Prescindible?
parametros = [] # Prescindible?
nameSpaces_running = 0
# sincronizacion = threading.Semaphore(value=nameSpaces_limit)
if(os.path.isdir('./logs')):
    call(['rm','-rf','./logs'])
os.mkdir("./logs")

if(os.path.isdir('./files')):
    call(['rm','-rf','./files'])
os.mkdir("./files")

# TODO: Add argparse
#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
logging.critical('url de las entradas:' + url_entradas)
access_key = str(sys.argv[2])
logging.critical('access key:' + access_key)
secret_key = str(sys.argv[3])
logging.critical('secret key:' + secret_key)

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logging.critical('Obtenido el fichero de configuracion para los parametros')

# Obtenemos parametros time_out y nameSpaces_limit que son globales para todos los stacks
time_out = entradas["time_out"]
nameSpaces_limit = entradas["limit_nameSpaces"]

catalogs_nombre = [catalog for catalog in entradas["catalog_services"]][::-1]
logging.critical(catalogs_nombre)

for catalog in catalogs_nombre:
    logging.critical(catalog)
    files, url, url_catalog = get_configuration(
            configuration=entradas["catalog_services"][catalog],
            access_key=access_key,
            secret_key=secret_key)
    configurate_kubectl(rancher_url=url, access_key=access_key, secret_key=secret_key)
    os.system('./exec/kubectl version')
    parametros_nombre, parametros = get_params(entradas["catalog_services"][catalog]['PARAMS'])
    launch_experiments(
            files=files,
            catalog_name=catalog,
            parametros=parametros,
            parametros_nombre=parametros_nombre)


# def get_logs_container(name_stack, url, access_key, secret_key):
#     #Obtiene los logs de un experimento dado
#     logging.critical('Obteniendo logs para'+name_stack)
#     llamadaInspect = Popen(
#         ['./exec/rancher',
#         '--url', url,
#         '--access-key', access_key,
#         '--secret-key', secret_key,
#         'inspect',name_stack],
#         stdout=PIPE)
#     logging.critical('Obteniendo serviceIds')
#     (out, err) = llamadaInspect.communicate()
#     if err:
#         logging.critical('ERROR EN LA LLAMADA A RANCHER INSPECT')
#         raise SyntaxError('Parametros en el yml de entradas incorectos')
#     else:
#         logging.critical('Llamada a rancher inspect correcta')
#
#     info_stack = json.loads(out.decode('utf-8'))
#
#     for service in info_stack['serviceIds']:
#         logging.critical('Logs del servicio'+service)
#         llamadaLogs = Popen(
#             ['./exec/rancher',
#             '--url', url,
#             '--access-key', access_key,
#             '--secret-key', secret_key,
#             'logs',service],
#             stdout=PIPE)
#         logging.critical('Obteniendo serviceIds')
#         (out, err) = llamadaLogs.communicate()
#         if err:
#             logging.critical('ERROR EN LA LLAMADA A RANCHER LOGS')
#             raise SyntaxError('Parametros en el yml de entradas incorectos')
#         else:
#             logging.critical('Llamada a rancher logs correcta')
#         service_logs = out.decode('utf-8')
#         # TODO: Decidir que hacer con los logs
#         print(service_logs)
#         file_logs = ''.join(['./logs/',name_stack,'.txt'])
#         with open(file_logs,"w") as file:
#             file.write(service_logs)
    # Creacion del dockercompose
    """
    content_dockercompose = str(content_all['files']['docker-compose.yml'])
    logging.critical('docker compose del JSON')
    docker_compose = open('docker-compose.yml', 'w')
    docker_compose.write(content_dockercompose)
    docker_compose.close()

    return (url_rancher, url_catalog)
    # getParams(parametros)
    """
