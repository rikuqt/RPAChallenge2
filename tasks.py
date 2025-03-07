import time
import _config

# Selenium imports and setup/variables
from selenium import webdriver
from selenium.webdriver.common.by import By

# Robocorp imports
from robocorp.tasks import task, get_output_dir, setup
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.FileSystem import FileSystem


# Variables for Robocorp
page = browser.page()
http = HTTP()
tables = Tables()
fs = FileSystem()

# Variables for paths/urls
output_dir_path = _config.OUTPUT_DIR_PATH
website_url = _config.WEBSITE_URL

# Selenium setup
driver = webdriver.Chrome()
driver.get(website_url)

"""Huom"""
# Sivuja voi olla enemmän kuin 4 ? -> next nappi
# Rivejä voi olle enenmmän kuin 4 ?

@setup(scope='session')
def before_all(tasks):
    """Deletes the output directory if it exists
    and creates a new one"""
    delete_or_create_output_directory(output_dir_path)
    

@task
def main():
    open_website()
    # download_invoices()
    # click_button_start()
    time.sleep(2)

def delete_or_create_output_directory(directory):
    """Deletes the directories if they exist"""
    if fs.does_directory_exist(directory) == False:
        fs.remove_directory(directory, recursive=True)
    else:
        fs.create_directory(directory)


def click_button_start():
    "Clicks the start button in website"
    page.click("button:has-text('START')")

def open_website():
    "Goes to the website"
    browser.goto("https://rpachallengeocr.azurewebsites.net/")

def download_invoices():
    "Downloads the invoice"
    rows = driver.find_elements(By.XPATH, "/html/body/div/div/div[2]") 

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        invoice_number = columns[0].text
        invoice_id = columns[1].text
        due_date = columns[2].text
        download_link = columns[3].find_element(By.TAG_NAME, "a").get_attribute("href")
        http.download(download_link, f"output/{invoice_number}.jpg", overwrite=True)

        print(f"Invoice #: {invoice_number}, ID: {invoice_id}, Due Date: {due_date}, Download: {download_link}")
        driver.quit()


def click_next_page():
    "Clicks the next page button"
    if page.query_selector("[class'paginate_button next']") != None:
        page.click("[class='paginate_button next']")
    else:
        pass

def get_table_data():
    pass