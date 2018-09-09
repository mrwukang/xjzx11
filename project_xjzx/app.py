from flask import Flask
from flask import render_template
import redis
from views_admin import admin_blueprint
from views_user import user_blueprint
from views_news import news_blueprint

def create_app(Config):
    app = Flask(__name__)
    app.config.from_object(Config)


app.run()