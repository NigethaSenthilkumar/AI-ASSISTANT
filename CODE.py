import streamlit as st
import speech_recognition as sr
import pyttsx3
import pdfplumber
from groq import Groq
from PIL import Image
import google.generativeai as genai
import io

# ✅ FIX: Set page config FIRST!
st.set_page_config(page_title="AI Assistant", layout="wide")

# Initialize AI Clients
@st.cache_resource
def init_clients():
    groq_client = Groq(api_key="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")  # Replace with actual key
    genai.configure(api_key="AIzaSyAFRxV8lXIHlQLgNKXZ47ZU3w8eJF6Smmg")  # Replace with actual key
    return groq_client

groq_client = init_clients()

@st.cache_resource
def init_model():
    return genai.GenerativeModel('gemini-1.5-flash-latest')

model = init_model()

engine = pyttsx3.init()

def process_text_input(prompt):
    """Processes a text-based input and gets a response from AI."""
    try:
        response = groq_client.chat.completions.create(
            messages=[{'role': 'system', 'content': "You are an AI assistant."},
                      {'role': 'user', 'content': prompt}],
            model='llama3-70b-8192',
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in processing text: {str(e)}")
        return "Sorry, I encountered an error."

def recognize_voice():
    """Captures voice input and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand your speech.")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def extract_text_from_pdf(pdf_file):
    """Extracts text from uploaded PDFs."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text if text else "No readable text found in the PDF."
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return "Could not process the PDF file."

def process_uploaded_file(uploaded_file):
    """Processes uploaded files (Image, PDF, or Text)."""
    if uploaded_file.type in ["image/png", "image/jpeg"]:
        img = Image.open(uploaded_file)
        response = model.generate_content(["Describe this image", img])
        return response.text
    elif uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
        return process_text_input(text)
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
        return process_text_input(text)
    else:
        return "Unsupported file type."

st.title("🤖 AI Assistant")

user_input = st.text_input("📝 Enter your question:")

if st.button("🎙️ Speak Your Question"):
    with st.spinner("Listening..."):
        voice_text = recognize_voice()
        if voice_text:
            response = process_text_input(voice_text)
            st.write(f"🤖 AI Answer: {response}")

uploaded_file = st.file_uploader("📂 Upload a file (PDF, Image, or Text)", type=["png", "jpg", "jpeg", "pdf", "txt"])
if uploaded_file:
    with st.spinner("Processing file..."):
        file_response = process_uploaded_file(uploaded_file)
        st.write(f"🤖 AI Answer: {file_response}")

if st.button("📤 Get Answer"):
    if user_input:
        with st.spinner("Processing..."):
            response = process_text_input(user_input)
            st.write(f"🤖 AI Answer: {response}")
    else:
        st.warning("Please enter a question or upload a file.")
