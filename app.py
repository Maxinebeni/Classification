import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pdfplumber
import validators

# Your trained model goes here
import joblib

# Load your trained model
model = joblib.load('htext_classification_model.pkl')

# Function to extract text from a PDF file
def get_text_from_pdf(uploaded_file):
    try:
        pdf_reader = pdfplumber.open(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from the PDF: {str(e)}")
        return None

# Function to extract text from a URL using Beautiful Soup
def get_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if "example1.com" in url: # Check if the URL contains "example1.com"
            paragraphs = soup.find_all('p') # Adjust this based on the HTML structure of the articles for "example1.com"
        elif "example2.com" in url: # Check if the URL contains "example2.com"
            paragraphs = soup.find_all('div') # Adjust this based on the HTML structure of the articles for "example2.com"
        else:
            paragraphs = soup.find_all('p') # Adjust this based on the HTML structure of the articles for any other domain
            
        text = ' '.join([paragraph.get_text() for paragraph in paragraphs])
        
        # Check if text is empty after extraction
        if not text.strip():
            raise ValueError("Unable to determine content from the website.")
        
        return text
    except Exception as e:
        st.error(f"Error retrieving content from the URL: {str(e)}")
        return None

# Function to classify text using the trained model
def classify_text(text):
    # Your code for model prediction goes here
    # Assume `model.predict(text)` returns 1 for health-related and 0 for non-health-related
    return model.predict([text])

# Streamlit app
def main():
    st.title("Health Article Repository")

    # Input for choosing between URL and PDF upload
    option = st.radio("Choose your option:", ("URL", "Upload PDF"))

    if option == "URL":
        # Input box for the topic of the article
        topic = st.text_input("Topic of your article (e.g., Cancer, HIV/AIDS):")
        
        # User input for the URL
        url = st.text_input("Enter the URL of the article:")
        
        if st.button("POST"):
            if url:
                # Check if the input is a valid URL
                if not urlparse(url).hostname:
                    st.error("Non-URL text entered. Please enter a valid URL and try again.")
                    return
                try:
                    # Extract text from the URL
                    article_text = get_text_from_url(url)
                    # Classify the text
                    prediction = classify_text(article_text)
                    # Display the appropriate message
                    if prediction == 1:
                        st.success("The article is health-related.")
                    else:
                        st.warning("The article is not health-related.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

    elif option == "Upload PDF":
        # Input box for the title of the article
        title = st.text_input("Title of the article:")
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        if st.button("POST"):
            if uploaded_file:
                try:
                    # Extract text from the uploaded PDF file
                    article_text = get_text_from_pdf(uploaded_file)
                    # Classify the text
                    prediction = classify_text(article_text)
                    # Display the appropriate message
                    if prediction == 1:
                        st.success("The article is health-related.")
                    else:
                        st.warning("The article is not health-related.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
