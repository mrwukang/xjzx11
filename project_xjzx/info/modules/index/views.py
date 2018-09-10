# -*- coding: utf-8 -*-
from flask import render_template, current_app

from info.modules.index import index_blueprint


@index_blueprint.route("/")
def index():
    return render_template("news/index.html")


# @index_blueprint.route('/favicon.ico')
# def favicon():
#     return current_app.send_static_file("news/images")
