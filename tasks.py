import time
import _config
import csv

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By

# Robocorp imports
from robocorp.tasks import task, setup
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.FileSystem import FileSystem


"""Huom"""
# Sivuja voi olla enemmän kuin 4 ? -> next nappi
# Rivejä voi olle enenmmän kuin 4 ?

# Robcorp variables
page = browser.page()
http = HTTP()
tables = Tables()
fs = FileSystem()

# Variables for paths/urls
ouput_dir_path = _config.OUTPUT_DIR_PATH
website_url = _config.WEBSITE_URL

# Selenium variables
driver = webdriver.Chrome()

# @setup(scope='session')
# def before_all(tasks):
#     "Runs before the tasks."
#     print(f"kansion polku on: {ouput_dir_path}")
#     delete_or_create_output_folder(ouput_dir_path)


def delete_or_create_output_folder(directory):
    "Deletes or creates the output folder"
    if fs.does_directory_exist(directory):
        fs.remove_directory(directory)
        print("Kansio poistettu")
    else:
        fs.create_directory(directory)
        print("Kansio luotu")


@task
def main():
    """Goes to the website and downloads the invoices
    builds and uploads csv file to the website"""
    open_website()
    arvot = download_invoices()
    create_csv_file(arvot)
    #click_button_start()
    click_next_page()
    print(arvot)

def click_button_start():
    "Clicks the start button in website"
    page.click("button:has-text('START')")

def open_website():
    "Goes to the website"
    driver.get(website_url)

# pitää ladata kaikki jpg filut mitkä sivulla on sen jälkeen pitää
# tsekata onko seuraava sivu olemassa jos on niin klikataan sitä ja sitten
# taas ladata uudelta sivulta uudet jpg filut


def download_invoices():
    "Downloads the invoice"
    rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
    invoice_list = []
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        invoice_number = columns[0].text
        invoice_id = columns[1].text
        due_date = columns[2].text
        download_link = columns[3].find_element(By.TAG_NAME, "a").get_attribute("href")
        http.download(download_link, f"output/{invoice_number}.jpg", overwrite=True)
        invoice_list.append({"ID": invoice_id, "DueDate": due_date})
    
    return invoice_list

def create_csv_file(invoice_list):
    "Creates a csv file from the invoices"
    with open("output/invoices.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID","DueDate","InvoiceNo","InvoiceDate","CompanyName","TotalDue"])
        writer.writeheader()
        writer.writerows(invoice_list)


def click_next_page():
    "Clicks the next page button"
    
    while True:
        download_invoices()
        next_button = driver.find_elements(By.CSS_SELECTOR, "[class='paginate_button next']")
        if next_button:
            try:
                next_button[0].click()
                print("Next page exists")
            except Exception as e:
                print(f"Failed to click next page: {e}")
                break
        else:
            print("Next page does not exist")
            break