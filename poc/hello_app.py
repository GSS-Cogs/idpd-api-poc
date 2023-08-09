from flask import Flask, request


app = Flask(__name__)

@app.route("/", methods=['GET'])
def main():
    if request.method == 'GET':
        if request.url.endswith(".json") or request.headers["Accept"] == "application/json":
            return get_json(request)
        elif request.url.endswith(".csv") or request.headers["Accept"] == "text/csv":
            return get_csv(request)
    else:
        return "<h1 style='color:red'>ERROR!</h1>"

def get_csv(request):
    return "I’m a csv"

def get_json(request):
    return "I’m a json"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
