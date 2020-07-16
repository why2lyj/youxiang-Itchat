'''
'''

import random
import time
from untils.common import save_pic, del_pic
import itchat
import suning.api as api
from chat.itchatHelper import set_system_notice

def sn_share_text(group_name: str, group_material_id: str, app_key:str, secret_key:str, ad_book_id: str):
    '''
    :param group_name:
    :param material_id:
    :return:
    '''
    try:
        offset = str(random.randint(1, 71))
        limit = str(random.randint(5, 10))
        print(f'''offset:{offset},limit:{limit}''')
        client = api.RecommendcommodityQueryRequest()
        client.setDomainInfo("open.suning.com", "80")
        client.setAppInfo(app_key, secret_key)
        client.couponMark = '1'
        client.pageIndex = offset
        client.size = limit
        resp = client.getResponse()['sn_responseContent']['sn_body']['queryRecommendcommodity']
        for data in resp:
            title = data['commodityInfo']['commodityName'] # 商品名称
            commodityCode = data['commodityInfo']['commodityCode'] # 商品编码
            supplierCode = data['commodityInfo']['supplierCode'] # 店铺编码
            sellingPoint = data['commodityInfo']['sellingPoint'] # 卖点
            snPrice = data['commodityInfo']['snPrice'] # 原价
            commodityPrice = data['commodityInfo']['commodityPrice'] # 内部价
            baoyou = data['commodityInfo']['baoyou'] # 内部价
            if baoyou == 1:
                sellingPoint = f'''包邮 {sellingPoint} '''
            images_count = 0
            for image in data['commodityInfo']['pictureUrl']:
                images_count += 1
                if images_count > 3:  ## 3个以上图片就不发了
                    pass
                else:
                    image_url = image['picUrl'].replace('_200w_200h_4e','')
                    print(image_url)
                    groups = itchat.search_chatrooms(name=f'''{group_name}''')
                    for room in groups:
                        room_name = room['UserName']
                        time.sleep(random.randint(5, 10))
                        filename = save_pic(image_url, commodityCode)
                        itchat.send('@img@%s' % (f'''{filename}'''), room_name)
                    del_pic(filename)

            pgPrice = data['pgInfo']['pgPrice'] # 拼购价
            pgNum = data['pgInfo']['pgNum'] # 拼购价

            couponValue = data['couponInfo']['couponValue'] # 优惠券面额
            bounsLimit = data['couponInfo']['bounsLimit'] # 使用下限（满多少可用）
            afterCouponPrice = data['couponInfo']['afterCouponPrice'] # 使用下限（满多少可用）

            sn_share_url = promotion_url_generate(app_key, secret_key, ad_book_id, commodityCode, supplierCode.zfill(10))

            if pgPrice == '': #不是拼购单
                if couponValue == '': # 没有券
                    if float(snPrice) == float(commodityPrice):
                        share_text = f'''{sellingPoint}\n【苏宁】{title}\n——————————\n 【爆款价】¥{commodityPrice}\n抢购地址：\n{sn_share_url}'''
                    else:
                        share_text = f'''{sellingPoint}\n【苏宁】{title}\n——————————\n 【原价】¥{snPrice}\n【爆款价】¥{commodityPrice}\n抢购地址：\n{sn_share_url}'''
                else: # 有券
                    bounsLimit = float(bounsLimit)
                    couponValue = float(couponValue)
                    commodityPrice = float(commodityPrice)
                    if commodityPrice >= bounsLimit: # 如果商品满足满用券下限
                        if float(snPrice) == float(commodityPrice):
                            share_text = f'''{sellingPoint}\n【苏宁】{title}\n领券再减{data['couponInfo']['couponValue']}元！\n——————————\n 【券后内部价】¥{round(float(commodityPrice-couponValue),2)}\n抢购地址：\n{sn_share_url}'''
                        else:
                            share_text = f'''{sellingPoint}\n【苏宁】{title}\n领券再减{data['couponInfo']['couponValue']}元！\n——————————\n 【原价】¥{snPrice}\n【券后内部价】¥{round(float(commodityPrice-couponValue),2)}\n抢购地址：\n{sn_share_url}'''
                    else:
                        buy_count = int(bounsLimit // commodityPrice + 1)
                        if float(snPrice) == float(commodityPrice):
                            if float(commodityPrice)*buy_count - float(data['couponInfo']['couponValue']) <=0:
                                share_text = f'''{sellingPoint}\n【苏宁】{title}\n——————————\n 【爆款价】¥{afterCouponPrice}\n部分地区用户可领券再减，以实际优惠为准！[哇][哇]\n抢购地址：\n{sn_share_url}'''
                            else:
                                share_text = f'''{sellingPoint}\n【苏宁】{title}\n——————————\n 【爆款价】¥{commodityPrice}\n拍{buy_count}件，用券再减{data['couponInfo']['couponValue']}元！{buy_count}件约{round(float(commodityPrice)*buy_count - float(data['couponInfo']['couponValue']),2)}元！\n抢购地址：\n{sn_share_url}'''

                        else:
                            if float(commodityPrice) * buy_count - float(data['couponInfo']['couponValue']) <= 0:
                                share_text = f'''{sellingPoint}\n【苏宁】{title}\n——————————\n 【原价】¥{snPrice}\n【爆款价】¥{afterCouponPrice}\n部分地区用户可领券再减，具体以实际优惠为准！[哇][哇]\n抢购地址：\n{sn_share_url}'''
                            else:
                                share_text = f'''{sellingPoint}\n【苏宁】{title}\n——————————\n 【原价】¥{snPrice}\n【爆款价】¥{commodityPrice}\n拍{buy_count}件，用券再减{data['couponInfo']['couponValue']}元！{buy_count}件约{round(float(commodityPrice)*buy_count - float(data['couponInfo']['couponValue']),2)}元！\n抢购地址：\n{sn_share_url}'''
            else: # 拼购单
                if couponValue == '': # 没有券
                    if float(snPrice) == float(commodityPrice):
                        share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n——————————\n 【拼购价】¥{pgPrice}\n抢购地址：\n{sn_share_url}'''
                    else:
                        share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n——————————\n 【原价】¥{snPrice}\n【拼购价】¥{pgPrice}\n抢购地址：\n{sn_share_url}'''
                else: # 有券
                    bounsLimit = float(bounsLimit)
                    pgPrice = float(pgPrice)
                    if pgPrice >= bounsLimit:# 如果拼购价格满足满用券下限
                        if float(snPrice) == float(pgPrice):
                            share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n领券再减{data['couponInfo']['couponValue']}元！\n——————————\n 【券后拼购价】¥{pgPrice}\n抢购地址：\n{sn_share_url}'''
                        else:
                            share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n领券再减{data['couponInfo']['couponValue']}元！\n——————————\n 【原价】¥{snPrice}\n【券后拼购价】¥{pgPrice}\n抢购地址：\n{sn_share_url}'''
                    else:
                        buy_count = int(bounsLimit // pgPrice + 1)
                        if float(snPrice) == float(commodityPrice):
                            if float(commodityPrice) * buy_count - float(data['couponInfo']['couponValue']) <= 0:
                                share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n——————————\n 【爆款价】¥{afterCouponPrice}\n部分地区用户可领券再减，以实际优惠为准！[哇][哇]\n抢购地址：\n{sn_share_url}'''
                            else:
                                share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n——————————\n 【爆款价】¥{commodityPrice}\n拍{buy_count}件，用券再减{data['couponInfo']['couponValue']}元！{buy_count}件约{round(float(commodityPrice)*buy_count - float(data['couponInfo']['couponValue']),2)}元！\n抢购地址：\n{sn_share_url}'''
                        else:
                            if float(commodityPrice) * buy_count - float(data['couponInfo']['couponValue']) <= 0:
                                share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n——————————\n 【原价】¥{snPrice}\n【爆款价】¥{afterCouponPrice}\n部分地区用户可领券再减，以实际优惠为准！[哇][哇]\n抢购地址：\n{sn_share_url}'''
                            else:
                                share_text = f'''{sellingPoint}\n【苏宁{pgNum}人拼购】{title}\n——————————\n 【原价】¥{snPrice}\n【爆款价】¥{commodityPrice}\n拍{buy_count}件，用券再减{data['couponInfo']['couponValue']}元！{buy_count}件约{round(float(commodityPrice)*buy_count - float(data['couponInfo']['couponValue']),2)}元！\n抢购地址：\n{sn_share_url}'''

            groups = itchat.search_chatrooms(name=f'''{group_name}''')
            for room in groups:
                room_name = room['UserName']
                time.sleep(random.randint(3, 5))
                print(share_text)
                itchat.send(share_text, room_name)

    except Exception as e:
        print(e)
        set_system_notice(f'''苏宁：offset: {offset},\nlimit:{limit}\n\n发现问题''')
        sn_share_text(group_name, group_material_id, app_key, secret_key, ad_book_id)

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
        set_system_notice(f'''comm_code: {comm_code},\nmert_code:{mert_code}\nad_book_id:{ad_book_id}\n\n无法获取推广连接''')
        short_url = ""
    return short_url

if __name__ == '__main__':
    pass
