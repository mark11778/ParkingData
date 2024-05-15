import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument('--headless')

service = Service(executable_path='/usr/bin/chromedriver')
driver = webdriver.Chrome(options=options, service=service)

df = pd.DataFrame({
    'Date Issue': [],
    'Location': [],
    'Comment': [],
    'License Plate': [],
    'Type': []
})

try:
    base_ticket_number = 1300001
    while True:
        ticket_number = f"24P{base_ticket_number}"
        start_url = "https://parkingtickets.cityofmadison.com/tickets/"
        driver.get(start_url)

        input_element = driver.find_element(By.ID, "ticket_plate_vin")
        input_element.clear()
        input_element.send_keys(ticket_number)

        search_button = driver.find_element(By.ID, "search_ticket")
        search_button.click()

        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#ticket_detail div.col-md-6")))

            ticket_info_div = driver.find_element(By.CSS_SELECTOR, "div#ticket_detail div.col-md-6")
            paragraphs = ticket_info_div.find_elements(By.TAG_NAME, "p")
            data = {}
            for p in paragraphs:
                try:
                    strong_tag = p.find_element(By.TAG_NAME, "strong").text
                    strong_following_text = p.text.replace(strong_tag, '').strip()

                    if 'Issue Date and Time:' in strong_tag:
                        data['Date Issue'] = strong_following_text
                    elif 'Location:' in strong_tag:
                        data['Location'] = strong_following_text
                    elif 'Comment:' in strong_tag:
                        data['Comment'] = strong_following_text
                except Exception as e:
                    print(f"Error retrieving part of the data for {ticket_number}: {e}")

            try:
                data['License Plate'] = driver.find_element(By.CSS_SELECTOR, "div.plate_number").text
            except Exception as e:
                data['License Plate'] = "Not Found"
                print(f"License Plate not found for {ticket_number}: {e}")

            try:
                data['Type'] = driver.find_element(By.XPATH, ".//th[contains(text(), '2 HR LIMIT DURING POSTED TIMES')]").text
            except Exception as e:
                data['Type'] = "Not Found"
                print(f"Violation Type not found for {ticket_number}: {e}")

            new_row = pd.DataFrame([data], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)

        except Exception as e:
            print(f"No more tickets found for {ticket_number}, error: {e}")
            break

        base_ticket_number += 1

finally:
    driver.quit()
    print(df)

