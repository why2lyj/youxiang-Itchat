import time
import json
import itchat
import random
from untils.common import save_pic, del_pic
from untils.pdd_api import PddApiClient
from chat.itchatHelper import set_system_notice

def pdd_share_text(group_name: str, group_material_id: str, app_key:str, secret_key:str, p_id: str):
    '''
    :param group_name:
    :param material_id:
    :return:
    '''
    try:
        offset = str(random.randint(1, 295)) # top.goods.list.query 好像只有300个商品
        limit = str(random.randint(3, 5))  #

        client = PddApiClient(app_key=app_key, secret_key=secret_key)
        resp = client.call("pdd.ddk.top.goods.list.query",
                                {"offset": offset,
                                 "limit": limit,
                                 "p_id": p_id
                                 })
    except Exception as e:
        print(e)
        set_system_notice(f'''offset: {offset},\nlimit:{limit}\n\n发现问题''')
        pdd_share_text(group_name, group_material_id, app_key, secret_key, secret_key, p_id)

    for data in json.loads(resp.text)['top_goods_list_get_response']['list'] :
        goods_id = data['goods_id']
        goods_name = data['goods_name']
        search_id = data['search_id']
        goods_thumbnail_url = data['goods_thumbnail_url']
        min_normal_price = int(data['min_normal_price']) # 现价
        coupon_discount = int(data['coupon_discount']) # 券价
        min_normal_price_str = str(min_normal_price)[:len(str(min_normal_price))-2] + '.' + str(min_normal_price)[len(str(min_normal_price))-2:]
        price = str(min_normal_price - coupon_discount)[:len(str(min_normal_price - coupon_discount))-2] + '.' \
                + str(min_normal_price - coupon_discount)[len(str(min_normal_price - coupon_discount))-2:]
        short_url = promotion_url_generate(app_key=app_key, secret_key=secret_key, p_id=p_id, goods_id_list=int(goods_id), search_id= search_id)

        groups = itchat.search_chatrooms(name=f'''{group_name}''')
        for room in groups:
            group_name = room['UserName']
            time.sleep(random.randint(1, 5))
            filename = save_pic(goods_thumbnail_url, goods_id)
            # 发送图片
            itchat.send('@img@%s' % (f'''{filename}'''), group_name)
            time.sleep(random.randint(1, 3))
            itchat.send(f''' {goods_name} \n【在售价】¥{min_normal_price_str}\n【券后价】¥{price}\n-----------------\n抢购地址:\n{short_url}''', group_name)
            del_pic(filename)


def promotion_url_generate(app_key:str, secret_key:str, p_id: str, goods_id_list: int, search_id:str):
    client = PddApiClient(app_key=app_key, secret_key=secret_key)
    resp = client.call("pdd.ddk.goods.promotion.url.generate",
                       {"goods_id_list": f'''[{goods_id_list}]''',
                        "search_id": search_id,
                        "p_id": p_id
                        })
    try:
        short_url = json.loads(resp.text)['goods_promotion_url_generate_response']['goods_promotion_url_list'][0]['short_url']
    except Exception as e:
        print(e)
        set_system_notice(f'''goods_id_list: {goods_id_list},\nsearch_id:{search_id}\np_id:{p_id}\n\n无法获取连接''')
        short_url = ""
    return short_url

if __name__ == '__main__':
    pass
