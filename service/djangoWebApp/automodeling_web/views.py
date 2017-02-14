from django.shortcuts import render
from django.http import HttpResponse
import json2html
import json
import os

# Create your views here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def results(request):
    with open(BASE_DIR + '/results/global_results.json', 'r') as f:
        results = json.load(f)
    return HttpResponse(json2html.json2html.convert(json=results))
