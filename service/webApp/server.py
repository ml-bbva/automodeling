from flask import Flask
import json
import json2html

app = Flask(__name__)

@app.route('/')
def getResults():
	with open('/usr/src/myapp/results/global_results.json', 'r') as f:
		results = json.load(f)
	return json2html.json2html.convert(json=results)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
