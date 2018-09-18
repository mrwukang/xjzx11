# -*- coding:utf-8 -*-

from datetime import datetime
import random
import re

from flask import request, current_app, make_response, jsonify, session

from info import redis_store, constants, db
from info.models import User
from info.modules.passport import passport_blueprint
from info.response_code import RET
from info.utils.sms import send_template_sms


from libs.captcha.captcha import captcha


@passport_blueprint.route("/image_code")
def get_image_code():
    """生成图片验证码"""

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
    """发送六位验证码并发送到注册者手机"""

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
        # 查询手机号是否已经被注册
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已注册")

    # 生成验证码，其实过于简单了，最好能有加密
    sms_code = str(random.randint(100000, 999999))
    print(sms_code)

    # 这是发送短信验证码的测试功能
    # result = send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    # if result != 0:
    #     # 发送短信失败
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    try:
        # 将验证码保存到redis中，留着下次校验用
        redis_store.setex("SMS_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据存入数据库失败")
    return jsonify(errno=RET.OK, errmsg="生成验证码成功")


@passport_blueprint.route("/register", methods=["POST"])
def register():
    """注册功能"""

    param_dict = request.json
    sms_code = param_dict.get("smscode")
    password = param_dict.get("password")
    mobile = param_dict.get("mobile")
    if not all([sms_code, password, mobile]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    sms_code_redis = redis_store.get("SMS_" + mobile)

    if not sms_code_redis:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    sms_code_redis = sms_code_redis.decode()

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
        登录功能
        1. 获取参数和判断是否有值
        2. 从数据库查询出指定的用户
        3. 校验密码
        4. 保存用户登录状态
        5. 返回结果
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
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库连接失败")
    return jsonify(errno=RET.OK, errmsg="登陆成功")


@passport_blueprint.route("/logout", methods=["POST"])
def logout():
    """退出普通用户登录功能"""

    session.pop("user_id", None)
    session.pop("nick_name", None)
    session.pop("mobile", None)
    return jsonify(errno=RET.OK, errmsg="OK")




