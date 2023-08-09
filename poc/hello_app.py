from flask import Flask, request


app = Flask(__name__)

def main():
    return "<h1 style='Blue:red'>Hello World!</h1>"


if __name__ == "__main__":
    app.run(host='0.0.0.0')
