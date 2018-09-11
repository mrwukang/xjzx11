# -*- coding:utf-8 -*-

from flask import request, make_response

from info.modules.passport import passport_blueprint
from info import redis_store
from info import constants
from libs.captcha.captcha import captcha
from info.response_code import RET


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

    print(1111111)


