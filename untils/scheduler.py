# coding=utf-8
from dataclasses import dataclass
from importlib import import_module
from typing import Dict, Iterable, Tuple

from untils import config


@dataclass(frozen=True)
class PlatformJob:
    config_key: str
    required_keys: Tuple[str, ...]
    task_path: str
    kwargs_map: Dict[str, str]
    jitter: int = 300


PLATFORM_JOBS = {
    "taobao": PlatformJob(
        config_key="taobao",
        required_keys=("app_key", "app_secret", "adzone_id"),
        task_path="coupon.tb:tb_share_text",
        kwargs_map={
            "group_name": "group_name",
            "material_id": "group_material_id",
            "app_key": "app_key",
            "app_secret": "app_secret",
            "adzone_id": "adzone_id",
        },
    ),
    "jingdong": PlatformJob(
        config_key="jingdong",
        required_keys=("app_key", "app_secret", "site_id", "suo_im"),
        task_path="coupon.jd:jingfen_query",
        kwargs_map={
            "group_name": "group_name",
            "group_material_id": "group_material_id",
            "app_key": "app_key",
            "secret_key": "app_secret",
            "site_id": "site_id",
            "suo_mi_token": "suo_im",
        },
    ),
    "pinduoduo": PlatformJob(
        config_key="pinduoduo",
        required_keys=("app_key", "app_secret", "p_id"),
        task_path="coupon.pdd:pdd_share_text",
        kwargs_map={
            "group_name": "group_name",
            "group_material_id": "group_material_id",
            "app_key": "app_key",
            "secret_key": "app_secret",
            "p_id": "p_id",
        },
        jitter=0,
    ),
    "suning": PlatformJob(
        config_key="suning",
        required_keys=("app_key", "app_secret", "ad_book_id"),
        task_path="coupon.sn:sn_share_text",
        kwargs_map={
            "group_name": "group_name",
            "group_material_id": "group_material_id",
            "app_key": "app_key",
            "secret_key": "app_secret",
            "ad_book_id": "ad_book_id",
        },
        jitter=0,
    ),
}


def job_tasks():
    scheduler_cls, event_job_executed, event_job_error = get_scheduler_dependencies()
    scheduler = scheduler_cls(timezone="Asia/Shanghai")
    conf = config.copy()

    for platform_job in PLATFORM_JOBS.values():
        register_platform_jobs(scheduler, platform_job, conf)

    scheduler.add_listener(scheduler_listener, event_job_executed | event_job_error)
    scheduler.start()
    return scheduler


def tb_job_tasks(scheduler):
    register_platform_jobs(scheduler, PLATFORM_JOBS["taobao"], config.copy())


def jd_job_task(scheduler):
    register_platform_jobs(scheduler, PLATFORM_JOBS["jingdong"], config.copy())


def pdd_job_task(scheduler):
    register_platform_jobs(scheduler, PLATFORM_JOBS["pinduoduo"], config.copy())


def sn_job_task(scheduler):
    register_platform_jobs(scheduler, PLATFORM_JOBS["suning"], config.copy())


def register_platform_jobs(scheduler, platform_job: PlatformJob, all_conf: Dict):
    platform_conf = all_conf.get(platform_job.config_key) or {}
    if not platform_conf.get("is_open"):
        return

    missing_keys = [
        key for key in platform_job.required_keys
        if not platform_conf.get(key)
    ]
    if missing_keys:
        print(
            "{} scheduler skipped, missing config: {}".format(
                platform_job.config_key,
                ", ".join(missing_keys),
            )
        )
        return

    for chat_group in iter_chat_groups(platform_conf):
        print(chat_group["group_name"])
        scheduler.add_job(
            func=resolve_task(platform_job.task_path),
            kwargs=build_job_kwargs(platform_job, platform_conf, chat_group),
            trigger="cron",
            hour=str(chat_group["hour"]),
            minute=str(chat_group["minute"]),
            second=0,
            jitter=platform_job.jitter,
            id=build_job_id(platform_job.config_key, chat_group),
            replace_existing=True,
        )


def iter_chat_groups(platform_conf: Dict) -> Iterable[Dict]:
    for chat_group in platform_conf.get("chat_groups") or []:
        if all(chat_group.get(key) for key in ("group_name", "group_material_id", "hour", "minute")):
            yield chat_group


def build_job_kwargs(platform_job: PlatformJob, platform_conf: Dict, chat_group: Dict) -> Dict:
    kwargs = {}
    for task_key, config_key in platform_job.kwargs_map.items():
        kwargs[task_key] = chat_group.get(config_key, platform_conf.get(config_key))
    return kwargs


def build_job_id(platform_name: str, chat_group: Dict) -> str:
    return "{}:{}:{}:{}:{}".format(
        platform_name,
        chat_group["group_name"],
        chat_group["group_material_id"],
        chat_group["hour"],
        chat_group["minute"],
    )


def resolve_task(task_path: str):
    module_name, function_name = task_path.split(":", 1)
    module = import_module(module_name)
    return getattr(module, function_name)


def get_scheduler_dependencies():
    from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
    from apscheduler.schedulers.background import BackgroundScheduler

    return BackgroundScheduler, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR


def scheduler_listener(event):
    if event.exception:
        print(
            "Error: JOB_ID: {}, run_time: {}, job failed.".format(
                event.job_id,
                event.scheduled_run_time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
    else:
        print(
            "Success: JOB_ID: {}, run_time: {}, job completed.".format(
                event.job_id,
                event.scheduled_run_time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )


if __name__ == '__main__':
    config.init()
    job_tasks()
