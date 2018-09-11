# -*- coding:utf-8 -*-

import time
import random
import re

from flask import request, current_app, make_response, jsonify, session

from info import redis_store, constants, db
from info.models import User
from info.modules.passport import passport_blueprint
from info.response_code import RET

from libs.captcha.captcha import captcha


@passport_blueprint.route("/image_code")
def get_image_code():
    image_code_id = request.args.get("code_id")
    name, text, image = captcha.generate_captcha()
    print(text)
    try:
        redis_store.setex("IMG_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


@passport_blueprint.route("/sms_code", methods=["POST"])
def send_sms_code():
    """发送验证码"""
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code_id = param_dict.get("image_code_id")
    image_code = param_dict.get("image_code")
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数输入不全")
    if not re.match(r"^1[3-9]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号输入格式有误")
    try:
        # 从redis中获取存储的验证码
        image_code_redis = redis_store.get("IMG_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取验证码失败")
    if not image_code_redis:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    image_code_redis = image_code_redis.decode()
    if image_code.lower() != image_code_redis.lower():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    try:
        redis_store.delete("IMG_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已注册")
    result = random.randint(100000, 999999)
    try:
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, result)
        print(result)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据存入数据库失败")
    return jsonify(errno=RET.OK, errmsg="生成验证码成功")


@passport_blueprint.route("/register", methods=["POST"])
def register():
    param_dict = request.json
    sms_code = param_dict.get("smscode")
    password = param_dict.get("password")
    mobile = param_dict.get("mobile")
    if not all([sms_code, password, mobile]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    sms_code_redis = redis_store.get("SMS_" + mobile)
    sms_code_redis = sms_code_redis.decode()
    if not sms_code_redis:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    if sms_code != sms_code_redis:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    try:
        redis_store.delete("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户数据保存失败")
    session["nick_name"] = user.nick_name
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    return jsonify(errno=RET.OK, errmsg="用户注册成功")


@passport_blueprint.route("/login", methods=["POST"])
def login():
    """
        1. 获取参数和判断是否有值
        2. 从数据库查询出指定的用户
        3. 校验密码
        4. 保存用户登录状态
        5. 返回结果
        :return:
        """
    param_dict = request.json
    mobile = param_dict.get("mobile")
    password = param_dict.get("password")
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数输入不全")
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    session["nick_name"] = user.nick_name
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    user.last_login = time.ctime()
    return jsonify(errno=RET.OK, errmsg="登陆成功")


@passport_blueprint.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("nick_name", None)
    session.pop("mobile", None)
    return jsonify(errno=RET.OK, errmsg="OK")




