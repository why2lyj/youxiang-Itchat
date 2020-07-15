'''

'''

import random
import time
import json
from untils.jd_api import JdApiClient
from untils.suo_im import Suo_mi
from untils.common import save_pic, del_pic
import itchat
import suning.api as api
from suning.api.netalliance import RecommendcommodityQueryRequest
from suning.api.netalliance import StorepromotionurlQueryRequest
from chat.itchatHelper import set_system_notice

def pdd_share_text(group_name: str, group_material_id: str, app_key:str, secret_key:str, ad_book_id: str):
    '''
    :param group_name:
    :param material_id:
    :return:
    '''
    try:
        offset = str(random.randint(1, 295))
        limit = str(random.randint(3, 5))
        client = api.RecommendcommodityQueryRequest()
        client.setDomainInfo("openpre.cnsuning.com", "80")
        client.setAppInfo(app_key, secret_key)
        client.couponMark = '1'
        client.pageIndex = offset
        client.size = limit
        resp= client.getResponse()

    except Exception as e:
        print(e)
        set_system_notice(f'''苏宁：offset: {offset},\nlimit:{limit}\n\n发现问题''')
        pdd_share_text(group_name, group_material_id, app_key, secret_key, secret_key, ad_book_id)

def promotion_url_generate(app_key:str, secret_key:str, ad_book_id: str, comm_code: int, mert_code:str):
    client = api.StorepromotionurlQueryRequest()
    client.setAppInfo(app_key, secret_key)
    client.setDomainInfo("open.suning.com", "80")
    client.adBookId = ad_book_id
    client.commCode = comm_code
    client.mertCode = mert_code
    client.urlType = '2'
    try:
        resp = client.getResponse()
        short_url = resp['sn_responseContent']['sn_body']['queryStorepromotionurl']['wapExtendUrl']
        short_url = short_url.replace('%3A%2F%2F', '://').replace('%2F', '/')
    except Exception as e:
        print(e)
        set_system_notice(f'''comm_code: {comm_code},\nmert_code:{mert_code}\nad_book_id:{ad_book_id}\n\n无法获取连接''')
        short_url = ""
    return short_url

if __name__ == '__main__':
    app_key = ''
    app_secret = ''
    ad_book_id = ''
    comm_code = ''
    mert_code = ''
    x = promotion_url_generate(app_key, app_secret, ad_book_id, comm_code, mert_code)
    print(x)