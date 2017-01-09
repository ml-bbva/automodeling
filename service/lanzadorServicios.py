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

def rm_stack(name_stack):
    get_logs_container(name_stack)
    global stacksRunning
    call([
        './exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'rm', '--stop', name_stack])
    stacksRunning -= 1

def createService(name_stack):
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'create'])

def startService(name_stack):
    call([
        './exec/rancher-compose',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        '--env-file', 'answers.txt',
        '--project-name', name_stack,
        'start'])

def get_logs_container(name_stack):
    logging.critical('Obteniendo logs para'+name_stack)
    llamadaInspect = Popen(
        ['./exec/rancher',
        '--url', url,
        '--access-key', access_key,
        '--secret-key', secret_key,
        'inspect',name_stack],
        stdout=PIPE)
    #logging.critical('Obteniendo serviceIds')
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
        logging.critical(service_logs)

        file_logs = ''.join(['./logs/',name_stack,'.txt'])
        with open(file_logs,"w") as file:
            file.write(service_logs)



    

# TODO: Set up del logger en condiciones. Ahora todo esta a critical. Puede que interese que escriba en algun lado
# logger = logging.getLogger('services_launcher')

#logging.critical('ENTRÓ EN EL LANZADOR DE STACKS')

# TODO: Dar nombre bien a los esperimentos lanzados.
url = ''
parametrosNombre=[]
threads = []
catalogs = []
catalogName = ''
cont = 1
if(os.path.isdir('./logs')):
    call(['rm','-rf','./logs'])
os.mkdir("./logs")

#Lectura de parametros para las url y las keys
url_entradas = str(sys.argv[1])
logging.critical('url de las entradas:'+url_entradas)
access_key = str(sys.argv[2])
secret_key = str(sys.argv[3])

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logging.critical('Obtenido el fichero de configuracion para los parametros')

time_stop = entradas["time_stop"]
limitStacks = entradas["limit_stacks"]
stacksRunning = 0

def lanzar_stacks(parametrosYml):
    parametrosNombre=[]
    parametros=[]
    #logging.critical(parametrosYml)
    global stacksRunning
    global cont
    #Las distintas formas que se consideran son: parametroNombre->n
    #1. [valorInicial:valorFinal:Salto] -> Lineal
    #2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
    #3. [un String]
    for parametro in parametrosYml:
        #logging.critical(parametro)
        parametrosNombre.append(parametro)
        opcion = parametrosYml[parametro]['type'] #parametro[parametro.index("{"):parametro.index("}")]
        if(opcion=='lineal'):
            valorInicial = parametrosYml[parametro]['initial-value']
            valorFinal = parametrosYml[parametro]["final-value"]
            valorSalto = parametrosYml[parametro]["interval"]
            opcionesParametro = numpy.arange(valorInicial, valorFinal, valorSalto)
            parametros.append(opcionesParametro.tolist())
        elif(opcion==2):
            #opcionesParametro
            pass
        elif(opcion=="absolute"):
            parametros.append(parametrosYml[parametro]["param"])
        else:
            logging.critical('ERROR: FORMATO DE PARAMETROS INCORRECTO')
            raise SyntaxError('Parametros en el yml de entradas incorectos')

    parametrosNombre = parametrosNombre[::-1]
    parametros = parametros[::-1]
    #logging.critical('Obtenida la lista de posibles parametros')

    for param in itertools.product(*parametros):
        #Escritura del fichero de respuestas
        answers = open('answers.txt', 'w')
        for j in range(len(parametrosNombre)):
            answers.write(parametrosNombre[j]+'='+str(param[j])+'\n')

        answers.close()
        project_name = ''.join([catalogName,'Model{num}'.format(num=cont)])
        #logging.critical('Preparado para lanzar stacks')

        while(stacksRunning>=limitStacks):
            continue

        #Llamadas a rancher-compose
        createService(project_name)
        startService(project_name)

        threads.append(threading.Timer(time_stop, rm_stack, args=[project_name]))
        #logging.critical("Se inicia el thread del stack con cont:"+str(cont-1))
        threads[cont-1].start()
        stacksRunning += 1
        cont = cont + 1


def getConfiguration(catalog):
    global url
    url_catalog = catalog["URL_API"]
    url = catalog["URL_RANCHER"]
    #Peticion a la API para obtener el dockercompose
    auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
    r = requests.get(url=url_catalog, auth=auth)
    content_all = r.json()
    logging.critical('Obtenido el objeto JSON de la API')
    content_dockercompose = str(content_all['files']['docker-compose.yml'])
    #logging.critical('docker compose del JSON')
    docker_compose = open('docker-compose.yml', 'w')
    docker_compose.write(content_dockercompose)
    docker_compose.close()
    parametros = catalog["PARAMS"]
    lanzar_stacks(parametros)


catalogsNombre = [catalog for catalog in entradas["stacks_catalog"]][::-1]
#logging.critical(catalogsNombre)
for catalog in catalogsNombre:
    catalogName = catalog
    logging.critical(catalogName)
    getConfiguration(entradas["stacks_catalog"][catalogName])


