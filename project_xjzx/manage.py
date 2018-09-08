#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wukang:123587415@192.168.15.131:3306/database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "jpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq"
    REDIS_HOST = "192.168.15.131"
    REDIS_PORT = 6379


app.config.from_object(Config)
db = SQLAlchemy(app)
CSRFProtect(app)
redis_store = StrictRedis(host=Config.REDIS_PORT, port=Config.REDIS_PORT)
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)


@app.route("/")
def hello_world():
    return "sadasdsad"


if __name__ == '__main__':
    manager.run()
