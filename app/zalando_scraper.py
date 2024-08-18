import re
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def fetch_zalando_page_content(cookies):

    #options.add_argument("--headless")  # Ensure this runs headless on the server
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--verbose")  # Enable verbose logging

    # Initialize the WebDriver with modified options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the Zalando Lounge page
        driver.get('https://www.zalando-lounge.pl')
        time.sleep(5)

        # Add cookies to the browser from Flask
        print("Cookies being added to Selenium:")
        for name, value in cookies.items():
            print(f"Name: {name}, Value: {value}")
            # Set the correct domain for Zalando Lounge
            driver.add_cookie({
                'name': name,
                'value': value,
                'domain': '.zalando-lounge.pl',  # Change to Zalando Lounge domain
                'path': '/campaigns/ZZO2XDJ/categories/60457365/articles/NE215O0DH-Q11',  # Make sure the path is correct
            })

        driver.get_cookies()  # Retrieve all cookies from Selenium
        for cookie in driver.get_cookies():
            print(f"Selenium Cookie: {cookie}")
        # Refresh the page to apply the cookies
        driver.refresh()
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        # Wait for dynamic content to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "product-card__title")))

        # Extract the page content
        page_content = driver.page_source
        print(page_content)

        if not page_content:
            raise ValueError("Failed to retrieve page content")

        return page_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()

def check_sizes_in_page_source(page_content, defined_sizes):
    try:
        # Assume we're using a regex to find sizes and stock statuses in the page content
        simples_pattern = re.compile(r'simples:\s*\[(.*?)\]', re.DOTALL)
        simples_match = simples_pattern.search(page_content)

        if not simples_match:
            raise ValueError("No 'simples' data found in the page content")

        simples_data = simples_match.group(1)

        size_pattern = re.compile(r'size:\s*"([\d\.]+)"')
        stock_status_pattern = re.compile(r'stockStatus:\s*"(\w+)"')

        sizes = size_pattern.findall(simples_data)
        stock_statuses = stock_status_pattern.findall(simples_data)

        size_stock_status = {}
        if sizes and stock_statuses and len(sizes) == len(stock_statuses):
            for size, stock_status in zip(sizes, stock_statuses):
                size_stock_status[float(size)] = stock_status

        # Filter results based on the defined sizes
        filtered_status = {size: size_stock_status.get(size, "Not Found") for size in defined_sizes}

        return filtered_status
    except Exception as e:
        # Log the error and return it for debugging
        return {'error': str(e)}
