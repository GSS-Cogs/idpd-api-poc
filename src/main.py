from flask import Flask, request, Response , json 
from store.sparql import SparqlStore

app = Flask(__name__)
storage = SparqlStore()
jsonld = "application/ld+json"

@app.route("/datasets", methods =["GET"])
def datasets():
    if request.headers['Accept'] == jsonld: 
        result = storage.get_datasets()

        resp = Response(json.dumps(result))
        resp.headers['Content-Type'] = jsonld
        return resp , 200
    
    else:
        return "", 406



if __name__ == "__main__":
    storage.setup()
    app.run(debug=True, host='0.0.0.0', port=5000)
