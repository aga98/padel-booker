from datetime import datetime, timedelta

import pendulum
from airflow.timetables.trigger import CronTriggerTimetable
from airflow.models.param import Param
from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator

IMAGE_NAME = "padel7-booking-bot:0.0.1"


@dag(
    dag_id="padel7_balance_check",
    start_date=datetime(2026, 8, 20, tzinfo=pendulum.timezone("Europe/Madrid")),
    schedule=CronTriggerTimetable("0 14 * * FRI", timezone="Europe/Madrid"),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    params={
        "dry_run": Param(
            True,
            type="boolean",
            description="When triggered manually, route the Telegram summary to TEST chat (True) or PROD chat (False).",
        ),
    },
)
def padel7_balance_check_dag():
    DockerOperator(
        task_id="check_account_balance",
        image=IMAGE_NAME,
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove="force",
        mount_tmp_dir=False,
        environment={
            "APP_USERNAME": "{{ var.value.PADEL7_USERNAME }}",
            "APP_PASSWORD": "{{ var.value.PADEL7_PASSWORD }}",
            "APP_TELEGRAM_BOT_TOKEN": "{{ var.value.APP_TELEGRAM_BOT_TOKEN }}",
            "APP_TELEGRAM_PROD_CHAT_ID": "{{ var.value.APP_TELEGRAM_PROD_CHAT_ID }}",
            "APP_TELEGRAM_TEST_CHAT_ID": "{{ var.value.APP_TELEGRAM_TEST_CHAT_ID }}",
        },
        command="""
            --check-balance
            --notifications
            {% if dag_run.run_type == 'scheduled' or not params.dry_run %}
                --no-dry-run
            {% else %}
                --dry-run
            {% endif %}
        """,
    )


padel7_balance_check_dag()