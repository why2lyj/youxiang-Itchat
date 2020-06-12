# -*- coding: utf-8 -*-
"""

"""
import re
import time
import random
import itchat
from untils import config
from untils.common import del_pic
from untils.ad import QRcode_detection
from chat.itchatHelper import set_system_notice, is_white_group
from untils.common import FILEHELPER
from untils.qq_nlpchat import get_auto_reply

__all__ = ['handle_friends_message', 'handle_groups_message']

at_compile = r'(@.*?\s{1,}).*?'

help_complie = r'^(?:0|帮忙|帮助|help)\s*$'

common_msg = '@{ated_name}\u2005\n{text} \n     ----机器人智能回复 \n    您如有事儿加机器人问话吧'

help_group_content = """@{ated_name}
群助手功能：

有啥事儿问管理员吧，群功能不开放

"""

def handle_friends_message(msg):
    """ 处理好友信息 """
    try:
        # 自己通过手机微信发送给别人的消息(文件传输助手除外)不作处理。
        if msg['FromUserName'] == config.get('wechat_uuid') and msg['ToUserName'] != FILEHELPER:
            return

        conf = config.get('auto_reply_info')
        if not conf.get('is_auto_reply'):
            return
        # 获取发送者的用户id
        uuid = FILEHELPER if msg['ToUserName'] == FILEHELPER else msg['FromUserName']
        is_all = conf.get('is_auto_reply_all')
        auto_uuids = conf.get('auto_reply_black_uuids') if is_all else conf.get('auto_reply_white_uuids')
        # 开启回复所有人，当用户是黑名单，不回复消息
        if is_all and uuid in auto_uuids:
            return

        # 关闭回复所有人，当用户不是白名单，不回复消息
        if not is_all and uuid not in auto_uuids:
            return

        receive_text = msg.text  # 好友发送来的消息内容
        # 好友叫啥，用于打印
        nick_name = FILEHELPER if uuid == FILEHELPER else msg.user.nickName
        reply_text = get_auto_reply(receive_text, uuid)  # 获取自动回复
        if reply_text:  # 如内容不为空，回复消息
            time.sleep(random.randint(1, 2))  # 休眠一秒，保安全。想更快的，可以直接注释。

            prefix = conf.get('auto_reply_prefix', '')  # 前缀
            if prefix:
                reply_text = '{}{}'.format(prefix, reply_text)

            suffix = conf.get('auto_reply_suffix', '')  # 后缀
            if suffix:
                reply_text = '{}{}'.format(reply_text, suffix)

            itchat.send(reply_text, toUserName=uuid)
        else:
            set_system_notice(f'''自动回复失败：\n『{nick_name}』发来信息：{receive_text} \n''')
    except Exception as exception:
        print(str(exception))


def handle_groups_message(msg):
    """
    处理群消息，
    :param msg:
    :return:
    """

    uuid = msg.fromUserName  # 群 uid
    ated_uuid = msg.actualUserName  # 艾特你的用户的uuid
    ated_name = msg.actualNickName  # 艾特你的人的群里的名称
    # print(msg)

    # 自己通过手机端微信发出的消息不作处理
    if ated_uuid == config.get('wechat_uuid'):
        return

    conf = config.get('group_helper_conf')
    text = msg['Text']  # 发送到群里的消息。
    # 如果是我们的群，不是管理组人员发送的消息，且长度大于30，直接踢
    # 我们认为 wechat 中一个人的聊天长度不会超过30，
    # 特别是对于一个优惠券群来说，
    # 一个可跟你说30个字以上的又如此“谆谆教导”的人值得被踢
    # 对于广告，宁可错杀不放过一个，随有极端但不菲是一种办法
    # TODO 此处需要文本审核，但市面上的文本审核都付费，如有免费的请及时通知我
    group_admins = conf.get('group_admin')
    if is_white_group(uuid) and (ated_name not in group_admins):
        if len(str(text)) >= 30:
            itchat.delete_member_from_chatroom(uuid, [{'UserName': msg.ActualUserName}])

    if not conf.get('is_open'):
        return

    # 如果开启了 『艾特才回复』，而群用户又没有艾特你。走垃圾分类
    if conf.get('is_at') and not msg.isAt:
        return

    is_all = conf.get('is_all', False)
    group_uuids = conf.get('group_name_black_list') if is_all else conf.get('group_name_white_list')
    # 开启回复所有群，而群组是黑名单，不处理消息
    if is_all:
        for group_name in group_uuids:
            chatrooms = itchat.search_chatrooms(name=f'''{group_name}''')
            # print(chatrooms)
            for room in chatrooms:
                if uuid == room['UserName']:
                    return

    # 未开启回复所有群，而群组不是白名单，不处理消息
    in_white_flag = False
    if not is_all:
        for group_name in group_uuids:
            chatrooms = itchat.search_chatrooms(name=f'''{group_name}''')
            for room in chatrooms:
                if uuid == room['UserName']:
                    in_white_flag = True
    if not in_white_flag:
        return

    # 去掉 at 标记
    text = re.sub(at_compile, '', text)

    reply_text = get_auto_reply(text, ated_uuid)  # 获取自动回复
    if reply_text:  # 如内容不为空，回复消息
        reply_text = common_msg.format(ated_name=ated_name, text=reply_text)
        itchat.send(reply_text, uuid)
        # print('回复{}：{}'.format(ated_name, reply_text))
    else:
        print('自动回复失败\n')

def handle_group_pictures(msg):
    '''
    :return:
    '''

    # 自己通过手机微信发送给别人的消息(文件传输助手除外)不作处理。
    if msg['FromUserName'] == config.get('wechat_uuid') and msg['ToUserName'] != FILEHELPER:
        return
    # 判断是否来自指定群
    uuid = msg.fromUserName  # 群 uid
    # print(f'''这个群聊的id是{uuid}''')
    # ated_uuid = msg.actualUserName  # 发送人的用户uuid
    # ated_name = msg.actualNickName  # 发送人群里的名称
    # file_name = msg['FileName'] # 文件默认文件名
    msg.download(msg.fileName)
    if is_white_group(uuid):
        if QRcode_detection(msg.fileName):
            itchat.delete_member_from_chatroom(msg.FromUserName, [{'UserName': msg.ActualUserName}])
    del_pic(msg.fileName)