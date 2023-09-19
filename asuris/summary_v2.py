import csv
import openai

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

# Open the CSV file for reading
with open('mini_pdfstocsv.csv', mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    # Extract the health insurance company name from the bulletin
    health_insurance_company = "Asuris"  # Replace with the actual company name
    
    # Create a new CSV file for writing the summaries
    with open('summaries.csv', mode='w', newline='', encoding='utf-8') as output_file:
        fieldnames = ['Date of Notice', 'Health Insurance Company', 'Line of Business', 'Effective Date of Change', 'Summary of the Recent Update', 'Topic', 'Link to Update']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in csv_reader:
            # Modify this line to match the actual column names in your CSV
            text_to_summarize = row['Text']
            
            # Summarize the text
            summary = summarize_text_gpt3(text_to_summarize)
            
            # Determine the topic based on keywords in the text (customize as needed)
            topic = None
            if 'COVID-19 updates and resources' in text_to_summarize:
                topic = 'Clinical'
            elif 'Medicare Advantage' in text_to_summarize:
                topic = 'Commercial'
            elif 'Genetic Testing' in text_to_summarize:
                topic = 'Clinical'
            
            # Only include items with detected topics
            if topic:
                # Write the summary along with other relevant data to the output CSV
                writer.writerow({
                    'Date of Notice': row['Date'],
                    'Health Insurance Company': health_insurance_company,
                    'Line of Business': 'Line of Business',  # Adjust as needed
                    'Effective Date of Change': row['Date'],
                    'Summary of the Recent Update': summary.strip(),
                    'Topic': topic,
                    'Link to Update': '[Link](Update Not Provided)'
                })

print("Itemized updates have been generated and saved to summaries.csv")
