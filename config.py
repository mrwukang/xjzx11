from redis import StrictRedis
import os

class Config(object):
    DEBUGE = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wukang:123587415@192.168.15.131:3306/database"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDIS_HOST = '192.168.15.131'
    REDIS_PORT = 6379
    SECRET_KEY = "itheima"
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 60*60*24*14
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    QINIU_AK = 'H999S3riCJGPiJOity1GsyWufw3IyoMB6goojo5e'
    QINIU_SK = 'uOZfRdFtljIw7b8jr6iTG-cC6wY_-N19466PXUAb'
    QINIU_BUCKET = 'itcast20171104'
    QINIU_URL = 'http://oyvzbpqij.bkt.clouddn.com/'

class DevelopConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://wukang:123587415@192.168.15.131:3306/xjzx"