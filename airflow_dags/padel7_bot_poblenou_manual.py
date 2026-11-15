from datetime import datetime

import pendulum
from airflow.decorators import dag
from airflow.models.param import Param
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

IMAGE_NAME = "padel7-booking-bot:0.0.1"


@dag(
    dag_id="padel7_booking_bot_poblenou_manual",
    start_date=datetime(2026, 8, 20, tzinfo=pendulum.timezone("Europe/Madrid")),
    schedule=None,
    catchup=False,
    default_args={"retries": 3},
    params={
        "notifications": Param(
            True,
            type="boolean",
            description="Send Telegram notification (uses TEST chat when dry_run is True, PROD chat when False).",
        ),
        "skip_wait": Param(
            False,
            type="boolean",
            description="Toggle ON to execute immediately without waiting for wait_until param.",
        ),
        "wait_until": Param("00:00:00", type="string", description="Time to wait until"),
        "centre": Param("poblenou", type="string", description="Padel center name"),
        "dry_run": Param(True, type="boolean", description="Run without booking"),
    },
)
def padel7_booking_dag():
    DockerOperator(
        task_id="run_booking_bot",
        image=IMAGE_NAME,
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove="force",
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source="/home/alberto/Documents/repos/padel-booker/padel7_booking_bot/screenshots",
                target="/app/screenshots",
                type="bind",
            ),
            Mount(
                source="/home/alberto/Documents/repos/padel-booker/padel7_booking_bot/logs",
                target="/app/logs",
                type="bind",
            ),
        ],
        environment={
            "APP_USERNAME": "{{ var.value.PADEL7_USERNAME }}",
            "APP_PASSWORD": "{{ var.value.PADEL7_PASSWORD }}",
            "APP_TELEGRAM_BOT_TOKEN": "{{ var.value.APP_TELEGRAM_BOT_TOKEN }}",
            "APP_TELEGRAM_PROD_CHAT_ID": "{{ var.value.APP_TELEGRAM_PROD_CHAT_ID }}",
            "APP_TELEGRAM_TEST_CHAT_ID": "{{ var.value.APP_TELEGRAM_TEST_CHAT_ID }}",
        },
        command="""
            --centre {{ params.centre }}
            {% if not params.skip_wait %}
                --wait-until {{ params.wait_until }}
            {% endif %}
            {% if params.dry_run %}--dry-run{% else %}--no-dry-run{% endif %}
            {% if params.notifications %}--notifications{% endif %}
        """,
    )


padel7_booking_dag()