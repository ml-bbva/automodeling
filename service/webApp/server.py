# coding=utf-8
from flask import Flask, render_template
import json
import json2html
import os

app = Flask(__name__)


# Pagina inicial 
@app.route('/')
def get_results():
	#with open('/usr/src/myapp/results/global_results.json', 'r') as f:
	#with open('../launcherApp/results/global_results.json', 'r') as f:
	#	results = json.load(f)
	#return json2html.json2html.convert(json=results)
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


