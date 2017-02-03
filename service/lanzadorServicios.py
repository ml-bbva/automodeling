# coding=utf-8
# import json
import sys
import requests
import itertools
from subprocess import call, Popen, PIPE
import threading
import yaml
import numpy
import logging
import os
import signal
import argparse
import shutil
from operator import methodcaller
import time

# TO SEE DEBUG AND INFO
# TODO: Check Error Handling
# TODO: create docstrings

# ARGPARSE CONFIG

parser = argparse.ArgumentParser(
            description='Launch several neural networks' +
            ' in order to achieve hypermaremetring tunning.')
parser.add_argument('url_entradas', metavar='url_entradas', type=str,
                    help='url in which the yaml file is located')
parser.add_argument('access_key', metavar='access_key', type=str,
                    help='access_key for rancher')
parser.add_argument('secret_key', metavar='secret_key', type=str,
                    help='secret_key for rancher')
parser.add_argument('-l', '--local', action='store_true',
                    help='Change the config to launchet it in local')
parser.add_argument('--info', action='store_const', const=20,
                    help='set log level INFO')
parser.add_argument('--debug', action='store_const', const=10,
                    help='set log level DEBUG')

# GET THE ARGUMENTS
args = parser.parse_args()

# LOGGER CONFIG
logger = logging.getLogger('AUTOMODELING')
# create formatter
formatter = logging.Formatter('%(name)s:%(levelname)s\t%(message)s')
# create console handler
ch = logging.StreamHandler()

# Set log level
if args.info:
    logger.setLevel(args.info)
    ch.setLevel(args.info)
elif args.debug:
    logger.setLevel(args.debug)
    ch.setLevel(args.debug)
else:
    logger.setLevel(logging.WARN)
    ch.setLevel(logging.WARN)

# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

# PARÁMETROS GLOBALES DE LA EJECUCIÓN
namespaces_running = 0

# Lectura de parametros para las url y las keys
url_entradas = args.url_entradas
logger.debug('url de las entradas:' + url_entradas)
access_key = args.access_key
logger.debug('access key:' + access_key)
secret_key = args.secret_key
logger.debug('secret key:' + secret_key)

entradas = requests.get(url=url_entradas, verify=False)
entradas = yaml.load(entradas.text)
logger.info('Obtenido el fichero de configuracion para los parametros')
logger.debug(entradas)

# Obtenemos parametros time_out y namespaces_limit que son globales para todos los stacks
time_out = entradas["time_out"]
namespaces_limit = entradas["limit_namespaces"]


def main():
    print('COMIENZA PROCESO DE LANZAMIENTO EXPERIMENTOS')
    prepareDirectories()

    catalogs = [catalog for catalog in entradas["catalog_services"]][::-1]
    logger.info(catalogs)

    for catalog in catalogs:
        logger.info(catalog)
        files, url, url_catalog = getConfiguration(configuration=entradas["catalog_services"][catalog])
        configurateKubectl(rancher_url=url)
        os.system('./exec/kubectl version')
        parametros_nombre, parametros = getDefinedParams(entradas["catalog_services"][catalog]['PARAMS'])
        parametros_nombre, parametros = addDefaultParams(parametros_nombre, parametros)
        launchExperiments(
                files=files,
                catalog_name=catalog,
                parametros=parametros,
                parametros_nombre=parametros_nombre)


def prepareDirectories():
    if(os.path.isdir('./logs')):
        # os.rmdir("./logs")
        shutil.rmtree('./logs')
    os.mkdir("./logs")

    if(os.path.isdir('./files')):
        # os.rmdir("./files")
        shutil.rmtree('./files')
    os.mkdir("./files")
    os.mkdir("./files/launch")

    if(os.path.isdir('./results')):
        # os.rmdir('./results')
        shutil.rmtree('./results')
    os.mkdir("./results")


def getConfiguration(configuration):
    # Extrae de un yaml toda la configuracion para el lanzador de namespaces y la organiza

    # Peticion a la API para obtener el dockercompose
    url_catalog = configuration["URL_API"]
    url_rancher = configuration["URL_RANCHER"]
    auth = requests.auth.HTTPBasicAuth(access_key, secret_key)
    r = requests.get(url=url_catalog, auth=auth)
    content_all = r.json()
    logger.info('Obtenido el objeto JSON de la API')
    logger.debug(content_all)

    # Obtención de los ficheros de los servicios que hay que arrancar
    files = content_all['files']

    # En esta parte, se obtienen de la API todos los ficheros que se van a arrancar
    # Se guardan en la carpeta ./files, que se ha creado antes
    for file in files:
        name_file = file
        with open('./files/' + name_file, 'w') as file_service:
            file_service.write(str(content_all['files'][name_file]))

    return (files, url_rancher, url_catalog)


