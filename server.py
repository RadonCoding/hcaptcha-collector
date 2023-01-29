import os

from dotenv import load_dotenv
from flask import *
from flask_hcaptcha import hCaptcha

load_dotenv()

server = Flask(__name__)
captcha = hCaptcha(server,
                   os.environ["HCAPTCHA_SITE_KEY"],
                   os.environ["HCAPTCHA_SECRET_KEY"],
                   True)


@server.route("/", methods=["GET"])
def index():
    return render_template("index.html", hcaptcha=captcha.get_code())


def main():
    server.run("hcaptcha-collector.com", 5000)


if __name__ == "__main__":
    main()
