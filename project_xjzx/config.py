from redis import StrictRedis
import os

class Config(object):
    DEBUGE = False


class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wukang:123587415@192.168.15.131:3306/xjzx"


