# -*- coding: utf-8 -*-
# pip3 install selenium
# author: Anton Khazov

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import requests
from os import listdir
from os.path import isfile, join
import pickle


SESSION_PORT = '55555'
SESSION_TOKEN = '123456789-1234-1234-1234-123456789012'

TOKEN = '1111111111:AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
CHAT_ID_START        = '1111111111'
CHAT_ID_BOT          = '1111111111'
CHAT_ID_SELF         = '222222222'
CHAT_ID_TARGET_GROUP = '333333333'
NAME_TARGET_GROUP    = 'Saved Messages'

LastMessage = ''
MemeIndex = 0

def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == 'newSession':
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)

    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver
    
def send_photo_with_bot(chat_id, image_path, image_caption=''):
    data = {'chat_id': chat_id, 'caption': image_caption}
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto'

    with open(image_path, "rb") as image_file:
        #send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + 'aaa'
        #response = requests.get(send_text)
        response = requests.get(url, data=data, files={'photo': image_file})
        
    return response.json()

def scroll_page_down(browser):
    try:
        scrollable_xpath = ('//div[@class="bubbles has-groups has-sticky-dates"]'
                            '/div[@class="scrollable scrollable-y"]')
        element = browser.find_element_by_xpath(scrollable_xpath)
        if element:
            browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', element)
    except:
        pass

def switch_to_target_group(browser):
    scroll_page_down(browser)
    
    chatlist_chat_xpath = '//a[@href="#' + CHAT_ID_TARGET_GROUP + '"]'
    chatlist_chat = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, chatlist_chat_xpath)))
    chatlist_chat.click()
    chat_info_xpath = ('//div[@class="sidebar-header topbar"]/div[@class="chat-info-container"]/div[@class="chat-info"]'
                        '/div[@class="person"]/div[@class="content"]/div[@class="top"]/div[@class="user-title"]'
                        '/span[@class="peer-title" and @data-peer-id="' + CHAT_ID_TARGET_GROUP + '"]')
    element = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, chat_info_xpath)))

def wait_new_message(browser=None, reset=True):
    global LastMessage
    silence = True

    while (silence):
        scroll_page_down(browser)

        messages_xpath = ('//div[@class="bubbles-group"]/div[contains(@class, "is-group-last")]/div[@class="bubble-content-wrapper"]'
                            '/div[@class="bubble-content"]/div[@class="message spoilers-container"]')
        elements = browser.find_elements_by_xpath(messages_xpath)
        
        #print('<<<<< ' + str(len(elements)) + ' elements found in group >>>>>')
        #for element in elements:
            #print(element.get_attribute('outerHTML'))
            #print(element.text)

        if len(elements):
            message = elements[-1].text

            if reset:
                silence = False
            elif LastMessage != message:
                print('message: [' + message + ']\n')
                silence = False

            LastMessage = message


def switch_to_bot(browser):
    scroll_page_down(browser)
    
    chatlist_chat_xpath = '//a[@href="#' + CHAT_ID_BOT + '"]'
    chatlist_chat = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, chatlist_chat_xpath)))
    chatlist_chat.click()
    chat_info_xpath = ('//div[@class="sidebar-header topbar"]/div[@class="chat-info-container"]/div[@class="chat-info"]'
                        '/div[@class="person"]/div[@class="content"]/div[@class="top"]/div[@class="user-title"]'
                        '/span[@class="peer-title" and @data-peer-id="' + CHAT_ID_BOT + '"]')
    element = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, chat_info_xpath)))

def forward_photo_from_bot_to_target_group(browser):
    scroll_page_down(browser)
    
    messages_xpath = ('//div[@class="bubbles-group"]/div[contains(@class, "is-group-last")]/div[@class="bubble-content-wrapper"]'
                        '/div[@class="bubble-content"]/div[@class="message spoilers-container"]')
    elements = browser.find_elements_by_xpath(messages_xpath)
    
    #print('>>>>> ' + str(len(elements)) + ' elements found in bot <<<<<')
    #for element in elements:
        #print(element.get_attribute('outerHTML'))
        #print(element.text)


    if len(elements):
        # Right click on last message
        actionChains = ActionChains(browser)
        actionChains.move_to_element(elements[-1]).perform()
        actionChains.context_click(elements[-1]).perform()

        forward_button_xpath = '//div[@id="bubble-contextmenu"]/div[@class="btn-menu-item rp-overflow tgico-forward"]'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, forward_button_xpath))).click()
        chat_search_input_xpath = '//input[@class="selector-search-input i18n"]'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, chat_search_input_xpath))).send_keys(NAME_TARGET_GROUP)
        target_group_select_xpath = ('//a[@class="row no-wrap row-with-padding row-clickable hover-effect chatlist-chat chatlist-chat-abitbigger" '
                                        'and @data-peer-id="' + CHAT_ID_TARGET_GROUP + '"]')
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, target_group_select_xpath))).click()
        send_button_xpath = '//button[@class="btn-icon tgico-none btn-circle btn-send animated-button-icon rp send"]'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, send_button_xpath))).click()

def meme_select():
    global MemeIndex

    mypath = './memes'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    meme_to_send_name = onlyfiles[MemeIndex]

    print('MemeIndex: ' + str(MemeIndex) + ', meme name: ' + meme_to_send_name)

    if MemeIndex == len(onlyfiles) - 1:
        MemeIndex = 0
    else:
        MemeIndex += 1

    return meme_to_send_name

def meme_index_load():
    global MemeIndex
    with open('meme_index.txt', 'r', encoding='utf-8') as f:
        MemeIndex = int(f.read())

def meme_index_save():
    global MemeIndex
    with open('meme_index.txt', 'w') as f:
        f.write(str(MemeIndex))


def main():
    meme_index_load()
    print('MemeIndex: ' + str(MemeIndex))

    browser = attach_to_session('http://127.0.0.1:' + SESSION_PORT, SESSION_TOKEN)
    browser.get('https://web.telegram.org/k/#' + CHAT_ID_START)

    while True:
        switch_to_target_group(browser)
        wait_new_message(browser=browser, reset=True)
        wait_new_message(browser=browser, reset=False)
        send_photo_with_bot(CHAT_ID_SELF, './memes/' + meme_select())
        meme_index_save()
        switch_to_bot(browser)
        forward_photo_from_bot_to_target_group(browser)
    

if __name__ == "__main__":
	main()
