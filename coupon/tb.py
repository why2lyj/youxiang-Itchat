import time
import json
import itchat
import random
from untils.common import save_pic, del_pic
from untils.tb_top_api import TbApiClient

def tb_share_text(group_name: str, material_id: str, app_key, app_secret, adzone_id):
    '''

    :param group_name:
    :param material_id:
    :return:
    '''
    try:
        material_id = str(random.choices(material_id.split(','))[0])
        print(material_id)
        groups = itchat.search_chatrooms(name=f'''{group_name}''')
        for room in groups:
            group_name = room['UserName']
            time.sleep(random.randint(1, 5))
            tb_client = TbApiClient(app_key=app_key, secret_key=app_secret, adzone_id=adzone_id)
            res = tb_client.taobao_tbk_dg_optimus_material(material_id)
            json_data = json.loads(res)['tbk_dg_optimus_material_response']['result_list']['map_data']
            count = 0
            for item in json_data:
                count += 1
                coupon_amount = 0
                coupon_share_url = ""
                title = ""
                if str(item).find("coupon_share_url") > -1:
                    coupon_share_url = "https:" + item['coupon_share_url']
                    coupon_amount = item['coupon_amount']
                    pict_url = "https:" + str(item['pict_url'])
                    title = item['title']
                    item_id = item['item_id']
                    filename = save_pic(pict_url, item_id)
                    zk_final_price = item['zk_final_price']
                    # 发送图片
                    itchat.send('@img@%s' % (f'''{filename}'''), group_name)

                    time.sleep(2)
                    itchat.send(f'''{title}\n【在售价】¥{zk_final_price}\n【券后价】¥{round(float(zk_final_price) - float(coupon_amount), 2)}''', group_name)
                    time.sleep(random.randint(1, 3))
                    text = f'''{tb_client.taobao_tbk_tpwd_create(title, coupon_share_url)}'''
                    start_index = text.find('￥')
                    itchat.send(f'''({text[start_index: 13+start_index]})''', group_name)
                    time.sleep(2)
                    del_pic(filename)
                else:
                    click_url = "https:" + item['click_url']
                    title = item['title']
                    item_id = item['item_id']
                    pict_url = "https:" + str(item['pict_url'])
                    zk_final_price = item['zk_final_price']
                    print(pict_url)
                    filename = save_pic(pict_url, item_id)
                    itchat.send('@img@%s' % (f'''{filename}'''), group_name)
                    time.sleep(2)
                    itchat.send(f'''{title}\n【在售价】¥{zk_final_price}\n【券后价】¥{round(float(zk_final_price) - float(coupon_amount), 2)}''', group_name)
                    time.sleep(random.randint(1, 3))
                    text = f'''{tb_client.taobao_tbk_tpwd_create(title, coupon_share_url)}'''
                    start_index = text.find('￥')
                    itchat.send(f'''({text[start_index: 13+start_index]})''', group_name)
                    time.sleep(2)
                    del_pic(filename)
                    time.sleep(2)
                    del_pic(filename)
    except Exception as e:
        print(e)
        tb_share_text(group_name, material_id, app_key, app_secret, adzone_id)


if __name__ == '__main__':
    print(f'''tb function''')
