# -*- coding: utf-8 -*-
import logging
import os
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
    dir_file = os.path.abspath(__file__)
    dir_info = os.path.dirname(dir_file)
    dir_base = os.path.dirname(dir_info)
    dir_log = os.path.join(dir_base, 'logs/log')

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler(dir_log, maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """通过传入不同的配置名称，初始化对应配置的应用实例"""

    setup_log(config_name)
    app = Flask(__name__)
    from info.modules.news import news_blueprint
    app.register_blueprint(news_blueprint)
    from info.modules.admin import admin_blueprint
    app.register_blueprint(admin_blueprint)
    from info.modules.index import index_blueprint
    app.register_blueprint(index_blueprint)

    from info.modules.passport import passport_blueprint
    app.register_blueprint(passport_blueprint)
    from info.modules.users import user_blueprint
    app.register_blueprint(user_blueprint)

    app.config.from_object(config[config_name])
    Session(app)
    db.init_app(app)
    CSRFProtect(app)
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # redis_store = StrictRedis(host=app.config.get("REDIS_HOST"), port=app.config.get("REDIS_PORT"))
    return app
