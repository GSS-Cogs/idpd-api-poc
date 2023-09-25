from flask import Flask, request, Response , json 
from store.sparql import SparqlStore

app = Flask(__name__)
STORAGE = SparqlStore()
JSONLD = "application/ld+json"

@app.route("/datasets", methods =["GET"])
def datasets():
    status_code = 200
    if request.headers['Accept'] == JSONLD: 
        result = STORAGE.get_datasets()
        
        if len(result["items"]) == 0:
            status_Code  = 404
        
        resp = Response(json.dumps(result))
        resp.headers['Content-Type'] = JSONLD
        return resp , status_code
    
    else:
        return "", 406



if __name__ == "__main__":
    STORAGE.setup()
    app.run(debug=True, host='0.0.0.0', port=5000)
