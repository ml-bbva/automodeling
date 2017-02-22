# coding=utf-8
from flask import Flask, render_template
import json
import json2html
import os
import argparse
import logging

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
parser.add_argument('bd_password', metavar='bd_password', type=str,
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
logger.debug('url de las entradas:' + url_entradas)
access_key = args.access_key
logger.debug('access key:' + access_key)
secret_key = args.secret_key
logger.debug('secret key:' + secret_key)

launcher = lanzador(args.url_entradas,args.access_key,args.secret_key)


# Pagina inicial 
@app.route('/')
def get_results():
	#with open('/usr/src/myapp/results/global_results.json', 'r') as f:
	#with open('../launcherApp/results/global_results.json', 'r') as f:
	#	results = json.load(f)
	#return json2html.json2html.convert(json=results)
	launcher.main()
	return render_template('index.html')


# Devuelve la dirección configurada de rancher
@app.route('/rancherUrl', methods=['GET'])
def get_rancherUrl():
	with open('config.json', 'r') as f:
		configuration = json.load(f)
	return str(configuration)


# Devuelve los parametros de un experimento
@app.route('/params/<int:id>', methods=['GET'])
def get_experiment_params(id):
	experiment = id
	return str(id)


# Devuelve los resultados de un experimento
@app.route('/results/<int:id>', methods=['GET'])
def get_experiment_results(id):
	experiment = id
	return str(id)


# Devuelve la cola de los experimentos que faltan por lanzarse
@app.route('/queue', methods=['GET'])	
def get_queue():
	return 'Queue'


# Añadir a la cola experimentos nuevos
@app.route('/launch', methods=['POST'])	
def launch_experiments():
	return 'New experiments'


# Eliminar un experimento de la cola
@app.route('/delete/<int:id>', methods=['DELETE'])	
def delete_experiment():
	return 'Experiment deleted'


# Eliminar experimentos con un parametro definido
@app.route('/delete/<param>/<value>', methods=['DELETE'])	
def delete_experiment_param(param,value):
	respon = ''.join(['Experiments of param: ',param,'=',value,' deleted'])
	return respon


# Eliminar todos los experimentos de la cola
@app.route('/delete/all', methods=['DELETE'])	
def delete_queue():
	return 'Queue deleted'


# Devuelve el mensaje de error correspondiente
@app.errorhandler(404)
def page_not_found(e):
	return "<h1>Página no encontrada</h1>", 404

@app.errorhandler(500)
def page_not_found(e):
	return "<h1>Fallo en el servidor</h1>", 500


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)


