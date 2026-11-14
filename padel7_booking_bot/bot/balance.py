import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import bot.utils as utils
import config.settings as settings


def _parse_euro_amount(raw_text: str) -> float:
    match = re.search(r"-?\d[\d.,]*", raw_text)
    if not match:
        raise ValueError(f"Could not parse Euro amount from text: '{raw_text}'")
    # Convert Spanish/European format (e.g. "1.234,50" or "34,25") to float
    normalized = match.group(0).replace(".", "").replace(",", ".")
    return float(normalized)


def get_account_balance(driver: webdriver.Chrome) -> float:
    try:
        balance_el = WebDriverWait(driver, 10).until(
            lambda d: (
                el
                if (el := d.find_element(By.ID, settings.BALANCE_AMOUNT_LABEL_ID)).text.strip()
                else False
            )
        )
        raw_text = balance_el.text.strip()
        balance = _parse_euro_amount(raw_text)
        logging.info("Current account balance: €%.2f (raw: '%s')", balance, raw_text)
        return balance
    except Exception:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        utils.save_screenshot(driver, f"error_balance_{timestamp}.png")
        logging.exception("Failed to read account balance from dashboard")
        raise
