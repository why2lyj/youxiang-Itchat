import pprint
import json
from untils.jd_api import JdApiClient

def jingfen_query():
    '''
    https://union.jd.com/openplatform/api/10421
    :return:
    '''
    client = JdApiClient("", "")
    resp = client.call("jd.union.open.goods.jingfen.query",
                       {"goodsReq":
                            {"sort": "desc",
                             "pageSize": "2",
                             "pageIndex": "1",
                             "eliteId": "31",
                             "sortName": "inOrderCount30DaysSku"
                             }})
    # pprint.pprint(json.loads(resp.json()['jd_union_open_goods_jingfen_query_response']['result']))
    for data in json.loads(resp.json()['jd_union_open_goods_jingfen_query_response']['result'])['data']:
        skuName = data['skuName']   ## 商品全名
        skuId = data['skuId']     ## 商品 sku
        materialUrl = f'''http://{(data['materialUrl'])}''' ## 商品url

        couponInfos = data['couponInfo'] ## 优惠券列表
        # 查找最优优惠券
        for couponInfo in couponInfos['couponList']:
            if int(couponInfo['isBest']) == 1:
                discount = couponInfo['discount']  ## 优惠券额度
                coupon_link = couponInfo['link']  ## 优惠券领取地址

        price = data['priceInfo']['price'] ## 商品价格

        print(skuName)
        print(skuId)
        print(discount)
        print(coupon_link)
        print(price)
        print(materialUrl)

        ## 获取 images
        for image in data['imageInfo']['imageList']:
            image_url = image['url']
            print(image_url)


        print('-----------------------------------')
# def share_text():

def tb_share_text():
    raise NotImplementedError

if __name__ == '__main__':
    jingfen_query()