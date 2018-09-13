# -*- coding:utf-8 -*-
from flask import Blueprint

news_blueprint = Blueprint("news", __name__, url_prefix="/news")

from info.modules.news import views
