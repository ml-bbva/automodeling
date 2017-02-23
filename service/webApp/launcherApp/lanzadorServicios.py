# coding=utf-8
"""Launch several services in a Rancher platform."""
import json
# import sys
import requests
import itertools
from subprocess import Popen, PIPE
import threading
import yaml
import numpy
import os
import signal
import shutil
from operator import methodcaller
import time
import re
from launcherApp.dbConnection import dbConnector

# TO SEE DEBUG AND INFO
# TODO: Check Error Handling
# TODO: create docstrings
# DB CONNECTION
# TODO: Fix it for local usage.


class lanzador:
    """."""

    def __init__(
            self, url_entradas, access_key, secret_key,
            db_password, logger):
        """Init the object."""
        self.url_entradas = url_entradas
        self.access_key = access_key
        self.secret_key = secret_key
        self.logger = logger
        self.namespaces_running = 0
        self.namespaces_limit = 0
        self.time_out = 0
        self.access_flag = threading.Event()
        self.db_password = db_password
        self.db = None
        self.MODULE_DIR = os.path.dirname(__file__)

    def main(self):
        """Main execution of the class."""
        print('COMIENZA PROCESO DE LANZAMIENTO EXPERIMENTOS')
        entradas = requests.get(url=self.url_entradas, verify=False)
        entradas = yaml.load(entradas.text)
        self.logger.info('Obtenido el fichero de configuracion ' +
                         'para los parametros')
        self.logger.debug(entradas)
        self.time_out = entradas["time_out"]
        self.namespaces_limit = entradas["limit_namespaces"]

        self.connect_db()
        self.prepareDirectories()
        with open('./results/global_results.json', 'w') as f:
            self.logger.info('Creado fichero de resultados vacio')
            # dicempty = {}
            # json.dump(dicempty, f)
            arrayempty = []
            json.dump(arrayempty, f)
        catalogs = [catalog for catalog in entradas["catalog_services"]][::-1]
        self.logger.info(catalogs)
        param_record = {}

        for catalog in catalogs:
            self.logger.info(catalog)
            files, url, url_catalog = self.getConfiguration(
                    configuration=entradas["catalog_services"][catalog])
            self.configurateKubectl(rancher_url=url)
            os.system('./exec/kubectl version')
            parametros_nombre, parametros = self.getDefinedParams(
                    entradas["catalog_services"][catalog]['PARAMS'])
            parametros_nombre, parametros = self.addDefaultParams(
                    parametros_nombre, parametros)
            param_record[catalog] = self.launchExperiments(
                        files=files,
                        catalog_name=catalog,
                        parametros=parametros,
                        parametros_nombre=parametros_nombre)
            self.db.save_document(param_record, coll_name='parameter_records')

        # TODO: Delete json things
        with open('./results/parameter_record.json', 'w') as outfile:
            json.dump(param_record, outfile)

    def connect_db(self):
        """Establish a connection with the database."""
        cont = 0
        while cont < 10:
            try:
                self.db = dbConnector(
                        db_name='automodelingDB',
                        password=self.db_password,
                        arangoURL='http://database:8529')
                # self.db = dbConnector(
                #         db_name='automodelingDB',
                #         arangoURL='http://database:8529')
            except Exception:
                self.logger.warning('NO DATABASE CONNECTION')
                cont += 1
                time.sleep(5)
            else:
                self.logger.info('Database succesfuly connected')
                break
        if cont > 10:
            self.logger.critical('FAILED TO CONNECT THE DATABASE')

        self.db.create_collection('parameter_records')
        self.db.create_collection('global_results')

        # TODO: Improve the format for the documents

    def prepareDirectories(self):
        """Clean and make the directories needed."""
        if(os.path.isdir('./files')):
            shutil.rmtree('./files')
        os.mkdir("./files")
        os.mkdir("./files/launch")

        # if(os.path.isdir('./results')):
        #     shutil.rmtree('./results')
        # os.mkdir("./results")

    def getConfiguration(self, configuration):
        """Extrae de un yaml toda la configuracion para el lanzador."""
        # Peticion a la API para obtener el dockercompose
        url_catalog = configuration["URL_API"]
        url_rancher = configuration["URL_RANCHER"]
        auth = requests.auth.HTTPBasicAuth(self.access_key, self.secret_key)
        r = requests.get(url=url_catalog, auth=auth)
        content_all = r.json()
        self.logger.info('Obtenido el objeto JSON de la API')
        self.logger.debug(content_all)

        # Obtención de los ficheros de los servicios que hay que arrancar
        files = content_all['files']

        # Se obtienen de la API todos los ficheros que se van a arrancar
        # Se guardan en la carpeta ./files, que se ha creado antes
        for file in files:
            name_file = file
            with open('./files/' + name_file, 'w') as file_service:
                file_service.write(str(content_all['files'][name_file]))

        return (files, url_rancher, url_catalog)

    def configurateKubectl(self, rancher_url):
        """Configurate the kubectl client in the container."""
        # TODO: Dejar configurable los parametros que llevan el nombre ml-kube

        # Configuramos kubectl
        self.logger.debug('Empezamos a configurar kubectl')

        # calculo de la ruta relativa donde se encuentra la carpeta .kube
        filepath = '/root/.kube/'
        # if args.local:  #TODO: New local configuration needed
        #     filepath = '/home/ignacio/.kube/config'
        os.system('cp ' + self.MODULE_DIR + '/config ' + filepath)

        # Obtenemos la plantilla para el config
        with open(filepath + 'config', 'r') as f:
            text = f.read()
            self.logger.debug('Plantilla del config\n' + text)
            kubeConfig = yaml.load(text)

        # https://rancher.default.svc.cluster.local:80/r/projects/1a8238/kubernetes
        kubeConfig['clusters'][0]['cluster']['server'] = rancher_url
        kubeConfig['users'][0]['user']['username'] = self.access_key
        kubeConfig['users'][0]['user']['password'] = self.secret_key

        self.logger.info('Configuration set')

        with open(filepath + 'config', 'w') as f:
            yaml.dump(kubeConfig, f)

    def getDefinedParams(self, parametros_yml):
        """Obtiene los parametros para un stack del catalogo."""
        parametros_nombre = []
        parametros = []
        self.logger.debug(parametros_yml)
        # Las distintas formas que se consideran son: parametroNombre->n
        # 1. [valorInicial:valorFinal:Salto] -> Lineal
        # 2. TODO: [valorInicial:valorFinal:Función] -> Otro tipo de funcion
        # 3. TODO: HIDDEN_SIZE debe aceptar parametros que no fueran absolute
        for parametro in parametros_yml:
            self.logger.info(parametro)
            parametros_nombre.append(parametro)
            # Obtiene el parametro HIDDEN_SIZE, que es especial
            if(parametro == 'HIDDEN_SIZE'):
                layers = [parametros_yml[parametro]['number_units'] for i in
                          range(parametros_yml[parametro]['number_layers'][0])]
                combinations = []
                for combination in itertools.product(*layers):
                    combination = ','.join(map(str, combination))
                    combinations.append(combination)
                parametros.append(combinations)
                continue

            opcion = parametros_yml[parametro]['type']
            # parametro[parametro.index("{"):parametro.index("}")]
            if(opcion == 'lineal'):
                valorInicial = parametros_yml[parametro]['initial-value']
                valorFinal = parametros_yml[parametro]["final-value"]
                valorSalto = parametros_yml[parametro]["interval"]
                opcionesParametro = numpy.arange(
                        valorInicial, valorFinal, valorSalto)
                parametros.append(opcionesParametro.tolist())
            elif(opcion == 2):
                # opcionesParametro
                pass
            elif(opcion == "absolute"):
                parametros.append(parametros_yml[parametro]["param"])
            else:
                self.logger.critical('ERROR: FORMATO DE PARAMETROS INCORRECTO')
                raise SyntaxError('Parametros en el yml incorectos')

        parametros_nombre = parametros_nombre[::-1]
        parametros = parametros[::-1]
        self.logger.info('Obtenida la lista de posibles parametros')

        return (parametros_nombre, parametros)

    def addDefaultParams(self, parametros_nombre, parametros):
        """Add default params to the files."""
        with open('./files/rancher-compose.yml', 'r') as f:
            fileContent = f.read()
            rancherComposeContent = yaml.load(fileContent)

        questions = rancherComposeContent['.catalog']['questions']

        for element in questions:
            if(element['variable'] in parametros_nombre
                    or element['variable'] == 'NAMESPACE'
                    or element['variable'] == 'ROOT_TOPIC'):
                continue
            else:
                parametros_nombre.append(element['variable'])
                listElem = list()
                listElem.append(element['default'])
                parametros.append(listElem)

        return (parametros_nombre, parametros)

    def launchExperiments(
            self, files, catalog_name,
            parametros, parametros_nombre):
        """Lanza las combinaciones entre los parametros de entrada."""
        cont = 1
        # threads = []
        threadsCheckResults = []
        param_record = {}

        # Se guardan los parametros en el fichero answers.txt
        for param in itertools.product(*parametros):
            # Substitucion de las variables en los ficheros
            # Check -> Los nombres de los paramentros deben ser exactamente
            #          los mismos que en los ficheros.

            # El namespace no admite mayusculas
            namespace = ''.join([catalog_name, 'model{num}'.format(num=cont)])
            param_record[namespace] = {}
            for file_name in files:
                if(file_name != 'rancher-compose.yml'):
                    with open('./files/' + file_name, 'r') as f:
                        text = f.read()

                    for index in range(len(parametros_nombre)):
                        self.logger.info(
                            parametros_nombre[index] + '=' +
                            str(param[index]) + '\n')
                        text = text.replace(
                            '${' + parametros_nombre[index] + '}',
                            str(param[index]))
                        param_record[namespace][
                            parametros_nombre[index]] = param[index]
                    # Set by default the namespace
                    text = text.replace(
                        '${' + 'NAMESPACE' + '}',
                        namespace)
                    text = text.replace(
                        '${' + 'ROOT_TOPIC' + '}',
                        namespace)
                    with open('./files/launch/' + file_name, 'w') as f:
                        f.write(text)

            while(self.namespaces_running >= self.namespaces_limit):
                continue

            self.logger.info('Preparado para lanzar namespace ' + namespace)
            # Llamadas a kubectl
            # Se crea un namespace por cada combinacion
            self.create_namespace(namespace)
            # Por cada fichero en ./files, se lanza un start_service
            # dentro de un namespace
            for file in files:
                if(file != 'rancher-compose.yml'):
                    self.start_service(namespace, './files/launch/' + file)

            pid = self.startKafka(namespace)

            # threads.append(threading.Timer(
            #        time_out, rm_namespace, args=[namespace, pid]))
            # threads[cont-1].start()

            threadsCheckResults.append(threading.Thread(
                    target=self.checkResults,
                    args=[namespace, self.time_out, pid]))
            threadsCheckResults[cont-1].start()

            cont = cont + 1

        return param_record

    def create_namespace(self, namespace):
        """Crea un namespace con el nombre dado."""
        os.system('./exec/kubectl create namespace ' + namespace)
        self.namespaces_running += 1

    def rm_namespace(self, namespace, pid):
        """Borra el namespace con el nombre dado y su contenido."""
        self.killProcess(pid)
        # Llama a kafka para obtener los resultados
        self.getResults(namespace, 1)
        # Delete namespace content
        os.system(
            './exec/kubectl delete ' +
            '--all service,rc,ingress,pod --namespace=' +
            namespace +
            ' --now'
        )
        # Delete the namespace itself
        os.system('./exec/kubectl delete namespace ' + namespace)
        self.namespaces_running -= 1

    def start_service(self, namespace, serviceFile):
        """Launch one service or rc from one file."""
        self.logger.info(
                'Lanzando servicio ' + serviceFile +
                ' en el namespace ' + namespace)
        os.system('./exec/kubectl --namespace=' + namespace +
                  ' create -f ' + serviceFile)

    def startKafka(self, namespace):
        """Start the kafka consumer process."""
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
            self.logger.info(pid)
        return pid

    def checkResults(self, namespace, pid):
        """Check the results till it reaches accuracy 1."""
        time_finish = time.time() + self.time_out
        last_time = time.time()
        start_time = time.time()
        while (time.time() <= time_finish):
            self.logger.debug('Está en le bucle de acceso a resultados')
            lastResults = self.getResults(namespace, 10)
            if(len(lastResults) == 0):
                time.sleep(10)
                continue
            if(lastResults[len(lastResults)-1]['accuracy'] == 1.0):
                self.logger.info('Resultados:')
                self.logger.info(lastResults)
                break
            time.sleep(10)
            last_time = time.time()

        self.rm_namespace(namespace, pid)
        self.logger.debug('Debería pasar por aquí para guardar los resultados')
        data = {namespace: {
                'time': last_time - start_time,
                'Results': lastResults}}

        # TODO: Delete json things
        if self.access_flag.isSet():
            self.access_flag.wait()
        self.access_flag.set()
        with open('./results/global_results.json', 'r') as json_file:
            json_obj = json.load(json_file)
        with open('./results/global_results.json', 'w') as json_file:
            self.logger.info('Guardando resultados:')
            self.logger.info(data)
            json_obj.append(data)
            self.logger.info(json_obj)
            json.dump(json_obj, json_file)
        self.db.save_document(data, 'global_results')
        self.access_flag.clear()

    def getResults(self, namespace, numberResults):
        """Obtiene el numero de resultados especificadas como parametro."""
        process1 = Popen(['cat', './results/'+namespace], stdout=PIPE)
        process2 = Popen(
                ['tail', '-'+str(numberResults)],
                stdin=process1.stdout,
                stdout=PIPE)
        (out, err) = process2.communicate()
        out = out.decode('UTF-8')
        self.logger.info(out)

        results = str(out).split('\n')[:-1]
        self.logger.info(results)

        if(len(results) <= 1):
            return []

        prog = re.compile('[(\d|\.)+\s]+')
        if(not (prog.match(results[len(results)-1]) and
                prog.match(results[0]))):
            self.logger.warning("Incorrect results format")
            self.logger.warning(results[0])
            self.logger.warning(results[len(results)-1])
            return []

        results = list(map(methodcaller("split"), results))

        if(len(results) <= 1):
            return []

        self.logger.info(results)
        resultsList = [{'cost': float(result[3]),
                        'accuracy': float(result[4])} for result in results]
        self.logger.info(resultsList)
        return resultsList

        # self.logger.info("Ejecutando cat directamente:")
        # os.system('cat ./results/'+namespace+' | tail -'+str(numberResults))

    def killProcess(self, pid):
        """Mata el proceso kafka creado por popen."""
        os.killpg(os.getpgid(pid), signal.SIGTERM)
