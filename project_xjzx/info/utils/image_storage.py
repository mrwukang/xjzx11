# -*- coding: utf-8 -*-
import logging
from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'

# 要上传的空间
bucket_name = 'ihome'


def storage(data):
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        ret, info = put_data(token, None, data)

    except Exception as e:
        logging.error(e)
        raise e
    if info and info.status_code != 200:
        raise Exception("上传到七牛云失败")

    return ret["key"]


