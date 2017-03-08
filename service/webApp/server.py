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
def get_index():
    """Pagina inicial."""
    # TODO: links{ proyectos, cola, pull}
    # TODO: actions{ process_yaml, launch_experiments, stop_everything}
    #return render_template('index.html')-> Servirá en un futuro
    return "<h1>Página inicial</h1>"

@app.route('/launch_experiments', methods=['POST'])
def launch_experiments():
    """Lanzar experimentos en la cola."""
    # Hecho: dbConnector.save_document
    launcher.launch_experiments()
    return 'Experimentos lanzandose'

@app.route('/stop_everything')
def stop_everything():
    """Para todo"""
    # TODO: funcion que para todo lo que se esta ejecutando
    # Se hace en el lanzador
    pass

@app.route('/process_yaml')
def process_yaml():
    # TODO: funcion que trata el yaml que se subirá
    pass

@app.route('/queue', methods=['GET'])
def get_queue():
    """Devuelve la cola de los experimentos que faltan por lanzarse."""
    # TODO: links{ lista de cada experimento} -> redirecciona a
    # /projects/project_id/experiment_id
    # TODO: actions{ delete_queue}
    return str(launcher.get_execution_queue())

@app.route('/delete_queue', methods=['DELETE'])
def delete_queue():
    """Elimina todos los experimentos de la cola"""
    # TODO: funcion que elimina los experimentos de la cola
    # funcion que se define en el lanzador
    pass

@app.route('/pull', methods=['GET'])
def get_pull():
    """Devuelve la cola de los experimentos que faltan por lanzarse."""
    # TODO: links{ lista de cada experimento} -> redirecciona a
    # /projects/project_id/experiment_id
    # TODO: actions{ delete_pull}
    return str(launcher.get_execution_list())

@app.route('/delete_pull', methods=['DELETE'])
def delete_pull():
    """Elimina todos los experimentos de la cola"""
    # TODO: funcion que elimina los experimentos del pull
    # funcion que se define en el lanzador
    pass

@app.route('/projects')
def get_projects():
    """Página de todos los proyectos"""
    # TODO: links{ cada proyecto}
    # TODO: actions{ delete_everything}
    # TODO: info{ time_out, namespaces_limit}
    return "<h1>Esta es la página de los proyectos</h1>"

@app.route('/projects/delete_everything', methods=['DELETE'])
def delete_everything():
    """Elimina todos los experimentos de todos los proyectos"""
    # TODO: funcion que elimine todo
    # se hace en el lanzador
    pass

@app.route('/projects/<str:project_id>')
def get_project(project_id):
    """Página de un solo proyecto"""
    # TODO: links{ cada experimento}
    # TODO: actions{ delete_experiments}
    # TODO: info{ parametros del proyecto, best_experiment, worst_experiment}
    pass

@app.route('/projects/<str:project_id>/delete_experiments', methods=['DELETE'])
def delete_experiments(project_id):
    """Elimina todos los experimentos de un proyecto"""
    # TODO: funcion que elimine todos los experimentos del proyecto
    # esta se hace en el lanzador
    pass

@app.route('/projects/<str:project_id>/<str:experiment_id>')
def get_experiment(project_id,experiment_id):
    """Devuelve la página de un experimento"""
    # TODO: funcion que devuelve toda la informacion de un experimento
    # se hace en el lanzador
    # TODO: actions{ delete_experiment}
    # TODO: info{ parametros del experimento, estado del experimento}
    pass

@app.route('/projects/<str:project_id>/<str:experiment_id>/delete_experiment',
    methods=['DELETE'])
def delete_experiment():
    """Elimina el experimento"""
    # TODO: funcion que elimina el experimento
    # se hace en el lanzador
    pass


# TODO: función que añade experimentos a la cola


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
