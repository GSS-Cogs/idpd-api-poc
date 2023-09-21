from flask import Flask, request, Response, json
from store.sparql import SparqlStore

app = Flask(__name__)
storage = SparqlStore()
jsonld = "application/ld+json"


@app.route("/datasets", methods =["GET"])
def datasets():
    if request.headers['Accept'] == "application/ld+json":
        return get_json(request)
    else:
        return "", 406

def get_json(request):
    return "", 200


@app.route("/datasets/<id>", methods =["GET"])
def dataset_id(id):
    status_code = 200
    if request.headers['Accept'] == jsonld:
    # Retrieve the dataset based on the 'id' parameter 
        dataset = storage.get_dataset_by_id(id)

        if dataset is None:
            status_Code  = 404
        
        resp = Response(json.dumps(dataset))
        resp.headers['Content-Type'] = jsonld
        return resp , status_code
    
    elif request.headers.get('Accept') == "text/html":
        html_response = ""
        return html_response, 200

    elif request.headers.get('Accept') == "text/csv":
        # Return a CSV file download
        csv_content = "CSV file content"
        return Response(csv_content, mimetype="text/csv"), 200

    elif request.headers.get('Accept') == "application/csvm+json":
        # Return a .csv-metadata.json file
        metadata_json_content = "CSV Metadata JSON content"
        return Response(metadata_json_content, mimetype="application/csvm+json"), 200

    else:
        return "", 406
    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

