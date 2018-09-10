# -*- coding:utf-8 -*-
from flask import render_template

from info.modules.admin import admin_blueprint


@admin_blueprint.route("/admins")
def index():
    return render_template("admin/index.html")
    # return render_template("news/index.html")
