import html
import logging
import requests

from bot.types import BookingDetails


def _booking_info_text(booking_details: BookingDetails) -> str:
    date = html.escape(str(booking_details["date"]))
    time = html.escape(str(booking_details["time"]))
    court = html.escape(str(booking_details["court"]))
    location = html.escape(str(booking_details["location"]))

    return (
        "━━━━━━━━━━━━━━━\n"
        f"📅 <b>Date:</b> {date}\n"
        f"⏰ <b>Time:</b> {time}\n"
        f"🏟️ <b>Court:</b> {court}\n"
        f"📍 <b>Location:</b> {location}\n"
    )


def _build_success_message(booking_details: BookingDetails) -> str:
    cost = html.escape(str(booking_details["cost"]))
    booked_by = html.escape(str(booking_details["booked_by"]))

    return (
        "🎾 <b>COURT BOOKED! TIME TO SLAY!</b> 🎉\n\n"
        f"{_booking_info_text(booking_details)}"
        f"💸 <b>Cost:</b> {cost}\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💪 <b>LET'S MAKE IT EPIC!</b> 🎯"
    )


def _build_failure_message(booking_details: BookingDetails) -> str:
    return (
        "🚨 <b>There was a problem booking a court!</b> 🚨\n\n"
        f"{_booking_info_text(booking_details)}"
        "━━━━━━━━━━━━━━━\n\n"
        "<i>Please check the booking system or screenshots for more details.</i>"
    )


def send_booking_notification(
        bot_token: str,
        chat_id: str,
        booking_details: BookingDetails,
        booking_successful: bool = True,
) -> None:
    text = (
        _build_success_message(booking_details)
        if booking_successful
        else _build_failure_message(booking_details)
    )
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    logging.debug("Telegram notification payload: %s", payload)

    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json=payload,
        timeout=15,
    )

    if response.status_code != 200 or not response.json().get("ok"):
        raise ValueError(
            f"Request to Telegram returned an error {response.status_code}, the response is:\n{response.text}"
        )
    logging.info("Telegram notification sent successfully.")
