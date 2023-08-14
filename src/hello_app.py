#this script set up the basic flask app

from flask import Flask


app = Flask(__name__)

@app.route("/", methods =["GET"])
def main():
    return "<h1 style='Blue:red'>Hello World!</h1>"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)