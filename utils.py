import sqlite3
import pandas as pd
from datetime import date

def initialize_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT aUNIQUE,
            password TEXT,
            age INTEGER,
            gender TEXT,
            medical_history TEXT
        )
    ''')

    # Symptom logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symptom_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            description TEXT,
            severity TEXT,
            date TEXT,
            triage_suggestion TEXT
        )
    ''')

    conn.commit()
    conn.close()

def triage_symptoms(description):
    desc = description.lower()
    if "chest pain" in desc or "shortness of breath" in desc:
        return "Seek emergency care"
    elif "fever" in desc or "headache" in desc:
        return "Self-monitor, consult doctor if persists"
    else:
        return "Consult your doctor"

def save_symptom_entry(user_id, description, severity, date_str, triage_suggestion):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO symptom_logs (user_id, description, severity, date, triage_suggestion)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, description, severity, date_str, triage_suggestion))
    
    conn.commit()
    conn.close()

def show_trend(user_id):
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query(f"SELECT date, severity FROM symptom_logs WHERE user_id={user_id}", conn)
    conn.close()

    if not df.empty:
        df['severity'] = df['severity'].map({"Mild": 1, "Moderate": 2, "Severe": 3})
        import streamlit as st
        st.line_chart(df.set_index('date'))
    else:
        import streamlit as st
        st.info("No symptom data to display yet.")

def export_logs(user_id):
    import pandas as pd
    import sqlite3

    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query(f"SELECT * FROM symptom_logs WHERE user_id={user_id}", conn)
    conn.close()

    # Convert date column to formatted string (YYYY-MM-DD)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    # Export to CSV
    df.to_csv('exported_logs.csv', index=False)

