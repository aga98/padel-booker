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


def _build_balance_message(
        balance: float,
        indoor_cost: float = 48.0,
        outdoor_cost: float = 45.0,
) -> str:
    indoor_courts = int(balance // indoor_cost)
    outdoor_courts = int(balance // outdoor_cost)
    remainder = balance % indoor_cost

    if indoor_courts >= 2:
        status_line = "✅ <b>Ready for 2 indoor courts!</b>"
    elif indoor_courts == 1:
        needed_for_two = (2 * indoor_cost) - balance
        status_line = (
            f"⚠️ <b>Enough for 1 indoor court.</b> "
            f"Need <b>€{needed_for_two:.2f}</b> more to reach 2 courts."
        )
    else:
        needed_for_one = indoor_cost - balance
        status_line = (
            f"🚨 <b>Not enough credit for 1 indoor court!</b> "
            f"Need <b>€{needed_for_one:.2f}</b> more."
        )

    return (
        "💳 <b>PADEL7 WALLET STATUS</b> 💳\n\n"
        "━━━━━━━━━━━━━━━\n"
        f"💰 <b>Current Credit:</b> €{balance:.2f}\n"
        f"🏟️ <b>Indoor Courts (€{indoor_cost:.0f}):</b> {indoor_courts} "
        f"<i>(€{remainder:.2f} left over)</i>\n"
        f"☀️ <b>Outdoor Courts (€{outdoor_cost:.0f}):</b> {outdoor_courts}\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"{status_line}"
    )


def send_balance_notification(
        bot_token: str,
        chat_id: str,
        balance: float,
        indoor_cost: float = 48.0,
        outdoor_cost: float = 45.0,
) -> None:
    bot_token = bot_token.strip().strip("\"'")
    chat_id = str(chat_id).strip().strip("\"'")
    if not bot_token or not chat_id:
        raise ValueError("Missing APP_TELEGRAM_BOT_TOKEN or chat ID in environment settings.")

    payload = {
        "chat_id": chat_id,
        "text": _build_balance_message(balance, indoor_cost, outdoor_cost),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    logging.debug("Telegram balance payload: %s", payload)

    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json=payload,
        timeout=15,
    )

    if response.status_code != 200 or not response.json().get("ok"):
        raise ValueError(
            f"Request to Telegram returned an error {response.status_code}, the response is:\n{response.text}"
        )
    logging.info("Balance notification sent successfully.")

