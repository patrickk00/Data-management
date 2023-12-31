import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from utils.utils import get_reviews, save_in_csv
import concurrent.futures
import threading


ignored_exceptions = (
    NoSuchElementException,
    StaleElementReferenceException,
)

driver = webdriver.Chrome()


driver.get("https://www.tripadvisor.it/Restaurants-g187849-Milan_Lombardy.html")
driver.maximize_window()

restaurantsList = []
reviewList = []
print("helloooo")
time.sleep(5)

# accept cookies
WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(
        (By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
    )
).click()

count = 0
while count < 1:
    count += 1
    time.sleep(2)
    # find table with restaurant list in the page
    elem = driver.find_element(By.CLASS_NAME, "YtrWs")
    # list of restaurants
    elements = elem.find_elements(By.XPATH, "//div[@class='zdCeB Vt o']")

    for e in elements:
        button = e.find_element(By.TAG_NAME, "a")
        actions = ActionChains(driver)
        actions.move_to_element(button).perform()
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(button)).click()

    for e in elements:
        if e.text.find("Sponsorizzato") == -1:
            try:
                title = e.find_element(By.TAG_NAME, "a")
                reviews = e.find_element(By.CLASS_NAME, "LBKCf")
                reviews_number = e.find_element(By.CLASS_NAME, "IiChw")
                reviews_bubble = reviews.find_element(By.TAG_NAME, "svg")
                r_b = reviews_bubble.get_attribute("aria-label")

                type = e.find_element(By.CLASS_NAME, "bAdrM")
                type_elems = type.find_elements(By.CLASS_NAME, "qAvoV")

                if len(type_elems) < 1:
                    cook_type = "?"
                else:
                    cook_type = type_elems[0].text
                if len(type_elems) < 2:
                    expensive = "?"
                else:
                    expensive = type_elems[1].text
                title = title.text
                r_bubbles = r_b
                r_number = reviews_number.text
                cook_type = cook_type
                expensive = expensive
                restaurant = {
                    "title": title,
                    "r_bubbles": r_bubbles,
                    "r_number": r_number,
                    "cook_type": cook_type,
                    "expensive": expensive,
                }
                print("////////////////////////")
                print(restaurant)
                restaurantsList.append(restaurant)
            except Exception as e:
                print("EXCEPTION", e)
                # save_in_csv(restaurantsList, reviewList)
                pass

        else:
            print("SPONSORIZZATO")

    if len(driver.find_elements(By.XPATH, '//span[@class="nav next disabled"]')) != 0:
        break
    else:
        try:
            WebDriverWait(driver, 30, ignored_exceptions=ignored_exceptions).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//a[@class="nav next rndBtn ui_button primary taLnk"]')
                )
            )
            element = driver.find_element(
                By.XPATH, '//a[@class="nav next rndBtn ui_button primary taLnk"]'
            )

            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//a[@class="nav next rndBtn ui_button primary taLnk"]')
                )
            ).click()
        except Exception as e:
            print("EXCEPTIONN")
            print("EXCEPTIONN", e)
            # save_in_csv(restaurantsList, reviewList)
            element = driver.find_element(
                By.XPATH, '//a[@class="nav next rndBtn ui_button primary taLnk"]'
            )
            link = element.get_attribute("href")
            driver.get(link)
            pass
        # driver.find_element(By.XPATH, './/a[@class="nav next rndBtn ui_button primary taLnk"]').click()

#
main_window_handle = driver.current_window_handle


def extract_reviews(handle):
    if handle != main_window_handle:
        driver.switch_to.window(handle)
        try:
            WebDriverWait(driver, 30).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, '//div[@class="rev_wrap ui_columns is-multiline"]')
                )
            )
            reviews = []
            restaurant = driver.find_element(
                By.XPATH, "h1[@data-test-target='top-info-header']"
            )
            rev = driver.find_elements(
                By.XPATH, '//div[@class="rev_wrap ui_columns is-multiline"]'
            )
            for r in rev:
                bubbles = r.find_element(
                    By.CLASS_NAME, "ui_bubble_rating"
                ).get_attribute("class")
                title = r.find_element(By.TAG_NAME, "a").text
                description = r.find_element(By.CLASS_NAME, "partial_entry").text
                reviews.append(
                    {
                        "restaurant": restaurant,
                        "bubbles": bubbles.split(" ")[1],
                        "title": title,
                        "description": description,
                    }
                )
        except:
            df = pd.DataFrame(reviews)
            df.to_csv("reviews_except.csv", index=False)
            pass
        # driver.close()
        # driver.switch_to.window(main_window_handle)
        return reviews


with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [
        executor.submit(extract_reviews, handle) for handle in driver.window_handles
    ]
    reviewList = [result.result() for result in results]

# save_in_csv(restaurantsList, reviewList)


# elem.clear()
driver.close()
