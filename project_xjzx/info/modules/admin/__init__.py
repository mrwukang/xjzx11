# -*- coding:utf-8 -*-
from flask import Blueprint, request, session, redirect

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

from info.modules.admin import views


@admin_blueprint.before_request
def admin_login():
    ignore_url = ["/admin/login"]
    if request.path in ignore_url:
        return
    if "admin_id" not in session or not session.get("is_admin", None):
        return redirect("/admin/login")