def configurateKubectl(rancher_url):
    # TODO: Dejar configurable los parametros que llevan el nombre ml-kube

    # Configuramos kubectl
    logger.info('Empezamos a configurar kubectl')

    # calculo de la ruta relativa donde se encuentra la carpeta .kube
    filepath = "/root/.kube/config"
    if args.local:
        filepath = '/home/ignacio/.kube/config'
    os.system("cp config " + filepath)

    # Obtenemos la plantilla para el config
    with open(filepath, 'r') as f:
        text = f.read()
        logger.debug('Plantilla del config\n' + text)
        kubeConfig = yaml.load(text)

    # rancher_url = https://rancher.default.svc.cluster.local:80/r/projects/1a8238/kubernetes
    kubeConfig['clusters'][0]['cluster']['server'] = rancher_url
    kubeConfig['users'][0]['user']['username'] = access_key
    kubeConfig['users'][0]['user']['password'] = secret_key

    logger.debug('Configuration set')

    with open(filepath, 'w') as f:
        yaml.dump(kubeConfig, f)


def getDefinedParams(parametros_yml):
    # Obtiene los parametros para un stack del catalogo
    parametros_nombre = []
    parametros = []
    logger.debug(parametros_yml)
    # Las distintas formas que se consideran son: parametroNombre->n
    # 1. [valorInicial:valorFinal:Salto] -> Lineal
    # 2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
    # 3. TODO: HIDDEN_SIZE deberia aceptar tambien parametros que no fueran absolute
    for parametro in parametros_yml:
        logger.info(parametro)
        parametros_nombre.append(parametro)
        # Obtiene el parametro HIDDEN_SIZE, que es especial
        if(parametro=='HIDDEN_SIZE'):
            layers = [parametros_yml[parametro]['number_units'] for i in range(parametros_yml[parametro]['number_layers'][0])]
            combinations = []
            for combination in itertools.product(*layers):
                combination = ','.join(map(str,combination))
                combinations.append(combination)
            parametros.append(combinations)
            continue

        opcion = parametros_yml[parametro]['type']
        # parametro[parametro.index("{"):parametro.index("}")]
        if(opcion == 'lineal'):
            valorInicial = parametros_yml[parametro]['initial-value']
            valorFinal = parametros_yml[parametro]["final-value"]
            valorSalto = parametros_yml[parametro]["interval"]
            opcionesParametro = numpy.arange(valorInicial, valorFinal, valorSalto)
            parametros.append(opcionesParametro.tolist())
        elif(opcion == 2):
            # opcionesParametro
            pass
        elif(opcion == "absolute"):
            parametros.append(parametros_yml[parametro]["param"])
        else:
            logger.critical('ERROR: FORMATO DE PARAMETROS INCORRECTO')
            raise SyntaxError('Parametros en el yml de entradas incorectos')

    parametros_nombre = parametros_nombre[::-1]
    parametros = parametros[::-1]
    logger.info('Obtenida la lista de posibles parametros')

    return (parametros_nombre, parametros)


def addDefaultParams(parametros_nombre, parametros):
    with open('./files/rancher-compose.yml', 'r') as f:
        fileContent = f.read()
        rancherComposeContent = yaml.load(fileContent)

    questions = rancherComposeContent['.catalog']['questions']

    for element in questions:
        if(element['variable'] in parametros_nombre or element['variable']=='NAMESPACE' or element['variable']=='ROOT_TOPIC'):
            continue
        else:
            parametros_nombre.append(element['variable'])
            listElem = list()
            listElem.append(element['default'])
            parametros.append(listElem)

    return (parametros_nombre, parametros)


