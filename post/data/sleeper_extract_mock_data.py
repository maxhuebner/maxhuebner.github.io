from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import pandas as pd
import time
from datetime import date

USERNAME = ""  # Sleeper.app Username
PASSWORD = ""  # Sleeper.app Password

chrome_options = Options()
# If you uncomment these line the browser will run headless meaning
# it wont open a browser window for you to look at
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")

# My chromedriver.exe is in the project path. Update accordingly
driver = webdriver.Chrome(executable_path='./driver/chromedriver.exe', options=chrome_options)
driver.get("https://sleeper.app/login")  # Get to the Login Page

# Find Username field using XPath - Fill in Username
driver.find_element_by_xpath("//input").send_keys(USERNAME)

# Find Login Button - Clock
loginButton = driver.find_element_by_xpath(
    '//*[contains(concat( " ", @class, " " ), concat( " ", "login-button", " " ))]')
loginButton.click()

time.sleep(2)

# After First Click Password Field Will Show Up - Enter Password and click again
driver.find_elements_by_xpath('//input')[1].send_keys(PASSWORD)
loginButton.click()

# LOGGED IN NOW - Waiting just to make sure
time.sleep(10)

# Click Mock Draft Page - Click on first Mock Draft Found
# HINT: You NEED to create this mock draft by hand before
driver.find_element_by_xpath(
    '//*[contains(concat( " ", @class, " " ), concat( " ", "nav-draftboard-item", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "title", " " ))]').click()
time.sleep(5)
driver.find_element_by_class_name("draft-list-item").click()
time.sleep(2)

# Switch To New Mock Draft Tab
# Although it looks like it, the active window is not yet the mock draft
driver.switch_to.window(driver.window_handles[1])

# Init Data Loading Web Driver
wait = WebDriverWait(driver, 15)

scraped_elements = set()  # Contains ID's of already scraped names
execute_loop = True
rows_list = []  # Contains Dicts - Row of our DataFrame
rank = 1  # Counter for Rank
while execute_loop:
    # Get Visible Entries
    names = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.name-wrapper')))
    for name in names:
        if name.id in scraped_elements:  # Already Scraped
            continue

        # New Player
        scraped_elements.add(name.id)
        data_extract = name.text.split('\n')

        if len(data_extract) < 3:  # Not Fully Loaded -> Remove Again
            scraped_elements.remove(name.id)
            break

        rows_list.append({
            "rank": rank,
            "name": data_extract[0],
            "pos": data_extract[1],
            "team": data_extract[2]
        })

        print(f"{rank} - {data_extract[0]}")

        rank += 1

        if len(rows_list) >= 300:  # Only Scrape First 300 Players
            print("ABORTING..")
            execute_loop = False

    # Scroll Down
    # .odd is every other row
    # (You could probably scroll down more/faster)
    ActionChains(driver).move_to_element(driver.find_elements_by_css_selector(".odd")[5]).perform()

# Write CSV
df = pd.DataFrame(data=rows_list)
print(df)
df.to_csv(f"data/sleeper-mock-ranks-{date.today()}.csv", index=False)
driver.quit()  # Quit
