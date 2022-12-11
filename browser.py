# -*- coding: utf-8 -*-
# pip3 install selenium
# author: Anton Khazov

import time
from selenium import webdriver


CHAT_ID_TARGET_GROUP = '333333333'

def main():
    browser = webdriver.Firefox(executable_path="./geckodriver")
    browser.get('https://web.telegram.org/k/#' + CHAT_ID_TARGET_GROUP)

    print('Executor_url = ' + browser.command_executor._url)
    print('Session_id = ' + browser.session_id)

    while True:
        time.sleep(1)

if __name__ == "__main__":
	main()
