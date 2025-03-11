# Importing python files
import _config, reading_image_info

# Python libraries
import time
import csv
import datetime

from bs4 import BeautifulSoup

# Robocorp imports
from robocorp.tasks import task, setup
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.FileSystem import FileSystem


"""Huom"""
# Sivuja voi olla enemmän kuin 4 ? -> next nappi
# Rivejä voi olle enenmmän kuin 4 ?
# Seleniumin vaihto -> playwrightiin
# dataclass

# Python libraries variables
DATE_NOW = datetime.datetime.now()
DATE_DDMMYYYY = DATE_NOW.strftime("%d-%m-%Y")

# Robcorp variables
http = HTTP()
tables = Tables()
fs = FileSystem()
page = browser.page()

# Variables for paths/urls other
invoices_path = _config.INVOICES_PATH
website_url = _config.WEBSITE_URL


@setup(scope='session')
def before_all(tasks):
    "Runs before the tasks."
    print(f"kansion polku on: {invoices_path}")
    delete_or_create_output_folder(invoices_path)


def delete_or_create_output_folder(directory):
    "Deletes or creates the output folder"
    if fs.does_directory_exist(directory):
        fs.remove_directory(directory, recursive=True)
        print("Kansio poistettu")
    if not fs.does_directory_exist(directory):
        fs.create_directory(directory)
        print("Kansio luotu")

@task
def main():
    """Goes to the website and downloads the invoices
    builds and uploads csv file to the website"""
    open_website()
    click_button_start()
    page_info = click_next_page()
    list = combine_list(page_info)
    create_csv_file(list)
    upload_files()
    # print(arvot)
    

def click_button_start():
    "Clicks the start button in website"
    page.click("button:has-text('START')")

def open_website():
    "Goes to the website"
    browser.goto(website_url)

# pitää ladata kaikki jpg filut mitkä sivulla on sen jälkeen pitää
# tsekata onko seuraava sivu olemassa jos on niin klikataan sitä ja sitten
# taas ladata uudelta sivulta uudet jpg filut

def read_page_info():
    "Downloads the invoice"
    page_content = page.content()
    soup = BeautifulSoup(page_content, 'html.parser')
    rows = soup.select("table tbody tr")
    invoice_list = []
    date_now = datetime.datetime.now()
    date_ddmmyyyy = date_now.strftime("%d-%m-%Y")
    for row in rows:
        columns = row.find_all("td")
        due_date_str = columns[2].text
        due_date = datetime.datetime.strptime(due_date_str, "%d-%m-%Y")
        if due_date <= date_now:
            invoice_number = columns[0].text
            invoice_id = columns[1].text
            download_link = columns[3].find("a")["href"]
            picture = f"output/invoices/{invoice_number}.jpg"
            url = f"{website_url}{download_link}"
            http.download(url, picture, overwrite=True)
            invoice_list.append({"ID": invoice_id, "DueDate": due_date_str, "InvoiceNo": invoice_number, "Picture": picture})

    return invoice_list
def combine_list(page_data):
    "Combines the list of invoices"
    combined_list = []
    dictionary_list = []
    for lists in page_data:
        for dict in lists:
            dictionary_list.append(dict)
        
    image_data = reading_image_info.iterate_images(dictionary_list)

    for i in range(len(dictionary_list)):
        combined_list.append([dictionary_list[i]["ID"],dictionary_list[i]["DueDate"], image_data[i]["InvoiceNo"], image_data[i]["InvoiceDate"], image_data[i]["CompanyName"], image_data[i]["TotalDue"]])
    print(f"LISTA {combined_list}")

    return combined_list

def download_invoices():
    "Downloads the right invoices"
    list_of_invoices = read_page_info()
    # http.download(download_link, f"output/{invoice_number}.jpg", overwrite=True)

def create_csv_file(combined_list):
    "Creates a csv file from the invoices"
    with open("output/invoices.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID","DueDate","InvoiceNo","InvoiceDate","CompanyName","TotalDue"])
        writer.writeheader()
        for row in combined_list:
            print(row)
            writer.writerow({"ID": row[0], "DueDate": row[1], "InvoiceNo": row[2], "InvoiceDate": row[3], "CompanyName": row[4], "TotalDue": row[5]})

def upload_files():
    """Uploads csv file to the website"""
    page.locator("input[type='file']").set_input_files("output/invoices.csv")
    time.sleep(15)
    

def click_next_page():
    "Clicks the next page button"
    page_info = []
    while True:
        page_info.append(read_page_info())
        next_button = page.query_selector("[class='paginate_button next']")
        if next_button:
            next_button.click()
            print("Next page exists")
        else:
            print("Next page does not exist")
            break
    return page_info # [[{},{}],[{},{}][{},{}]]