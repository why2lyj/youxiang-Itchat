'''
用suo_mi短址的原因是因为京东使用短址的api需要申请，申请的门槛我放到这里：

a)      流量稳定且具备一定推广规模的联盟会员，无违规行为，接受业绩考核。

b)      会员申请标准：开通后两个月内的月订单量>3万单 或 月点击量>30万次

c)      如开通后2个自然月内如无返回数据，或月订单量达不到要求的，联盟平台将可以关闭高级权限。


就上面第二条是我未来所期待的，所以折中选了个其他短址的
'''

import random
import json
from untils.jd_api import JdApiClient
from untils.suo_im import Suo_mi
from untils.common import save_pic, del_pic
import itchat

def jingfen_query(group_name:str, group_material_id:str, app_key:str, secret_key:str, site_id:str, suo_mi_token:str):
    ''' 方法效率不咋地，不管了
    https://union.jd.com/openplatform/api/10421
    :return:
    '''
    info = []
    page_no = str(random.randint(1, 25))
    page_size = str(random.randint(3, 5))  # 不建议发很多，图片接口会跪

    client = JdApiClient(app_key=app_key, secret_key=secret_key)
    resp = client.call("jd.union.open.goods.jingfen.query",
                       {"goodsReq":
                            {"sort": "desc",
                             "pageSize": page_size,
                             "pageIndex": page_no,
                             "eliteId": group_material_id
                             }})
    # pprint.pprint(json.loads(resp.json()['jd_union_open_goods_jingfen_query_response']['result']))
    for data in json.loads(resp.json()['jd_union_open_goods_jingfen_query_response']['result'])['data']:
        sku_name = data['skuName']   ## 商品全名
        sku_id = data['skuId']     ## 商品 sku
        material_url = f'''http://{(data['materialUrl'])}''' ## 商品url

        couponInfos = data['couponInfo'] ## 优惠券列表
        # 查找最优优惠券
        for couponInfo in couponInfos['couponList']:
            if int(couponInfo['isBest']) == 1:
                discount = couponInfo['discount']  ## 优惠券额度
                coupon_link = couponInfo['link']  ## 优惠券领取地址

        price = data['priceInfo']['price'] ## 商品价格
        lowest_coupon_price = data['priceInfo']['lowestCouponPrice']  ## 商品价格

        # print(skuName)
        # print(skuId)
        # print(discount)
        # print(coupon_link)
        # print(price)
        # print(materialUrl)

        ## 获取 images
        image_list = []
        images_count = 0
        for image in data['imageInfo']['imageList']:
            images_count += 1
            if images_count > 3: ## 3个以上图片就不发了
                pass
            else:
                image_url = image['url']
                filename = save_pic(image_url, sku_id)
                groups = itchat.search_chatrooms(name=f'''{group_name}''')
                for room in groups:
                    room_name = room['UserName']
                    itchat.send('@img@%s' % (f'''{filename}'''), room_name)
                del_pic(filename)
                # print(image_url)

        # 得到短址
        duanzhi = tb_share_text(app_key, secret_key, material_url, coupon_link, site_id, suo_mi_token)
        # print(duanzhi)
        share_text = f'''【京东】{sku_name}\n——————————\n  【原价】¥{price}\n 【爆款价】¥{lowest_coupon_price}\n抢购地址：{duanzhi}'''

        groups = itchat.search_chatrooms(name=f'''{group_name}''')
        for room in groups:
            room_name = room['UserName']
            itchat.send(share_text, room_name)

def tb_share_text(app_key, secret_key, material_url, coupon_url, site_id, suo_mi_token):
    '''
    :param material_url: 物料的url
    :param coupon_url:  优惠券的url
    :param site_id:  网站id
    :param suo_mi_token: suo_mi网站的token
    :return: string ，返回一个suo_mi的短址
    '''
    client = JdApiClient(app_key=app_key, secret_key=secret_key)

    resp = client.call("jd.union.open.promotion.common.get",
                       {"promotionCodeReq":
                            {
                             "siteId": site_id,
                             "materialId": material_url,
                             "couponUrl": coupon_url
                             }})
    x = json.loads(resp.json()['jd_union_open_promotion_common_get_response']['result'])['data']['clickURL']

    # 直接返回短址
    url = x
    c = Suo_mi(app_key=suo_mi_token).get_short_url(url)
    return c

if __name__ == '__main__':
    jingfen_query()