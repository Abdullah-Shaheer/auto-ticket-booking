import random
import time
import traceback
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import requests
from selenium.webdriver.chrome.service import Service
import json


def get_real_time_update(authorize):
    lst = {}
    print(f'Authorization Token:- {authorize}')
    while True:
        try:
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Authorization': authorize,
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Origin': 'https://tickets.feyenoord.nl',
                'Pragma': 'no-cache',
                'Referer': 'https://tickets.feyenoord.nl/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                'no-auth': 'true',
                'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
            response = requests.get('https://feyenoord.api.tymes4-infra.com/v2/Event', headers=headers)
            dat = response.json()
            her = dat.get('TabItems', '')[1].get('Items', '')
            for i in her:
                name = i.get('Name', '')
                lst['Name'] = name
                till = i.get('VisibleInShopTill', '')
                lst['Till'] = till
                if lst['Name'] == 'Willem II - Feyenoord' or 'willem' in lst['Name'].lower():
                    print('Event found on API. Booking now')
                    print(f'Event is available till {till}')
                    break
            else:
                print('Not Available at this time. Searching after 0.1 minutes')
                time.sleep(10)
                continue
        except:
            traceback.print_exc()


def get_auth_token(driver):
    logs = driver.get_log("performance")
    for log in logs:
        try:
            network_log = json.loads(log["message"])["message"]
            if network_log["method"] == "Network.requestWillBeSent":
                request = network_log["params"]["request"]
                url = request.get("url", "")
                headers = request.get("headers", {})

                # print(f"Captured URL: {url}")  # Debugging: Print all URLs
                # Match the exact API request
                if "feyenoord.api.tymes4-infra.com/v2/Event" in url:
                    authorization_header = headers.get('Authorization') or headers.get('authorization', '')

                    if authorization_header:
                        print('Authorization header has been found.')
                        return authorization_header
                    else:
                        print('Authorization header not found in the request.')

        except Exception as e:
            print(f'Error while processing logs: {e}')


def book_ticket(driver):
    stadium_map = WebDriverWait(driver, 20).until(
        ec.presence_of_element_located((By.XPATH, "//div[@id='stadium-map']")))

    if stadium_map:
        seats = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.XPATH, "//*[local-name()='g' and @class='section ']/*")))

        if seats:
            print('Seat found')
            seats[0].click()
        else:
            print('No seat found')
        try:
            icp = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//input[@type='number']")))
            icp.click()
            icp.clear()
            icp.send_keys('1')
            b = driver.find_element(By.XPATH, "//button[@class='btn btn-full btn-green btn--uppercase']")
            if b:
                driver.execute_script('arguments[0].click();', b)
            sub = WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
                (By.XPATH, "//button[@class='btn btn-full btn-green btn-highlight btn--uppercase']")))
            if sub:
                time.sleep(3)
                driver.execute_script('arguments[0].scrollIntoView(true);', sub)
                driver.execute_script('arguments[0].click();', sub)
                print('Order is now in que for 20 minutes. Confirm your payment method.')
        except:
            m = WebDriverWait(driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, "//*[local-name()='g' and @cursor='pointer']"))
            )
            if m:
                driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));",
                                      m[0])
                driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));", m[0])
                driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', { bubbles: true }));", m[0])
            sub = WebDriverWait(driver, 20).until(ec.element_to_be_clickable(
                (By.XPATH, "//button[@class='btn btn-full btn-green btn-highlight btn--uppercase']")))
            if sub:
                time.sleep(3)
                driver.execute_script('arguments[0].scrollIntoView(true);', sub)
                driver.execute_script('arguments[0].click();', sub)
    else:
        print('Stadium map not found')


def automate():
    result = {}
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.debugger_address = 'localhost:9222'
    s = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=options)
    url = 'https://tickets.feyenoord.nl/account/sso-login'
    driver.get(url)
    emai = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.NAME, "Email")))
    em = 'Vannieuwenhuijzenjaap@gmail.com'
    for char in em:
        emai.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))
    ps = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.NAME, "Password")))
    p = 'Ys454124'
    for char in p:
        ps.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))
    sub = driver.find_element(By.XPATH, "//input[@id='submitForm']")
    if sub:
        driver.execute_script('arguments[0].scrollIntoView(true);', sub)
        driver.execute_script('arguments[0].click();', sub)
    time.sleep(3)
    try:
        ee = driver.find_element(By.NAME, "Email")
        p = driver.find_element(By.NAME, 'Password')
        if ee:
            print('Login failed. Trying again')
            ee.clear()
            ee.send_keys('Vannieuwenhuijzenjaap@gmail.com')
            time.sleep(1)
            p.send_keys('Ys454124')
            time.sleep(2)
            driver.execute_script('arguments[0].scrollIntoView(true);', sub)
            driver.execute_script('arguments[0].click();', sub)
            time.sleep(4)
            e = driver.find_element(By.NAME, "Email")
            if e:
                print('Login failed. Quitting some error encountered.')
                driver.quit()
    except:
        print('Login Success')
    for _ in range(1):
        time.sleep(4)
        sing = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, "//a[@class='nav-link nav-link-saleschannel-button']")))
        driver.execute_script('arguments[0].click();', sing)
        time.sleep(10)
        authorization = get_auth_token(driver)
        print(authorization)
        get_real_time_update(authorization)
    driver.refresh()
    xpath = "//div[@class='tab__container']"
    tabs = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.XPATH, xpath)))
    ss = tabs.find_elements(By.TAG_NAME, 'h6')
    if ss and len(ss) > 2:
        uit = ss[1]
        if uit:
            driver.execute_script('arguments[0].scrollIntoView(true);', uit)
            driver.execute_script('arguments[0].click();', uit)
    lis = driver.find_elements(By.CLASS_NAME, "home")
    for l in lis:
        print(l.text)
        if 'WILLEM' in l.text:
            result['get'] = 'Able to detect it.'
            break
        else:
            result['get'] = 'Not able till now'
    if result['get'] == 'Able to detect it.':
        print('Event has been found successfully. Now going to book')
        but = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//button[@class='btn btn-full btn--uppercase']")))
        time.sleep(5)
        if but:
            if but.text.strip() == 'TICKETS KOPEN':
                driver.execute_script('arguments[0].scrollIntoView(true);', but)
                driver.execute_script('arguments[0].click();', but)
                book_ticket(driver)
                # try:
                #     resp = requests.get(f"https://api.telegram.org/bot7522702707:AAG-ArCh982M1lio2DZOmrMY5vKoHULT5hM/sendMessage?chat_id=-4702099598&text= WILLEM II - Feyenoord is Booked Now Please Confirm Your Payment. Ticket Is In your Cart For 20 MInutes")
                #     print(resp.json())
                # except:
                #     print('An error while sending the message.')
            else:
                print('The ticket has been sold out.')

    else:
        print('Event cannot be detected by driver')


automate()

