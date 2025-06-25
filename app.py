import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Model
import sqlite3

# Connect to SQLite DB (or create if it doesn't exist)
conn = sqlite3.connect("healthai.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    location TEXT,
    medical_history TEXT,
    current_medication TEXT,
    allergies TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    user_input TEXT,
    ai_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
# Load .env file for credentials (if needed later)
load_dotenv()
API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

# Page setup
st.set_page_config(page_title="HealthAI", layout="centered")

# App heading
st.markdown("<h1 style='text-align: center;'>🩺 HealthAI - Intelligent Healthcare Assistant</h1>", unsafe_allow_html=True)

# Sidebar – Full Patient Profile form
with st.sidebar:
    st.markdown("## 🧑‍⚕ Patient Profile")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    location = st.text_input("Location")
    medical_history = st.text_area("Medical History")
    current_Medication=st.text_area("current Medication")
    Allergies=st.text_area("Allergies")
# Main content – Support and Chat
st.subheader("🕒 24/7 Patient Support")
st.write("Ask any health-related question for immediate assistance.")



menu = st.sidebar.selectbox("📋 Choose a Feature", 
                            ["🏠 Home", "🧠 Disease Prediction", "💊 Treatment Plan", "💬 Patient Chat", "📊 Health Analytics"])

if menu == "🏠 Home":
    st.write("")
    st.markdown("""
       
    """)

elif menu == "🧠 Disease Prediction":
    st.header("🧠 Disease Prediction")
    symptoms = st.text_area("Enter your symptoms (comma separated)", placeholder="e.g., fever, cough, headache")
    if st.button("🔍 Predict"):
        if "fever" in symptoms and "cough" in symptoms:
            st.success("🤒 You might have Flu or COVID-19. Please consult a doctor.")
        elif "headache" in symptoms and "fatigue" in symptoms:
            st.success("😓 You may be experiencing Migraine or Viral infection.")
        else:
            st.warning("❓ No clear prediction. Try different symptoms or consult a professional.")

elif menu == "💊 Treatment Plan":
    st.header("💊 Treatment Plan Generator")
    condition = st.text_input("Enter diagnosed disease", placeholder="e.g., Diabetes")
    if st.button("📋 Generate Plan"):
        st.write(f"🔎 Treatment plan for {condition}:")
        st.markdown("""
        - 💊 Take medications as prescribed  
        - 🥗 Follow a healthy diet  
        - 🧘‍♂ Do regular exercise  
        - 🩺 Attend follow-up checkups  
        """)

elif menu == "💬 Patient Chat":
    st.header("💬 Ask Your Health Question")
    question = st.text_input("Type your health question here")
    if st.button("🧠 Get AI Answer"):
        st.write("🤖 This is a simulated AI response. Please consult a doctor for accurate advice.")

elif menu == "📊 Health Analytics":
    st.header("📊 Health Analytics Dashboard")
    data = {
        'Date': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        'Heart Rate': [72, 75, 78, 76, 74],
        'Blood Pressure': [120, 122, 121, 124, 123]
    }
    df = pd.DataFrame(data)
    st.line_chart(df.set_index('Date'))



if st.sidebar.button("💾 Save Profile"):
    cursor.execute('''
        INSERT INTO patients (name, age, gender, location, medical_history, current_medication, allergies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, gender, location, medical_history, current_Medication, Allergies))
    conn.commit()
    st.sidebar.success("Profile saved successfully!")



# Chat system with history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# IBM Credentials
api_key = "ZPvG-12ijx5ATRN6BQ55q9hI5iqQrF5B5c55VHWYyV-U"
project_id = "693633cd-ac3b-4230-9eda-e179323e00a7"
base_url = "https://us-south.ml.cloud.ibm.com"

# Initialize the model


# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages
for i in range(0, len(st.session_state.chat_history), 2):
    if i < len(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(st.session_state.chat_history[i])
    if i + 1 < len(st.session_state.chat_history):
        st.chat_message("assistant").write(st.session_state.chat_history[i + 1])


    # Get response from the model
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                model_id="ibm/granite-13b-chat-v2"
                model = Model(
                    model_id=model_id,
                    credentials={
                        "apikey": api_key,
                        "base_url": base_url
                    },
                    project_id=project_id
                )

                response = model.generate_text(
                    prompt=user_input,
                    max_new_tokens=100,
                    temperature=0.7,
                )
                assistant_reply = response['results'][0]['generated_text']
                st.session_state.chat_history.append(assistant_reply)
                st.write(assistant_reply)

            except Exception as e:
                st.write("Error:", e)