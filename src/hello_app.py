#this script set up the basic flask app

import re
from flask import Flask, request


app = Flask(__name__)

@app.route("/", methods =["GET"])
def main():
    if request.method == 'GET':
        if request.url.endswith('json') or request.headers['Accept'] == "application/ld+json":
            return '200'
        else:
            return '406'            


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)