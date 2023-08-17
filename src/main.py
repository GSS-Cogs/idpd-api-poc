from flask import Flask, request


app = Flask(__name__)

@app.route("/datasets", methods =["GET"])
def datasets():
    if request.headers['Accept'] == "application/ld+json":
        return get_json(request)
    else:
        return "", 406

def get_json(request):
    return "", 200

def not_recognised(request):
    return "", 406


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)