# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_session import Session

from info.config import config


db = SQLAlchemy()
redis_store = None


def setup_log(config_name):
    """配置日志"""
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    formater = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d %(message)s")
    file_log_handler.setFormatter(formater)
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """通过传入不同的配置名称，初始化对应配置的应用实例"""

    # setup_log(config_name)
    app = Flask(__name__)
    from modules.news import news_blue
    app.register_blueprint(news_blue)

    app.config.from_object(config[config_name])
    Session(app)
    # db = SQLAlchemy(app)
    db.init_app(app)
    CSRFProtect(app)
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    return app
