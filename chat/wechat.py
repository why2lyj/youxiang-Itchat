# coding=utf-8

"""

"""
import time
import platform
import os
import re
import random
import itchat
from itchat.content import (
    TEXT,
    FRIENDS,
    NOTE,
    PICTURE
)

from collections import OrderedDict
from untils import config
from untils.scheduler import job_tasks
from chat.itchatHelper import init_wechat_config, set_system_notice
from chat.message import handle_friends_message, handle_groups_message, handle_group_pictures

__all__ = ['run', 'delete_cache']

group_infos_dict = OrderedDict()  # 群信息字典

def run():
    """ 主运行入口 """
    conf = config.init()
    # conf = get_yaml()
    if not conf:  # 如果 conf，表示配置文件出错。
        print('程序中止...')
        return
    # 判断是否登录，如果没有登录则自动登录，返回 False 表示登录失败
    print('开始登录...')
    if not is_online(auto_login=True):
        print('程序已退出...')
        return


def is_online(auto_login=False):
    """
    判断是否还在线。
    :param auto_login: bool,当为 Ture 则自动重连(默认为 False)。
    :return: bool,当返回为 True 时，在线；False 已断开连接。
    """

    def _online():
        """
        通过获取好友信息，判断用户是否还在线。
        :return: bool,当返回为 True 时，在线；False 已断开连接。
        """
        try:
            if itchat.search_friends():
                return True
        except IndexError:
            return False
        return True

    if _online(): return True  # 如果在线，则直接返回 True
    if not auto_login:  # 不自动登录，则直接返回 False
        print('微信已离线..')
        return False

    hotReload = False  #
    loginCallback = init_data
    exitCallback = exit_msg
    try:
        for _ in range(2):  # 尝试登录 2 次。
            if platform.system() in ('Windows', 'Darwin'):
                itchat.auto_login(hotReload=hotReload,
                                  loginCallback=loginCallback, exitCallback=exitCallback)
                itchat.run(blockThread=True)
            else:
                # 命令行显示登录二维码。
                itchat.auto_login(enableCmdQR=2, hotReload=hotReload, loginCallback=loginCallback,
                                  exitCallback=exitCallback)
                itchat.run(blockThread=True)
            if _online():
                print('登录成功')
                return True
    except Exception as exception:  # 登录失败的错误处理。
        sex = str(exception)
        if sex == "'User'":
            print('此微信号不能登录网页版微信，不能运行此项目。没有任何其它解决办法！可以换个号再试试。')
        else:
            print(sex)

    delete_cache()  # 清理缓存数据
    print('登录失败。')
    return False


def delete_cache():
    """ 清除缓存数据，避免下次切换账号时出现 """
    file_names = ('QR.png', 'itchat.pkl')
    for file_name in file_names:
        if os.path.exists(file_name):
            os.remove(file_name)


def init_data():
    """ 初始化微信所需数据 """
    set_system_notice('登录成功')
    itchat.get_friends(update=True)  # 更新好友数据。
    itchat.get_chatrooms(update=True)  # 更新群聊数据。

    conf = config.get('group_helper_conf')
    group_name_list = conf.get('group_name_white_list')

    init_chatsroom(group_name_list)
    init_wechat_config()  # 初始化所有配置内容
    init_alarm()

    print('初始化完成，开始正常工作。')

def init_chatsroom(group_name_list):

    uidlist_compile = re.compile(
        r"(?<!'Self': )\<ChatroomMember:.*?'UserName': '(.*?)', 'NickName'.*?")  # 筛选出群所有用户的 uid
    for group_name in group_name_list:
        group_list = itchat.search_chatrooms(name=group_name)  # 通过群聊名获取群聊信息
        group_info = {}
        if group_list:
            group_uuid = group_list[0]['UserName']
            group = itchat.update_chatroom(group_uuid, detailedMember=True)  # 通过群id更新群名单
            group_uuid = group['UserName']  # 群聊 id
            group_info['group_name'] = group_name  # 群聊名称
            group_info['group_uuid'] = group_uuid  # 群聊 uuid
            count = len(group['MemberList'])  # 群聊人数
            group_info['count'] = count
            member_uid_list = uidlist_compile.findall(str(group))  # 根据正则取出群组里所有用户的 uuid。也可以用循环的方式。
            if member_uid_list:
                group_info['member_uid_list'] = member_uid_list
            group_infos_dict[group_uuid] = group_info

def init_alarm():
    """
    初始化定时任务
    :param alarm_dict: 定时相关内容
    """
    # 定时任务
    job_tasks()

