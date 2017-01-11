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

# TODO: Add an argeparser
# import argparse or click
# TODO: Set up del logger en condiciones. Ahora todo esta a critical. Puede que
# interese que escriba en algun lado
# logger = logging.getLogger('services_launcher')

def rm_stack(name_stack, url, access_key, secret_key):
    #Borra el stack con el nombre dado y obtiene los logs
    get_logs_container(
        name_stack=name_stack, url=url,
        access_key=access_key, secret_key=secret_key)
    global stacks_running
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])
    stacks_running -= 1

def create_nameSpace(nameSpace, url, access_key, secret_key):
    #Crea un nameSpace con el nombre dado
    os.system('./exec/kubectl create namespace ' + nameSpace)

def create_service(nameSpace, serviceFile):
    os.system('./exec/kubectl --namespace=' + nameSpace + ' create -f ' + serviceFile)

def create_replicationController(nameSpace, rcFile):
    os.system('./exec/kubectl --namespace=' + nameSpace + ' create -f ' + rcFile)



def start_stack(name_stack, url, access_key, secret_key):
    #Ejecuta el stack con el nombre dado
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'start'])




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

    # Creacion del dockercompose
    content_dockercompose = str(content_all['files']['docker-compose.yml'])
    logging.critical('docker compose del JSON')
    docker_compose = open('docker-compose.yml', 'w')
    docker_compose.write(content_dockercompose)
    docker_compose.close()

    return (url_rancher, url_catalog)
    # getParams(parametros)

def launch_experiments(url, catalog_name, access_key, secret_key, parametros, parametros_nombre):
    #Iteracion para lanzar las combinaciones entre los parametros de entrada
    global stacks_running
    cont = 0
    threads = []
    for param in itertools.product(*parametros):
        #Escritura del fichero de respuestas
        # TODO: Context manager -> with statement
        answers = open('answers.txt', 'w')
        for j in range(len(parametros_nombre)):
            answers.write(parametros_nombre[j]+'='+str(param[j])+'\n')
            logging.critical(parametros_nombre[j]+'='+str(param[j])+'\n')
        answers.close()

        project_name = ''.join([catalog_name,'Model{num}'.format(num=cont)])
        # project_name = 'Model{num}'.format(num=cont)
        logging.critical('Preparado para lanzar stacks')

        while(stacks_running>=stack_limit):
            continue

        #Llamadas a rancher-compose
        create_stack(
            name_stack=project_name,
            url=url,
            access_key=access_key,
            secret_key=secret_key)
        start_stack(
            name_stack=project_name,
            url=url,
            access_key=access_key,
            secret_key=secret_key)

        threads.append(threading.Timer(time_out, rm_stack, args=[project_name, url, access_key, secret_key]))
        threads[cont].start()

        stacks_running += 1
        cont = cont + 1

def get_logs_container(name_stack, url, access_key, secret_key):
    #Obtiene los logs de un experimento dado
    logging.critical('Obteniendo logs para'+name_stack)
    llamadaInspect = Popen(
        ['./exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'inspect',name_stack],
        stdout=PIPE)
    logging.critical('Obteniendo serviceIds')
    (out, err) = llamadaInspect.communicate()
    if err:
        logging.critical('ERROR EN LA LLAMADA A RANCHER INSPECT')
        raise SyntaxError('Parametros en el yml de entradas incorectos')
    else:
        logging.critical('Llamada a rancher inspect correcta')

    info_stack = json.loads(out.decode('utf-8'))

    for service in info_stack['serviceIds']:
        logging.critical('Logs del servicio'+service)
        llamadaLogs = Popen(
            ['./exec/rancher',
            '--url', url,
            '--access-key', access_key,
            '--secret-key', secret_key,
            'logs',service],
            stdout=PIPE)
        logging.critical('Obteniendo serviceIds')
        (out, err) = llamadaLogs.communicate()
        if err:
            logging.critical('ERROR EN LA LLAMADA A RANCHER LOGS')
            raise SyntaxError('Parametros en el yml de entradas incorectos')
        else:
            logging.critical('Llamada a rancher logs correcta')
        service_logs = out.decode('utf-8')
        # TODO: Decidir que hacer con los logs
        print(service_logs)
        file_logs = ''.join(['./logs/',name_stack,'.txt'])
        with open(file_logs,"w") as file:
            file.write(service_logs)



logging.critical('COMIENZA PROCESO DE LANZAMIENTO EXPERIMENTOS')

parametros_nombre=[] # Prescindible?
parametros = [] # Prescindible?
stacks_running = 0
# sincronizacion = threading.Semaphore(value=stack_limit)
if(os.path.isdir('./logs')):
    call(['rm','-rf','./logs'])
os.mkdir("./logs")

# TODO: Add argparse
#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
logging.critical('url de las entradas:'+url_entradas)
access_key = str(sys.argv[2])
logging.critical('access key:'+access_key)
secret_key = str(sys.argv[3])
logging.critical('secret key:'+secret_key)

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logging.critical('Obtenido el fichero de configuracion para los parametros')

# Obtenemos parametros time_out y stack_limit que son globales para todos los stacks
time_out = entradas["time_stop"]
stack_limit = entradas["limit_stacks"]

catalogs_nombre = [catalog for catalog in entradas["stacks_catalog"]][::-1]
logging.critical(catalogs_nombre)
for catalog in catalogs_nombre:
    logging.critical(catalog)
    url, url_catalog = get_configuration(configuration=entradas["stacks_catalog"][catalog], access_key=access_key, secret_key=secret_key)
    parametros_nombre, parametros = get_params(entradas["stacks_catalog"][catalog]['PARAMS'])
    launch_experiments(
            url=url,
            access_key=access_key,
            secret_key=secret_key,
            catalog_name=catalog,
            parametros=parametros,
            parametros_nombre=parametros_nombre)
