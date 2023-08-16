#this script set up the basic flask app
from flask import Flask, request


app = Flask(__name__)

@app.route("/", methods =["GET"])
def main():
    if request.method == 'GET':
        if request.url.endswith('json') or request.headers['Accept'] == "application/ld+json":
            return get_json(request)
        else:
            return not_recognised(request)
    else: 
        return"Not GET request"

def get_json(request):
    return "200"

def not_recognised(request):
    return "406"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)