import datetime
import requests
import hashlib
import json

JD_API_ROOT = 'https://api.jd.com/routerjson'

class JdApiClient(object):
    def __init__(self, app_key, secret_key):
        self.app_key = app_key
        self.secret_key = secret_key

    def get_sign(self, params):
        params_list = sorted(list(params.items()), key=lambda x: x[0])
        params_bytes = (self.secret_key + ''.join("%s%s" % (k, v) for k, v in params_list) + self.secret_key).encode('utf-8')
        sign = hashlib.md5(params_bytes).hexdigest().upper()
        return sign

    def call(self, method, param_json, **kwargs):
        params = {
            "v": "1.0",
            "method": method,
            "app_key": self.app_key,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "sign_method": "md5"
        }
        if isinstance(param_json, (dict, list)):
            params["param_json"] = json.dumps(param_json)
        else:
            params["param_json"] = param_json
        params['sign'] = self.get_sign(params)
        resp = requests.get(JD_API_ROOT, params=params, **kwargs)
        return resp

    def jd_union_open_goods_jingfen_query(self):
        '''
        https://union.jd.com/openplatform/api/10421
        :return:
        '''
        return
