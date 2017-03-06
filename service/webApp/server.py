# coding=utf-8
"""Flask Server. It manage the API petitions."""
from flask import Flask, render_template
import json
import json2html
import argparse
import logging
from launcherApp.lanzadorServicios import lanzador

app = Flask(__name__)

parser = argparse.ArgumentParser(
            description='Launch several neural networks' +
            ' in order to achieve hypermaremetring tunning.')
parser.add_argument('url_entradas', metavar='url_entradas', type=str,
                    help='url in which the yaml file is located')
parser.add_argument('access_key', metavar='access_key', type=str,
                    help='access_key for rancher')
parser.add_argument('secret_key', metavar='secret_key', type=str,
                    help='secret_key for rancher')
parser.add_argument('db_password', metavar='db_password', type=str,
                    help='password for the db access')
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


url_entradas = args.url_entradas
logger.info('url de las entradas:' + url_entradas)
access_key = args.access_key
logger.info('access key:' + access_key)
secret_key = args.secret_key
logger.info('secret key:' + secret_key)

launcher = lanzador(
        args.url_entradas, args.access_key,
        args.secret_key, args.db_password, logger)


@app.route('/')
def get_results():
    """Pagina inicial."""
    # with open('/usr/src/myapp/results/global_results.json', 'r') as f:
    # with open('../launcherApp/results/global_results.json', 'r') as f:
    # 	results = json.load(f)
    # return json2html.json2html.convert(json=results)
    launcher.launch_experiments()
    return render_template('index.html')


@app.route('/rancherUrl', methods=['GET'])
def get_rancherUrl():
    """Devuelve la dirección configurada de rancher."""
    with open('config.json', 'r') as f:
        configuration = json.load(f)
    return str(configuration)


@app.route('/params/<int:id>', methods=['GET'])
def get_experiment_params(id):
    """Devuelve los parametros de un experimento."""
    # TODO: funcion que devuelva los parametros de un experimento
    #       encontrado por id
    # Hecho: dbConnector.get_document
    experiment = id
    return str(id)


@app.route('/results/<int:id>', methods=['GET'])
def get_experiment_results(id):
    """Devuelve los resultados de un experimento."""
    experiment = id
    # TODO: funcion que pueda encontrar un experimento por id
    # y devuelva los resultados asociados
    # Hecho: dbConnector.get_document
    return str(id)


@app.route('/queue', methods=['GET'])
def get_queue():
    """Devuelve la cola de los experimentos que faltan por lanzarse."""
    # TODO: funcion que devuelva todos los experimentos que estan por lanzarse
    #       o se están lanzando
    # Hecho: dbConnector.get_document
    return str(launcher.get_execution_queue())


@app.route('/execution_list')
def get_execution_list():
    """."""
    return str(launcher.get_execution_list())

# TODO: función que añade experimentos a la cola


@app.route('/launch', methods=['POST'])
def launch_experiments():
    """Lanzar experimentos en la cola."""
    # Hecho: dbConnector.save_document
    launcher.launch_experiments()
    return 'Experimentos lanzandose'


@app.route('/newparams', methods=['POST'])
def set_execution_params():
    """Confifurar los parametro de la ejecucion."""
    # TODO: función que establezca los parámetros de la ejecución
    return 'New parameters'


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_experiment():
    """Eliminar un experimento concreto de la cola."""
    # TODO: funcion que elimine un experimento de la cola encontrado por id
    # Hecho: dbConnector.delete_documents_param
    return 'Experiment deleted'


@app.route('/delete/<param>/<value>', methods=['DELETE'])
def delete_experiment_param(param, value):
    """Eliminar experimentos con un parametro definido de la cola."""
    # TODO: funcion que elimine todos los experimentos de la cola que tengan
    # un valor de parametro determinado
    # Hecho: dbConnector.delete_documents_param
    respon = ''.join(['Experiments of param: ', param, '=', value, ' deleted'])
    return respon


@app.route('/delete/all', methods=['DELETE'])
def delete_queue():
    """Eliminar todos los experimentos de la cola."""
    # TODO: funcion que elimine todos los experimentos de la cola
    # Hecho: dbConnector.delete_all_documents
    return 'Queue deleted'


@app.errorhandler(404)
def page_not_found(e):
    """Devuelve el mensaje de error correspondiente."""
    return "<h1>Página no encontrada</h1>", 404


@app.errorhandler(500)
def page_not_found(e):
    """Devuelve el mensaje de error correspondiente."""
    return "<h1>Fallo en el servidor</h1>", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
