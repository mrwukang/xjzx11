# -*- coding:utf-8 -*-
from flask import render_template

from info.modules.news import news_blueprint


@news_blueprint.route("/news")
def index():
    return render_template("news/index.html")
