#this script will call the app and run it
from hello_app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)