# coding=utf-8
"""Flask Server. It manage the API petitions."""
from flask import Flask, render_template
import json
import json2html
import argparse
import logging
from launcherApp.lanzadorServicios import lanzador
# from launcherApp.dbConnection import dbConnector

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
    launcher.main()
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
    # TODO: Finish method
    experiment = id
    return str(id)


@app.route('/results/<int:id>', methods=['GET'])
def get_experiment_results(id):
    """Devuelve los resultados de un experimento."""
    # TODO: Finish method
    experiment = id
    return str(id)


@app.route('/queue', methods=['GET'])
def get_queue():
    """Devuelve la cola de los experimentos que faltan por lanzarse."""
    # TODO: Finish method
    return 'Queue'


@app.route('/launch', methods=['POST'])
def launch_experiments():
    """Aniadir a la cola experimentos nuevos."""
    # TODO: Finish method
    return 'New experiments'


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_experiment():
    """Eliminar un experimento de la cola."""
    # TODO: Finish method
    return 'Experiment deleted'


@app.route('/delete/<param>/<value>', methods=['DELETE'])
def delete_experiment_param(param, value):
    """Eliminar experimentos con un parametro definido."""
    # TODO: Finish method
    respon = ''.join(['Experiments of param: ', param, '=', value, ' deleted'])
    return respon


@app.route('/delete/all', methods=['DELETE'])
def delete_queue():
    """Eliminar todos los experimentos de la cola."""
    # TODO: Finish method
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
