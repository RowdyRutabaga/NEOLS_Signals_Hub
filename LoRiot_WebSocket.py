import websocket
import json
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time

# # Github credentials
# username = "username"
# password = "password!"

# # initialize the Chrome driver
# driver = webdriver.Edge()
# delay = 15 # seconds
# # head to github login page
# driver.get('https://us1.loriot.io/login')
# try:
#     myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "/html/body/div/app-root/app-login-main/section/form/div[1]/input")))
#     print("Page is ready!")
# except TimeoutException:
#     print("Loading took too much time!")


# # find username/email field and send the username itself to the input field
# driver.find_element(By.XPATH, "/html/body/div/app-root/app-login-main/section/form/div[1]/input").send_keys(username)
# # find password input field and insert password as well
# driver.find_element(By.XPATH, "/html/body/div/app-root/app-login-main/section/form/div[2]/input").send_keys(password)
# # click login button
# driver.find_element(By.XPATH, "/html/body/div/app-root/app-login-main/section/form/button[1]").click()
# time.sleep(5)
# driver.get("https://us1.loriot.io/applications/BE7E0868/devices")
# table =  driver.find_element(By.XPATH, "/html/body/div/app-root/lyt-main/div/ng-component/nsw-devices/lrw-frame/div/div[1]/section[2]/div/div/div/div/div[3]/div/div/nsw-devices-table/table")

# for row in table.find_element(By.XPATH, ".//tr"):
#     print([td.text for td in row.find_element(By.XPATH,".//td[@class='dddefault'][1]")])

def on_message(ws, message):
    json_message = json.loads(message)
    if json_message['cmd'] =="gw":
        eui = json_message['EUI']
        timestamp = json_message['gws'][0]['time']
        decoded_data = bytearray.fromhex(json_message['data']).decode()

        print(f"EUI: {eui}")
        print(f"Timestamp: {timestamp}")
        print(f"Data: {decoded_data}")

def on_error(ws, error):
    print(f"Encountered error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    ws.send("Hello, Server!")

if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://us1.loriot.io/app?token=vn4IaAAAAA11czEubG9yaW90LmlvGWk_UPLNmrmvDpQMBDyVGw==",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()