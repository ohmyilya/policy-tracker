import os
import requests
import csv
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import pandas as pd
from tqdm import tqdm
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time  # Add this import for sleep

# Define the URL of the webpage containing PDF links
webpage_url = "https://www.regence.com/provider/library/bulletins"
pdfs_folder = "pdfs"
pdfstocsv_file = "pdfstocsv.csv"

# Function to download a PDF given its URL and save it to the specified folder
def download_pdf(pdf_url, folder):
    response = requests.get(pdf_url)
    filename = os.path.join(folder, os.path.basename(pdf_url))
    with open(filename, 'wb') as pdf_file:
        pdf_file.write(response.content)

# Function to extract text from a PDF file and return it as a string
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Create the folder to store downloaded PDFs
if not os.path.exists(pdfs_folder):
    os.makedirs(pdfs_folder)

# Initialize the Chrome WebDriver
chrome_service = webdriver.chrome.service.Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=chrome_service)

# Fetch the webpage and wait for ZIP code input field
driver.get(webpage_url)
try:
    zip_code_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "zip-code-field"))
    )
except Exception as e:
    print("Failed to locate ZIP code field:", str(e))
    driver.quit()
    exit(1)

# Type the ZIP code into the input field
zip_code_field = driver.find_element(By.ID, "zip-code-field")
zip_code_field.clear()  # Clear any existing text in the field
zip_code_field.send_keys("98101")  # Type the ZIP code

# Input the ZIP code
if zip_code_field:
    zip_code_field.send_keys("98101")

    # Locate and click the "Set ZIP" button
    try:
        set_zip_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Set ZIP')]"))
        )
        set_zip_button.click()
    except Exception as e:
        print("Failed to click 'Set ZIP' button:", str(e))
        driver.quit()
        exit(1)

    # Add a 5-second delay here (you can adjust this duration as needed)
    time.sleep(5)

# Fetch the webpage again after setting the ZIP code
driver.get(webpage_url)

# Find all PDF links on the webpage
pdf_links = []
for link in driver.find_elements(By.XPATH, "//a[@href]"):
    href = link.get_attribute("href")
    if href and href.endswith('.pdf'):
        pdf_links.append(href)

# Download PDFs from the webpage with progress bar
for pdf_url in tqdm(pdf_links, desc="Downloading PDFs", unit="file"):
    download_pdf(pdf_url, pdfs_folder)

# Extract text from downloaded PDFs and save to pdfstocsv.csv
pdf_text_data = []
for pdf_file_name in tqdm(os.listdir(pdfs_folder), desc="Extracting Text", unit="file"):
    pdf_file_path = os.path.join(pdfs_folder, pdf_file_name)
    pdf_text = extract_text_from_pdf(pdf_file_path)
    date = parse(pdf_file_name.split(".pdf")[0], fuzzy=True)
    pdf_text_data.append({"Domain": webpage_url, "PDF File": pdf_file_name, "Text": pdf_text, "Date": date})

# Sort the data by date
pdf_text_data.sort(key=lambda x: x["Date"], reverse=True)

# Create a DataFrame from the extracted data and save to pdfstocsv.csv
pdf_text_df = pd.DataFrame(pdf_text_data)
pdf_text_df.to_csv(pdfstocsv_file, index=False)

# Quit the WebDriver
driver.quit()

print(f"Extracted text from {len(pdf_text_data)} PDFs and saved to {pdfstocsv_file}")
