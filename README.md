### Prerequisites
1. Install [python](https://www.python.org/downloads/)
2. Run `pip install -r requirements.txt`

### Usage
1. Open your hosts file and route hcaptcha-solver.com to localhost
2. Set HCAPTCHA_SITEKEY environment variable to your [hcaptcha](https://www.hcaptcha.com) sitekey
2. Set HCAPTCHA_SECRET environment variable to your [hcaptcha](https://www.hcaptcha.com) secret
2. Run `python server.py` in a separate terminal
3. Run `python collector.py`
4. Start solving captchas

### Contributing
1. Fork it
2. Create your branch (`git checkout -b my-change`)
3. Commit your changes (`git commit -m "changed something"`)
4. Push to the branch (`git push origin my-change`)
5. Create new pull request
