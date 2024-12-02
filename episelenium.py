import os
import time
import pandas as pd
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

warnings.filterwarnings("ignore")
ua = UserAgent()

def driver_conn():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")      # Make the browser Headless. if you don't want to see the display on chrome just uncomment this
    chrome_options.add_argument("--log-level=3")    # Removes error/warning/info messages displayed on the console
    chrome_options.add_argument("--disable-infobars")  # Disable infobars ""Chrome is being controlled by automated test software"  Although is isn't supported by Chrome anymore
    chrome_options.add_argument("start-maximized")     # Make chrome window full screen
    chrome_options.add_argument('--disable-gpu')       # Disable gmaximizepu (not load pictures fully)
    chrome_options.add_argument("--incognito")       # If you want to run browser as incognito mode then uncomment it
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--disable-extensions")     # Will disable developer mode extensions
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")    # retrieve_block
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])    # retrieve_block
    chrome_options.add_experimental_option('useAutomationExtension', False)    # retrieve_block
    chrome_options.add_argument(f'user-agent={ua.random}')

    # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')    # retrieve_block
    chrome_options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')    # retrieve_block
    chrome_options.add_argument('--accept-encoding=gzip, deflate, br')    # retrieve_block
    chrome_options.add_argument('--accept-language=en-US,en;q=0.9')    # retrieve_block
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)  # you don't have to download chromedriver it will be downloaded by itself and will be saved in cache
    return driver


def get_url():
    all_link = []
    driver = driver_conn()
    print('==============================Getting URL==========================')
    url = 'https://www.epiesa.ro/gmtn1:auto/gmtn2:uleiuri-si-lubrifianti-auto/'
    driver.get(url)
    time.sleep(2)
    
    # try:
    #     driver.find_element(By.CSS_SELECTOR, '#button.cc-nb-okagree').click()  # Dismiss cookie consent
    #     time.sleep(1)
    # except:
    #     pass
    
    try:
        # Wait for the cookie consent button to become clickable and try scrolling into view if necessary
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.cc-nb-okagree'))
        )

        # Scroll to the consent button to ensure it's in the viewport
        driver.execute_script("arguments[0].scrollIntoView(true);", consent_button)
        time.sleep(1)  # Give it a moment to ensure it's visible
        
        # Try clicking the button using JavaScript
        driver.execute_script("arguments[0].click();", consent_button)
        print("Cookie consent button clicked")
        time.sleep(1)
    except Exception as e:
        print(f"Error clicking cookie consent button: {e}")
    
  
    page = 0
    while True:
        page += 1
        print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Page: {str(page)}")
        
        # Get the page content
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        try:
            lis = soup.findAll('div', {"class": "sub-product-text"})
        except:
            lis = ''
        
        print("Listing here: ", len(lis))
        
        if len(lis) < 1:
            print("No listing... Ending pagination for this URL")
            break
        
        if len(lis) > 1:
            for li in lis:
                link = ''
                try:
                    link = li.find('a')['href']
                except:
                    pass
                data = {
                    'links': "https://www.epiesa.ro" + str(link)
                }
                print(data)
                if data not in all_link:
                    all_link.append(data)
                    df = pd.DataFrame([data])
                    df.to_csv("firoz.csv", mode="a", header=not os.path.exists("firoz.csv"), encoding="utf-8-sig", index=False)
                else:
                    input("hit enter: ")

        try:
            # Wait for the "next page" button to be clickable
            next_page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'pagmstrn-') and text()='Pagina urmatoare']"))
            )
            print("Found the next page button!")
            
            # Scroll to the button to make sure it's clickable
            driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
            time.sleep(1)  # Give it a moment to ensure the button is fully in view
            
            # Use JavaScript to click the button directly
            driver.execute_script("arguments[0].click();", next_page_button)
            time.sleep(3)  # Allow time for the next page to load
        except Exception as e:
            print(f"Next page button not found or error: {e}")
            print("Ending pagination.")
            break

    driver.quit()

if __name__ == '__main__':
    get_url()
