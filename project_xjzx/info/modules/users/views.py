#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import session, make_response, request, jsonify, g, render_template, current_app, redirect

from info.modules.users import user_blueprint
from info.utils.common import user_login
from info.response_code import RET
from info import db


@user_blueprint.route('/info')
@user_login
def get_user_info():
    if not g.user:
        return redirect("/")
    data = {
        "user_info": g.user.to_dict()
    }
    return render_template("news/user.html", data=data)


@user_blueprint.route('/user_info', methods=["POST", "GET"])
@user_login
def base_info():
    """
        用户基本信息
        1. 获取用户登录信息
        2. 获取到传入参数
        3. 更新并保存数据
        4. 返回结果
        :return:
        """
    user = g.user
    if request.method == "GET":
        return render_template('news/user_base_info.html', data={"user_info": user.to_dict()})

    # 2. 获取到传入参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in (['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3. 更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")


@user_blueprint.route('/pic_info', methods=['GET', 'POST'])
@user_login
def pic_info():
    """
            用户头像
            1. 获取用户登录信息
            2. 获取到上传头像
            3. 更新并保存数据
            4. 返回结果
            :return:
            """
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pic_info.html', data={"user_info": user.to_dict()})


@user_blueprint.route('/pass_info', methods=['GET', 'POST'])
@user_login
def pass_info():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_pass_info.html', data={"user_info": user.to_dict()})


@user_blueprint.route('/user_follow', methods=['GET'])
@user_login
def user_follow():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_follow.html', data={"user_info": user.to_dict()})


@user_blueprint.route('/collection', methods=['GET'])
@user_login
def collection():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_collection.html', data={"user_info": user.to_dict()})


@user_blueprint.route('/news_release', methods=['GET'])
@user_login
def news_release():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_news_release.html', data={"user_info": user.to_dict()})


@user_blueprint.route('/news_list', methods=['GET'])
@user_login
def news_list():
    user = g.user
    if request.method == "GET":
        return render_template('news/user_news_list.html', data={"user_info": user.to_dict()})
