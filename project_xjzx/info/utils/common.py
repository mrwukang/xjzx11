# -*- coding: utf-8 -*-
import functools
from flask import session, g, current_app, request, redirect


def do_index_class(index):
    """自定义过滤器，过滤点击排序html的class"""
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""


def user_login(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        from info.models import User
        try:
            if user_id:
                g.user = User.query.get(user_id)
            else:
                g.user = None
                if request.path.startswith("/profile"):
                    return redirect("/")
        except Exception as e:
            current_app.logger.error(e)

        return view(*args, **kwargs)
    return wrapper
