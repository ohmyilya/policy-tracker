import csv
import openai

# Replace with your OpenAI API key
api_key = "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"

# Function to summarize text using OpenAI GPT-3
def summarize_text_gpt3(text):
    openai.api_key = api_key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        max_tokens=50,  # Adjust the max_tokens as needed for your summary length
        temperature=0.7,  # You can adjust the temperature for generating diverse summaries
        stop=None  # You can specify additional stop words as needed
    )
    return response.choices[0].text

# Open the CSV file for reading
with open('mini_pdfstocsv.csv', mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    # Create a new CSV file for writing the summaries
    with open('summaries.csv', mode='w', newline='', encoding='utf-8') as output_file:
        fieldnames = ['Date of Notice', 'Health Plan', 'Line of Business', 'Effective Date', 'Summary of Update (250 characters)', 'Link to Update']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in csv_reader:
            # Modify this line to match the actual column names in your CSV
            text_to_summarize = row['Text']
            
            # Summarize the text
            summary = summarize_text_gpt3(text_to_summarize)
            
            # Write the summary along with other relevant data to the output CSV
            writer.writerow({
                'Date of Notice': row['Date'],
                'Health Plan': '',  # Fill in as needed
                'Line of Business': '',  # Fill in as needed
                'Effective Date': '',  # Fill in as needed
                'Summary of Update (250 characters)': summary,
                'Link to Update': ''  # Fill in as needed
            })

print("Summaries have been generated and saved to summaries.csv")
