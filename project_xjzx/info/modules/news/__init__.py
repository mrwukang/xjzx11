# -*- coding:utf-8 -*-
from flask import Blueprint

news_blueprint = Blueprint("news", __name__)

from info.modules.news import views
