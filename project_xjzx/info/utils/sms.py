# -*- coding: utf-8 -*-
from libs.ytx_sdk.CCPRestSDK import REST
import configparser

accountSid = '8a216da865ae11f80165b9202a260529'
# 说明：主账号，登陆云通讯网站后，可在控制台首页中看到开发者主账号ACCOUNT SID。

accountToken = '3e100bf6b9724243b359b8aebc9499a9'
# 说明：主账号Token，登陆云通讯网站后，可在控制台首页中看到开发者主账号AUTH TOKEN。

appId = '8a216da865ae11f80165b9202a840530'
# 请使用管理控制台中已创建应用的APPID。

serverIP = 'app.cloopen.com'
# 说明：请求地址，生产环境配置成app.cloopen.com。

serverPort = '8883'
# 说明：请求端口 ，生产环境为8883.

softVersion = '2013-12-26'  # 说明：REST API版本号保持不变。


def send_template_sms(to, datas, temp_id):
    """发送模板短信"""
    # @param to 手机号码
    # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
    # @param temp_id 模板Id
    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, temp_id)

    # 如果云通讯发送短信成功，返回的字典数据result中statuCode字段的值为"000000"
    if result.get("statusCode") == "000000":
        # 返回0 表示发送短信成功
        return 0
    else:
        # 返回-1 表示发送失败
        return -1
