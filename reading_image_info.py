from PIL import Image
import pytesseract
import re
import os
import _config
import datetime

DATE_FORMAT = "%d-%m-%Y"
# Output directory path
invoices_dir_path = _config.INVOICES_PATH

# List of image file paths


# path to the Tesseract-OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# List to store the extracted information from all images

# Tästä kaksi funktiota !!!

# Function to extract information from an image
def image_to_text_and_extract(image_file):
    date_now = datetime.datetime.now()
    date_ddmmyyyy = date_now.strftime(DATE_FORMAT)
    img = Image.open(image_file)
    # Extract text from image
    text = pytesseract.image_to_string(img)
    # print(f"Text from {image_file}:\n{text}\n")
    
    # Initialize the dictionary to store extracted information
    invoice_data = {'InvoiceNo': '', 'InvoiceDate': '', 'CompanyName': '', 'TotalDue': ''}

    # Extract information using regular expressions
    invoice_number_match = re.search(r'#\s*(\d+)', text)
    invoice_date_match = re.search(r'Date: (\w+ \d+, \d{4})', text)
    total_due_match = re.search(r'Total: \$([\d,]+\.\d+)', text)
    specific_company_match = re.search(r'Sit Amet Corp.', text)

    if not specific_company_match:
        invoice_number_match = re.search(r'#(\d+)', text)
        invoice_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text) # 2019-06-20
        specific_company_match = re.search(r'Aenean LLC', text)
        total_due_match = re.search(r'Total\s*(\d+\.\d+)', text)

    if invoice_number_match:
        invoice_data['InvoiceNo'] = invoice_number_match.group(1)
    if invoice_date_match:
        data_date = invoice_date_match.group(1)
        data_date = datetime.datetime.strptime(data_date, "%Y-%m-%d")
        data_date = datetime.datetime.strftime(data_date, DATE_FORMAT)
        invoice_data['InvoiceDate'] = data_date
    if specific_company_match:
        invoice_data['CompanyName'] = specific_company_match.group(0)
    if total_due_match:
        invoice_data['TotalDue'] = total_due_match.group(1)

    return invoice_data

def iterate_images(image_files):
    all_invoices = []
    # Iterate over the image files and extract information
    # image files = ({"ID": invoice_id, "DueDate": due_date_str, "InvoiceNo": invoice_number, "Picture": picture})
    for image_file in image_files:
        invoice_data = image_to_text_and_extract(image_file["Picture"])
        all_invoices.append(invoice_data)

    # Print the list of all extracted information
    for invoice in all_invoices:
        print(invoice)
    
    return all_invoices

def read_files_in_directory(invoices_dir_path):
    dir_list = os.listdir(invoices_dir_path)
    print("Files and directories in '", invoices_dir_path, "' :")
    # prints all files
    print(dir_list)

    return dir_list


if __name__ == "__main__":
    # List of image file paths
    image_files = read_files_in_directory(invoices_dir_path)