@itchat.msg_register([TEXT])
def text_reply(msg):
    """ 监听用户消息，用于自动回复 """
    handle_friends_message(msg)

@itchat.msg_register([PICTURE], isGroupChat=True)
def picture_register(msg):
    """ 监听群消息发来的图片消息 """
    handle_group_pictures(msg)

@itchat.msg_register([TEXT], isGroupChat=True)
def text_group(msg):
    """ 监听群消息，用于自动回复 """
    handle_groups_message(msg)

@itchat.msg_register(FRIENDS)
def add_friends_msg(msg):
    """ 监听添加好友请求 为了自动同意好友请求
    """

    conf = config.get('auto_reply_info')
    IS_AUTO_ADD_FRIEND = conf.get('is_auto_add_friend')

    add_friend_keys = ''.join(conf.get('auto_add_friend_keywords'))
    note_first_meet_text = '''等你等的好辛苦，很高心您的加入！

    '''  # 好友成功后的第一句话
    add_friend_compile = re.compile('|'.join(i.strip() for i in
                                             re.split(r'[,，]+', add_friend_keys) if i), re.I)  # 通过关键词同意加好友请求

    itchat.get_friends(update=True)  # 更新好友数据。

    if not IS_AUTO_ADD_FRIEND:  # 如果是已关闭添加好友功能，则直接返回
        return

    userid = msg['RecommendInfo']['UserName']
    nickname = msg['RecommendInfo']['NickName']

    content = msg['RecommendInfo']['Content']  # 获取验证消息
    if add_friend_compile.findall(content):
        time.sleep(random.randint(1, 2))  # 随机休眠（1~3）秒，用于防检测机器人
        itchat.add_friend(**msg['Text'])  # 同意加好友请求
        time.sleep(random.randint(1, 2))
        itchat.send(note_first_meet_text, userid)  # 给刚交的朋友发送欢迎语句
        note = '已添加好友：{}'.format(nickname)
        set_system_notice(note)
    else:
        note = '添加好友失败：用户「{}」 发来的验证消息「{}」。'.format(nickname, content)
        set_system_notice(note)

@itchat.msg_register([NOTE], isGroupChat=True)
def group_note_msg(msg):
    """ 群通知处理

    邀请进来的和扫二维码进来的进行提示
    """
    invite_compile = re.compile(r'"(.*?)"邀请"(.*?)"加入了群聊\s*$')
    scan_invite_compile = re.compile(r'"(.*?)"通过扫描"(.*?)"分享的二维码加入群聊\s*$')
    scan_my_invite_compile = re.compile(r'"(.*?)"通过扫描你分享的二维码加入群聊\s*$')

    group_uuid = msg['FromUserName']  # 获取当前群的 uuid
    if group_uuid in group_infos_dict:  # 判断是否为同一个群组
        text = msg['Text']  # 通知的内容
        invite_names = scan_my_invite_compile.findall(text)  # 判断是我邀请的
        scan_invite = scan_invite_compile.findall(text)  ## 判断是否是群内人员通过二维码邀请而入
        others_invite = invite_compile.findall(text)  ## 判断是否是群内人员邀请直接邀请而入
        if invite_names:  # 用于邀请
            invite_name = invite_names[0]  # 加入者的昵称
            time.sleep(random.randint(1, 2))

            note_invite_welcome = f'''@{invite_name}\u2005 \n欢迎加入群，请查看群规
① 此群禁止发广告，聊天请随意
② 请勿发涉黄，涉政，辱骂性话语
③ 允许拉小伙伴进来，记得加管理员

请主动维护群内秩序，若有违反，直送飞机票。
如需要帮助请主动联系管理员。
            '''
            itchat.send(note_invite_welcome, group_uuid)  # 向群里发送欢迎语句

        invite_list = scan_invite or others_invite
        if invite_list:
            invite_name = invite_list[0][0]  # 加入者的昵称
            inviter_name = invite_list[0][1]  # 邀请者的昵称
            time.sleep(random.randint(1, 2))

            note_invite_welcome = f'''@{invite_name}\u2005 \n欢迎加入群，请查看群规
① 此群禁止发广告，聊天请随意
② 请勿发涉黄，涉政，辱骂性话语
③ 允许拉小伙伴进来，记得加管理员

@{inviter_name}\u2005
请主动约束受邀好友：{invite_name}，若其违反上述约定，送连坐飞机票！
如需要帮助请主动联系管理员。
                        '''
            itchat.send(note_invite_welcome, group_uuid)  # 向群里发送欢迎语句
            return

def exit_msg():
    """ 退出通知 """
    print('程序已退出')

if __name__ == '__main__':
    run()
