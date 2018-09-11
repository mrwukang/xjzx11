from redis import StrictRedis
import logging


class Config(object):
    """工程配置信息"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wukang:123587415@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "jpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq"

    # redis设置
    REDIS_HOST = "192.168.15.131"
    REDIS_PORT = 6379

    # flask_session的设置信息
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400

    LOG_LEVEL = logging.DEBUG


class DevelopConfig(Config):
    """开发模式的配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wukang:123587415@192.168.15.131:3306/xjzx"


class ProductionConfig(Config):
    """生产模式的配置"""
    LOG_LEVEL = logging.ERROR


config = {
    "development": DevelopConfig,
    "production": ProductionConfig
}
