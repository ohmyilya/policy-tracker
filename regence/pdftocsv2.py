import os
import requests
from bs4 import BeautifulSoup
import csv
from PyPDF2 import PdfReader
import pandas as pd
from tqdm import tqdm
from dateutil.parser import parse

# Define the URL of the webpage containing PDF links
webpage_url = "https://www.regence.com/provider/library/bulletins"
pdf_urls_csv = "pdfs_urls.csv"
pdfs_folder = "pdfs"
pdfstocsv_file = "pdfstocsv.csv"

# Function to download PDFs from a webpage and save their URLs to a CSV file
def download_pdfs_and_save_urls(url, csv_file):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    pdf_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.pdf'):
            pdf_links.append(href)

    # Save the PDF URLs to a CSV file
    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ["PDF URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pdf_url in pdf_links:
            writer.writerow({"PDF URL": pdf_url})

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

# Download PDFs and save their URLs to the CSV file
download_pdfs_and_save_urls(webpage_url, pdf_urls_csv)

# Download PDFs from the CSV file with progress bar
pdf_urls = pd.read_csv(pdf_urls_csv)
pdf_urls = pdf_urls["PDF URL"].tolist()
for pdf_url in tqdm(pdf_urls, desc="Downloading PDFs", unit="file"):
    download_pdf(pdf_url, pdfs_folder)

# Extract text from downloaded PDFs and save to pdfstocsv.csv
pdf_text_data = []
for pdf_file_name in tqdm(os.listdir(pdfs_folder), desc="Extracting Text", unit="file"):
    pdf_file_path = os.path.join(pdfs_folder, pdf_file_name)
    pdf_text = extract_text_from_pdf(pdf_file_path)
    pdf_text_data.append({"Domain": webpage_url, "PDF File": pdf_file_name, "Text": pdf_text})

# Create a DataFrame from the extracted data and save to pdfstocsv.csv
pdf_text_df = pd.DataFrame(pdf_text_data)
pdf_text_df["Date"] = pdf_text_df["PDF File"].apply(lambda x: x.split("-")[-2])
pdf_text_df["Year"] = pdf_text_df["PDF File"].apply(lambda x: x.split("-")[-1].split(".pdf")[0])
pdf_text_df = pdf_text_df.sort_values(by=["Year", "Date"], ascending=False)
pdf_text_df.to_csv(pdfstocsv_file, index=False)

print(f"Extracted text from {len(pdf_text_data)} PDFs and saved to {pdfstocsv_file}")
