import requests
import time
from utils.logs import logger
from utils.session import create_session

class Faucet:
    def __init__(self, token, address, proxy=None):
        self.token = token
        self.address = address
        self.taskId = ""
        self.captcha = ""

        self.acc_name = f"{self.address[:5]}..{self.address[-5:]}"
        self.session = create_session(proxy)

    def create_task(self):
        # Отправка задания на решение капчи Turnstile в 2Captcha
        resp = requests.post("http://2captcha.com/in.php", data={
            "key": self.token,
            "method": "turnstile",  # Используем метод turnstile для Cloudflare Turnstile
            "sitekey": "0x4AAAAAAARdAuciFArKhVwt",  # Убедитесь, что это правильный sitekey
            "pageurl": "https://bartio.faucet.berachain.com/"
        })

        if "OK|" in resp.text:
            self.taskId = resp.text.split('|')[1]
            logger.info(f"{self.acc_name} отправили капчу на решение {self.taskId}..")
        else:
            logger.error(f"{self.acc_name} ошибка при создании задачи: {resp.text}")
            raise Exception("Ошибка создания задачи 2Captcha")

    def task_status(self):
        for i in range(15):
            try:
                time.sleep(5)

                # Проверка статуса решения капчи
                resp = requests.get(f"http://2captcha.com/res.php?key={self.token}&action=get&id={self.taskId}")
                if "OK|" in resp.text:
                    self.captcha = resp.text.split('|')[1]
                    logger.info(f"{self.acc_name} капча решена")
                    return True
                elif resp.text != "CAPCHA_NOT_READY":
                    logger.error(f"{self.acc_name} ошибка при решении капчи: {resp.text}")
                    break
            except Exception as e:
                logger.error(f"{self.acc_name} {self.taskId} {e}")

        return False

    def get_token(self):
        self.session.headers["Authorization"] = f"Bearer {self.captcha}"
        resp = self.session.post(f"https://bartiofaucet.berachain.com/api/claim?address={self.address}", json={"address": self.address})

        status_code = resp.status_code
        if status_code == 200:
            logger.success(f"{self.acc_name} получили токены BERA")
            return True

        elif status_code == 429:
            logger.info(f"{self.acc_name} получение токенов на перезарядке")
        elif status_code == 402:
            logger.info(f"{self.acc_name} на балансе менее 0.001 ETH")

        return False

    def faucet(self):
        try:
            while True:
                self.create_task()
                if self.task_status():
                    break

            return self.get_token()
        except Exception as e:
            logger.error(f"{self.acc_name} ошибка при получении токенов: {e}")