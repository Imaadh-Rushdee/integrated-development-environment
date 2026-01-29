from flask import Flask
from flask_cors import CORS
from controller import api
from db import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    # init database
    init_db()

    # register routes
    app.register_blueprint(api)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
