import gzip
import json
import re
import shutil
import time
from os import path, mkdir, listdir

import numpy as np
import requests
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from tqdm import tqdm

GOAL = 10000


class Filesystem:
    def __init__(self):
        self.output_dir = "data"

        if not path.exists(self.output_dir):
            mkdir(self.output_dir)

    def get_remaining(self):
        file_count = len(listdir(self.output_dir))
        return GOAL - file_count

    def write(self, images, answers, prompt):
        output_dir = path.join(self.output_dir, str(round(time.time() * 1000)))
        mkdir(output_dir)

        answers_path = path.join(output_dir, "answer.json")

        with open(answers_path, "w") as f:
            data = {"prompt": prompt, "answers": answers}
            f.write(json.dumps(data))

        images_dir = path.join(output_dir, "images")
        mkdir(images_dir)

        for j, image in enumerate(images):
            save_path = path.join(images_dir, f"{j}.jpg")

            image_response = requests.get(image, stream=True)

            with open(save_path, "wb") as f:
                image_response.raw.decode_content = True
                shutil.copyfileobj(image_response.raw, f)


def sectors(num, chunk_size):
    if num % chunk_size == 0:
        width = num // chunk_size
        return [width + i * width for i in range(chunk_size)]
    else:
        x = np.linspace(1, num, chunk_size + 1)
        return [x[i + 1] for i in range(chunk_size)]


def switch_to_iframe(driver, iframe):
    driver.switch_to.default_content()
    driver.switch_to.frame(iframe)


def main():
    filesystem = Filesystem()

    options = FirefoxOptions()

    driver = webdriver.Firefox(options=options)

    driver.get("http://hcaptcha-collector.com:5000")

    amount = filesystem.get_remaining()

    for i in tqdm(range(amount)):
        driver.refresh()

        del driver.requests

        driver.switch_to.default_content()

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        switch_to_iframe(driver, iframes[0])

        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "checkbox")))

        driver.find_element(By.ID, "checkbox").click()

        driver.switch_to.default_content()

        WebDriverWait(driver, 30).until(lambda browser: len(browser.find_elements(By.TAG_NAME, "iframe")) > 1)

        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        switch_to_iframe(driver, iframes[1])

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "prompt-text")))

        prompt_text = driver.find_element(By.CLASS_NAME, "prompt-text")
        prompt = prompt_text.text

        answers = []
        images = []

        image_url_pattern = re.compile(r'url\("(.*)"\)')

        def check_for_images():
            image_elements = driver.find_elements(By.CSS_SELECTOR, "[class='task-image'] [class='image']")

            for image_element in image_elements:
                try:
                    background = image_element.value_of_css_property("background")

                    if not image_url_pattern.match(background):
                        continue

                    image_url = image_url_pattern.search(background).group(1)

                    if image_url not in images:
                        images.append(image_url)
                except StaleElementReferenceException:
                    break

        passed = False

        while not passed:
            check_for_images()

            check_captcha_request = None

            for request in driver.requests:
                if "checkcaptcha" in request.url and request.method == "POST" and request.response:
                    check_captcha_request = request

            if check_captcha_request:
                passed = json.loads(gzip.decompress(check_captcha_request.response.body))["pass"]

                if not passed:
                    break
                else:
                    answers.extend(json.loads(check_captcha_request.body)["answers"].values())

            switch_to_iframe(driver, iframes[0])
            captcha_open = driver.find_element(By.ID, "anchor").get_attribute("aria-hidden")
            switch_to_iframe(driver, iframes[1])

            if images and not passed and captcha_open == "false":
                images.clear()
                break

        if not passed:
            continue

        filesystem.write(images, answers, prompt)

        if i != 0 and i % 10 == 0:
            driver.delete_all_cookies()


if __name__ == "__main__":
    main()
