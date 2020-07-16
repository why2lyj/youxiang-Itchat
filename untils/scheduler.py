# coding=utf-8
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from untils import config
from coupon.tb import tb_share_text
from coupon.jd import jingfen_query
from coupon.pdd import pdd_share_text
from coupon.sn import sn_share_text

def job_tasks():

    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    tb_job_tasks(scheduler)
    jd_job_task(scheduler)
    pdd_job_task(scheduler)
    sn_job_task(scheduler)

    # 加一个监控
    scheduler.add_listener(scheduler_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()

def tb_job_tasks(scheduler):

    conf = config.get_yaml()
    conf = conf.get('taobao')
    if not conf.get('is_open'):
        return

    if conf.get('app_key') =='' or conf.get('appSecret') =='' or conf.get('adzone_id') =='':
        return

    app_key = conf.get('app_key')
    app_secret = conf.get('app_secret')
    adzone_id = conf.get('adzone_id')

    chat_groups = conf.get('chat_groups')
    for chat_group in chat_groups:
        print(chat_group['group_name'])
        scheduler.add_job(func=jingfen_query,
                          kwargs={'group_name': chat_group['group_name'], 'group_material_id': chat_group['group_material_id'],
                                  'app_key': app_key, 'secret_key': app_secret, 'site_id': site_id, 'suo_mi_token': suo_im},
                          trigger='cron', hour=f'''{chat_group['hour']}''', minute=f'''{chat_group['minute']}''', second=0,  jitter=300, 
def  jd_job_task(scheduler):

    conf = config.get_yaml()
    conf = conf.get('jingdong')
    if not conf.get('is_open'):
        return

    if conf.get('app_key') =='' or conf.get('app_secret') =='' or conf.get('site_id') =='' or conf.get('suo_im') =='':
        return

    app_key = conf.get('app_key')
    app_secret = conf.get('app_secret')
    site_id = conf.get('site_id')
    suo_im = conf.get('suo_im')

    chat_groups = conf.get('chat_groups')
    for chat_group in chat_groups:
        print(chat_group['group_name'])
        scheduler.add_job(func=jingfen_query,
                          kwargs={'group_name': chat_group['group_name'], 'material_id': chat_group['group_material_id'],
                                  'app_key': app_key, 'app_secret': app_secret, 'site_id': site_id, 'suo_im': suo_im},
                          trigger='cron', hour=f'''{chat_group['hour']}''', minute=f'''{chat_group['minute']}''', second=0,  jitter=300, id=f'''{chat_group['group_name']}''')


def pdd_job_task(scheduler):

    conf = config.get_yaml()
    conf = conf.get('pinduoduo')
    if not conf.get('is_open'):
        return

    if conf.get('app_key') == '' or conf.get('app_secret') == '' or conf.get('p_id') == '':
        return

    app_key = conf.get('app_key')
    app_secret = conf.get('app_secret')
    p_id = conf.get('p_id')

    chat_groups = conf.get('chat_groups')
    for chat_group in chat_groups:
        print(chat_group['group_name'])
        scheduler.add_job(func=pdd_share_text,
                          kwargs={'group_name': chat_group['group_name'], 'group_material_id': chat_group['group_material_id'],
                                  'app_key': app_key, 'secret_key': app_secret, 'p_id': p_id},
                          trigger='cron', hour=f'''{chat_group['hour']}''', minute=f'''{chat_group['minute']}''', second=0,  jitter=0, id=f'''{chat_group['group_name']}''')

def sn_job_task(scheduler):

    conf = config.get_yaml()
    conf = conf.get('suning')
    if not conf.get('is_open'):
        return

    if conf.get('app_key') == '' or conf.get('app_secret') == '' or conf.get('ad_book_id') == '':
        return

    app_key = conf.get('app_key')
    app_secret = conf.get('app_secret')
    ad_book_id = conf.get('ad_book_id')

    chat_groups = conf.get('chat_groups')
    for chat_group in chat_groups:
        print(chat_group['group_name'])
        scheduler.add_job(func=sn_share_text,
                          kwargs={'group_name': chat_group['group_name'], 'group_material_id': chat_group['group_material_id'],
                                  'app_key': app_key, 'secret_key': app_secret, 'ad_book_id': ad_book_id},
                          trigger='cron', hour=f'''{chat_group['hour']}''', minute=f'''{chat_group['minute']}''', second=0,  jitter=0, id=f'''{chat_group['group_name']}''')


def scheduler_listener(event):
    '''
    监听程序，如果发现错误程序终止
    :param event:
    :return:
    '''
    if event.exception:
        print(f'''Error: JOB_ID: {event.job_id}, 运行时间：{(event.scheduled_run_time).strftime("%Y-%m-%d %H:%M:%S.%f")[0:19]}, 任务出错了！所有程序暂停！''')
        # 别闹，不会暂停，就是一轮错误罢了。
    else:
        print(f'''Success: JOB_ID: {event.job_id}, 运行时间：{(event.scheduled_run_time).strftime("%Y-%m-%d %H:%M:%S.%f")[
                                                       :-3]}, 任务运行成功，继续运行...''')

if __name__ == '__main__':
    job_tasks()
