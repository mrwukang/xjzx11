#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import request, make_response, session

from info import redis_store
from info import constants
from info.modules.passport import passport_blueprint
from info.utils.captcha.captcha import captcha


@passport_blueprint.route("/image_code")
def get_image_code():
    code_id = request.args.get("code_id")
    name, text, image = captcha.generate_captcha()
    session['image_code'] = text
    # redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)


    # 返回响应内容
    response = make_response(image)
    # 设置内容类型
    response.headers['Content-Type'] = 'image/jpg'
    return response
