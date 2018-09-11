# -*- coding:utf-8 -*-
import random
import re

from flask import request, make_response, jsonify
from flask.globals import current_app, session

from info.modules.passport import passport_blueprint
from info import redis_store
from info import constants
from info.response_code import RET
from info.models import User
from info import db
from libs.captcha.captcha import captcha


@passport_blueprint.route("/image_code")
def get_image_code():
    code_id = request.args.get("code_id")
    name, text, image = captcha.generate_captcha()
    print(text)
    redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

    # 返回响应内容
    response = make_response(image)
    # 设置内容类型
    response.headers['Content-Type'] = 'image/png'
    return response


@passport_blueprint.route("/sms_code", methods=["POST"])
def send_smscode():
    """
        1. 接收参数并判断是否有值
        2. 校验手机号是正确
        3. 通过传入的图片编码去redis中查询真实的图片验证码内容
        4. 进行验证码内容的比对
        5. 生成发送短信的内容并发送短信
        6. redis中保存短信验证码内容
        7. 返回发送成功的响应
        :return:
        """

    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.NODATA, errmsg="参数不全")
    if not re.match(r"^1[3-9]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号码格式错误")
    try:
        image_code_redis = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取验证码出错")
    if not image_code_redis:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")
    image_code_redis = image_code_redis.decode()
    redis_store.delete('ImageCode_' + image_code_id)
    if image_code.lower() != image_code_redis.lower():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机号已被注册")
    smscode = str(random.randint(100000, 999999))
    redis_store.setex("SMS_"+mobile, constants.SMS_CODE_REDIS_EXPIRES, smscode)

    print(smscode)
    return jsonify(errno=RET.OK, errmsg="验证码发送成功")


@passport_blueprint.route("/register", methods=["POST"])
def register():
    """
       1. 获取参数和判断是否有值
       2. 从redis中获取指定手机号对应的短信验证码的
       3. 校验验证码
       4. 初始化 user 模型，并设置数据并添加到数据库
       5. 保存当前用户的状态
       6. 返回注册的结果
       :return:
       """
    param_dict = request.json

    mobile = param_dict.get("mobile")
    smscode = param_dict.get("smscode")
    password = param_dict.get("password")
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if not re.match(r"^1[3-9]\d{9}$", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号码格式错误")
    try:
        smscode_redis = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.errr(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取本地验证码失败")
    if not smscode_redis:
        return jsonify(errno=RET.DATAERR, errmsg="验证码已过期")
    smscode_redis = smscode_redis.decode()
    if smscode != smscode_redis:
        return jsonify(errno=RET.DATAERR, errmsg="验证码错误")
    try:
        redis_store.delete("SMS_"+mobile)
    except Exception as e:
        current_app.logger.errr(e)

    print(password)

    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.errr(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    return jsonify(errno=RET.OK, errmsg="创建用户成功")






