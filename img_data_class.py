from dataclasses import dataclass


@dataclass
class ImgData:
    """Dataclass for image data"""
    invoice_no: str
    invoice_date: str
    company_name: str
    total_due: str
    image_file: str

    "ID","DueDate","InvoiceNo","InvoiceDate","CompanyName","TotalDue"