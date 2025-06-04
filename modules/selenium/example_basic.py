from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from testcontainers.selenium import SeleniumContainer


def basic_example():
    with SeleniumContainer() as selenium:
        # Get the Selenium WebDriver
        driver = selenium.get_driver()

        try:
            # Navigate to a test page
            driver.get("https://www.python.org")
            print("Navigated to python.org")

            # Wait for the search box to be present
            search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id-search-field")))

            # Type in the search box
            search_box.send_keys("selenium")
            print("Entered search term")

            # Click the search button
            search_button = driver.find_element(By.ID, "submit")
            search_button.click()
            print("Clicked search button")

            # Wait for search results
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "list-recent-events")))

            # Get search results
            results = driver.find_elements(By.CSS_SELECTOR, ".list-recent-events li")
            print("\nSearch results:")
            for result in results[:3]:  # Print first 3 results
                print(result.text)

            # Take a screenshot
            driver.save_screenshot("python_search_results.png")
            print("\nScreenshot saved as 'python_search_results.png'")

        finally:
            # Clean up
            driver.quit()


if __name__ == "__main__":
    basic_example()
