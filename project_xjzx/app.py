from flask import Flask


def create_app(Config):
    app = Flask(__name__)
    app.config.from_object(Config)
