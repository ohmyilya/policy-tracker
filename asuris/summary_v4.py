import csv
import openai
import requests
from PyPDF2 import PdfReader
from time import sleep

# Replace with your OpenAI API key
api_key = "place the key here"

# Function to summarize text using OpenAI GPT-3
def summarize_text_gpt3(text):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        max_tokens=200,  # Adjust the max_tokens as needed for your summary length
        temperature=0.7,  # You can adjust the temperature for generating diverse summaries
        stop=None  # You can specify additional stop words as needed
    )
    return response.choices[0].text

# Function to extract text from a PDF URL
def extract_text_from_pdf_url(pdf_url):
    response = requests.get(pdf_url)
    with open("temp.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)

    pdf_text = ""
    pdf = PdfReader("temp.pdf")
    for page in pdf.pages:
        pdf_text += page.extract_text()

    return pdf_text

# PDF URL to summarize
pdf_url = "https://beonbrand.getbynder.com/m/1ae5ccebf197b637/original/The-Bulletin-September-2023.pdf"

# Extract text from the PDF URL
pdf_text = extract_text_from_pdf_url(pdf_url)

# Prompt for summarization
prompt = """Provide itemized updates in chart format from the health plan monthly bulletin below. The itemized updates should include the following columns for each specific update: Date of Notice, Health Insurance Company, Line of Business (either Medicare Advantage or Commercial), Effective Date of Change, Summary of the Recent Update, Topic (clinical, reimbursement, pharmacy, or billing), and Link to Update (if available).

“Medical” topics = “clinical” in this itemized update. If a topic is not mentioned in the bulletin or does not have a recent update, do not include it in the output. The health insurance company name is listed at the bottom of the monthly bulletin. The date of notice is at the top of the monthly bulletin and should be the same for all updates. Formatting should be consistent throughout the chart. The summary of the recent update should include a 1 sentence overview and should not include bullet points."""

# Summarize the text
summary = summarize_text_gpt3(prompt + "\n" + pdf_text)

# Create a CSV file to write the summary
with open('summary.csv', mode='w', newline='', encoding='utf-8') as output_file:
    fieldnames = ['Summary']
    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'Summary': summary})

print("Summary has been generated and saved to summary.csv")
