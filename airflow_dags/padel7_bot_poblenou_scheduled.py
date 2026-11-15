from datetime import datetime

import pendulum
from airflow.timetables.trigger import CronTriggerTimetable
from airflow.decorators import dag
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

IMAGE_NAME = "padel7-booking-bot:0.0.1"
WAIT_UNTIL = ["00:00:00", "00:00:10", "00:00:20"]
MAX_COURTS_TO_BOOK = len(WAIT_UNTIL)


@dag(
    dag_id="padel7_booking_bot_poblenou_scheduled",
    start_date=datetime(2026, 8, 20, tzinfo=pendulum.timezone("Europe/Madrid")),
    schedule=CronTriggerTimetable("57 23 * * FRI", timezone="Europe/Madrid"),
    catchup=False,
    default_args={"retries": 3},
)
def padel7_booking_dag():
    for attempt in range(MAX_COURTS_TO_BOOK):
        DockerOperator(
            task_id=f"run_booking_bot_{attempt}",
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
            command=f"""
                --centre poblenou
                {{% if task_instance.try_number == 1 %}}--wait-until {WAIT_UNTIL[attempt]}{{% endif %}}
                --no-dry-run
                --notifications
            """,
        )


padel7_booking_dag()