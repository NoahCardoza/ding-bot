import re
import ssl
import uuid
import time
import random
import logging
import requests
from itertools import cycle


logging.basicConfig(
    format='%(asctime)s :%(name)s: [%(levelname)s] %(message)s')
log = logging.getLogger('DingBot')
log.setLevel(level=logging.INFO)

print(ssl.OPENSSL_VERSION)


RE_NUMBER = re.compile(r'\d+')
REQ_TIMEOUT = 10


def load_numbers(file):
    with open(file, 'r') as f:
        return [RE_NUMBER.search(line).group(0) for line in f if line.strip()]


def load_proxies(file):
    proxies = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                ip, port, user, password = line.split(':')
                host = f'{user}:{password}@{ip}:{port}'
                proxies.append({
                    'http': 'http://' + host,
                    'https': 'https://' + host,
                })
    return proxies


class DingBot:
    def __init__(self, number, proxies):
        self.number = number

        self.s = requests.Session()
        self.s.proxies.update(proxies)
        self.s.headers.update({
            'content-type': 'text/plain;charset=UTF-8',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'content-language': 'en',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        })

    def register(self):
        self.s.get('https://www.ding.com/register', timeout=REQ_TIMEOUT)

        payload = {
            "countryDial": "0",
            "number": self.number,
            "uniqueId": str(uuid.uuid4()),
        }

        r = self.s.post(
            'https://api.www.ding.com/api/phonenumbersubmit', headers={
                'origin': 'https://www.ding.com',
                'referer': 'https://www.ding.com/register',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
            }, json=payload, timeout=REQ_TIMEOUT)

        if not r.ok:
            log.error("POST %s : %s", r.status_code, r.text)
        else:
            log.debug("POST %s : %s", r.status_code, r.text)

    def start(self):
        try:
            self.register()
        except Exception as e:
            log.exception(e)


numbers = load_numbers('numbers.txt')
proxies = load_proxies('proxies.txt')

random.shuffle(numbers)
random.shuffle(proxies)

pairs = zip(numbers, cycle(proxies)) if len(numbers) > len(
    proxies) else zip(cycle(numbers), proxies)

for number, proxy in cycle(pairs):
    log.info('number +%s', number)
    DingBot(number, proxy).start()
    timeout = random.randint(0, 5)
    log.info('waiting %ss', timeout)
    time.sleep(timeout)


# from threading import Thread
# tasks = []

# # Wait for all the tasks to finish
# for t in tasks:
#     t.join()

# # Start tasks
# for number, proxy in pairs:
#     log.info('number +%s', number)

#     instance = DingBot(number, proxy)
#     t = Thread(target=instance.start)
#     t.start()
#     tasks.append(t)

# # Wait for all the tasks to finish
# for t in tasks:
#     t.join()