def launchExperiments(files, catalog_name, parametros, parametros_nombre):
    # Iteracion para lanzar las combinaciones entre los parametros de entrada
    global namespaces_running
    cont = 1
    threads = []
    threadsCheckResults = []
    # Se guardan los parametros en el fichero answers.txt
    for param in itertools.product(*parametros):
        # Substitucion de las variables en los ficheros
        # Check -> Los nombres de los paramentros deben ser exactamente
        #          los mismos que en los ficheros.

        # El namespace no admite mayusculas
        namespace = ''.join([catalog_name, 'model{num}'.format(num=cont)])

        for file_name in files:
            if(file_name != 'rancher-compose.yml'):
                with open('./files/' + file_name, 'r') as f:
                    text = f.read()
                for index in range(len(parametros_nombre)):
                    logger.info(
                        parametros_nombre[index] + '=' +
                        str(param[index]) + '\n')
                    text = text.replace(
                        '${' + parametros_nombre[index] + '}',
                        str(param[index]))
                # If there is not a Namespace in the paremetres it's set by default
                text = text.replace(
                    '${' + 'NAMESPACE' + '}',
                    namespace)
                text = text.replace(
                    '${' + 'ROOT_TOPIC' + '}',
                    namespace)
                with open('./files/launch/' + file_name, 'w') as f:
                    f.write(text)

        while(namespaces_running >= namespaces_limit):
            continue

        logger.info('Preparado para lanzar namespaces')
        # Llamadas a kubectl
        # Se crea un namespace por cada combinacion
        create_namespace(namespace)
        # Por cada fichero en ./files, se lanza un start_service dentro de un namespace
        for file in files:
            if(file != 'rancher-compose.yml'):
                start_service(namespace, './files/launch/' + file)

        pid = startKafka(namespace)

        #threads.append(threading.Timer(time_out, rm_namespace, args=[namespace, pid]))
        #threads[cont-1].start()

        threadsCheckResults.append(threading.Thread(target=checkResults, args=[namespace,time_out,pid]))
        threadsCheckResults[cont-1].start()

        cont = cont + 1


def checkResults(namespace, time_out, pid):
    time_start = time.time()
    time_finish = time_start + time_out
    while (time.time() <= time_finish):
        lastResults = getResults(namespace,10)
        #if(lastResults[len(lastResults)]['accuracy'] == 1):
        #    logger.info('Resultados: ' + lastResults)
        #    rm_namespace(namespace,pid)
        #elif()
        time.sleep(5)




def create_namespace(namespace):
    # Crea un namespace con el nombre dado
    global namespaces_running
    os.system('./exec/kubectl create namespace ' + namespace)
    namespaces_running += 1


def start_service(namespace, serviceFile):
    logger.info('Lanzando servicio ' + serviceFile + ' en el namespace ' + namespace)
    os.system('./exec/kubectl --namespace=' + namespace + ' create -f ' + serviceFile)


def startKafka(namespace):
    pid = 0
    with open('./results/'+namespace, 'w') as file_results:
        kafkaConsumer = Popen(
            ['./exec/kafka-console-consumer'],
            env={"KAFKA_SERVICE": "kafka.default.svc.cluster.local",
                 "TOPIC": namespace+"-metrics",
                 "OFFSET": "oldest",
                 "KAFKA_GROUP": namespace},
            stdout=file_results,
            shell=True,
            preexec_fn=os.setsid)
        pid = kafkaConsumer.pid
        logger.info(pid)
    return pid


def rm_namespace(namespace, pid):
    # Borra el namespace con el nombre dado y su contenido
    global namespaces_running
    # Mata el proceso kafka
    killProcess(pid)
    # Llama a kafka para obtener los resultados
    getResults(namespace, 1)
    # Delete namespace content
    os.system(
        './exec/kubectl delete ' +
        '--all service,rc,ingress,pod --namespace=' +
        namespace +
        ' --now'
    )
    # Delete the namespace itself
    os.system('./exec/kubectl delete namespace ' + namespace)
    namespaces_running -= 1


def getResults(namespace, numberResults):
    # Obtiene el resultado del numero de lineas especificadas como parametro
    process1 = Popen(['cat', './results/'+namespace], stdout=PIPE)
    process2 = Popen(['tail', '-'+str(numberResults)], stdin=process1.stdout, stdout=PIPE)
    (out, err) = process2.communicate()
    out = out.decode('UTF-8')
    logger.info(out)

    results = str(out).split('\n')
    # results = map(split('\t'),results)
    results = list(map(methodcaller("split"), results))

    logger.info(results)

    resultsList = []

    #resultsList = [{'cost': float(result[3]), 'accuracy': float(result[4])} for result in results]

    return resultsList
    
    # logger.info("Ejecutando cat directamente:")
    # os.system('cat ./results/'+namespace+' | tail -'+str(numberResults))


def killProcess(pid):
    # Mata el proceso kafka creado por popen
    os.killpg(os.getpgid(pid), signal.SIGTERM)


main()
