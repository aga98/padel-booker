import logging
import config.settings as settings
import bot.utils as utils
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login_to_site(username: str, password: str, env: str) -> webdriver.Chrome:
    driver = utils.create_chrome_driver(env)

    try:
        driver.get(settings.LOGIN_URL)
        logging.debug("Going to login page: %s", settings.LOGIN_URL)

        wait = WebDriverWait(driver, 15)

        # 1. Dismiss Cookie Banner quickly (3s max so a missing banner never stalls midnight bookings)
        try:
            refuse_cookies_button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, settings.LOGIN_REFUSE_COOKIES_BUTTON_ID))
            )
            driver.execute_script("arguments[0].click();", refuse_cookies_button)
        except TimeoutException:
            logging.debug("Cookie banner did not appear within 3s; continuing.")


        # 2. Wait briefly for the overlay to vanish; remove via JS if left orphaned
        try:
            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "banner-block-screen"))
            )
        except TimeoutException:
            logging.debug("Overlay banner-block-screen remained in DOM; removing via JS.")
            driver.execute_script(
                "document.querySelectorAll('.banner-block-screen').forEach(el => el.remove());"
            )

        # 3. Fill Username
        username_field = wait.until(
            EC.element_to_be_clickable((By.ID, settings.LOGIN_USERNAME_FIELD_ID))
        )
        username_field.clear()
        username_field.send_keys(username)

        # 4. Fill Password
        password_field = wait.until(
            EC.element_to_be_clickable((By.ID, settings.LOGIN_PASSWORD_FIELD_ID))
        )
        password_field.clear()
        password_field.send_keys(password)

        # Re-populate username if an async page script cleared it
        if username_field.get_attribute("value") != username:
            username_field.clear()
            username_field.send_keys(username)

        # 5. Wait until the submit button is interactive, then click via JS
        submit_button = wait.until(
            EC.element_to_be_clickable((By.ID, settings.LOGIN_BUTTON_ID))
        )
        driver.execute_script("arguments[0].click();", submit_button)

        # 6. Wait for navigation after login submission
        wait.until(EC.url_changes(settings.LOGIN_URL))
        logging.debug("Landed in the user profile page: %s", driver.current_url)

        return driver

    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        utils.save_screenshot(driver, f"error_login_final_state_{timestamp}.png")
        logging.error("Error during login on URL %s: %s", driver.current_url, e)
        driver.quit()
        raise
