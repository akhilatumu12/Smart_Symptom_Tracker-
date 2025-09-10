import streamlit as st
from datetime import date, datetime, timedelta
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
import re
import json
from textblob import TextBlob
import numpy as np

# Page configuration
st.set_page_config(
    page_title="HealthVault - Smart Symptom Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded for better navigation
)

# Enhanced Custom CSS with Sidebar styling
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Enhanced Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        color: white;
        width: 320px !important;
        min-width: 320px !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    /* Sidebar navigation menu styling */
    .sidebar-nav-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        margin: 15px 0;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 18px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-nav-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 12px;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: 500;
    }
    
    .sidebar-nav-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    .sidebar-nav-item.active {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        font-weight: 700;
    }
    
    /* Language selection buttons - Enhanced styling */
    [data-testid="stSidebar"] .stButton > button {
        background: white !important;
        color: #6366f1 !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin: 8px 0 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f8f9fa !important;
        color: #6366f1 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
        border-color: #6366f1 !important;
    }
    
    /* User profile section in sidebar */
    .sidebar-profile {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-profile .profile-avatar {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #10b981, #059669);
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .sidebar-profile .profile-name {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 5px;
    }
    
    .sidebar-profile .profile-role {
        font-size: 12px;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Language selector section */
    .language-selector {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        margin: 15px 0;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .language-title {
        text-align: center;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 15px;
        color: white;
    }
    
    /* Custom background */
    .stApp {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main container styling */
    .main-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1.5rem auto;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        max-width: 480px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Logo and title styling */
    .logo-container {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .logo {
        width: 90px;
        height: 90px;
        background: linear-gradient(135deg, #10b981, #059669);
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1f2937, #374151);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Enhanced form styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 14px 18px;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background-color: #f9fafb;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #10b981;
        background-color: white;
        box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
        outline: none;
        transform: translateY(-1px);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4);
        background: linear-gradient(135deg, #059669, #047857);
    }
    
    /* Toggle buttons styling */
    .toggle-container {
        display: flex;
        background: #f3f4f6;
        border-radius: 16px;
        padding: 6px;
        margin-bottom: 2rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .toggle-btn {
        flex: 1;
        padding: 14px;
        text-align: center;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .toggle-btn.active {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transform: translateY(-1px);
    }
    
    .toggle-btn:not(.active) {
        color: #6b7280;
    }
    
    /* Enhanced success/error messages */
    .success-message {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        color: #991b1b;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #ef4444;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    }
    
    /* Persistent triage result styling */
    .triage-result {
        background: linear-gradient(135deg, #e0f2fe, #b3e5fc);
        color: #0277bd;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border-left: 5px solid #0288d1;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 20px rgba(2, 136, 209, 0.2);
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Enhanced dashboard styling */
    .dashboard-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
    }
    
    .dashboard-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid #f3f4f6;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
    }
    
    /* Fixed metric cards - only show when there's data */
    .metric-card {
        text-align: center;
        padding: 2rem 1.5rem;
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 20px;
        margin: 0.5rem;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-color: #10b981;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Health profile styling */
    .health-profile {
        background: linear-gradient(135deg, #fef7ff, #f3e8ff);
        border: 2px solid #d8b4fe;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .profile-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(139, 92, 246, 0.1);
    }
    
    .profile-item:last-child {
        border-bottom: none;
    }
    
    /* Health Trends specific styling */
    .trend-insight {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-weight: 600;
        color: #92400e;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .trend-positive {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border-color: #10b981;
        color: #065f46;
    }
    
    .trend-warning {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border-color: #ef4444;
        color: #991b1b;
    }
    
    .trends-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .trend-stat-card {
        background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid #cbd5e1;
        transition: all 0.3s ease;
    }
    
    .trend-stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        border-color: #10b981;
    }
    
    .trend-stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .trend-stat-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f4f6;
        border-radius: 50%;
        border-top-color: #10b981;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Trends tabs styling */
    .trend-tab-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
        margin: 1rem 0;
        display: flex;
        gap: 0.5rem;
    }
    
    .trend-tab {
        flex: 1;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        background: transparent;
        border: none;
        cursor: pointer;
        font-weight: 600;
        color: #64748b;
        transition: all 0.3s ease;
    }
    
    .trend-tab.active {
        background: white;
        color: #1e293b;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Database functions (keeping all your existing functions intact)
def fix_symptom_table():
    """Fix the symptom_logs table structure to match our insert queries"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Drop and recreate the symptom_logs table with correct schema
    cursor.execute("DROP TABLE IF EXISTS symptom_logs")
    cursor.execute("""
        CREATE TABLE symptom_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            duration_hours INTEGER,
            pain_scale INTEGER,
            temperature REAL,
            triage_result TEXT,
            triage_confidence REAL,
            additional_notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def initialize_enhanced_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Check if users table exists and has all required columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    required_columns = ['email', 'height', 'weight', 'blood_type', 'allergies', 'medications', 'emergency_contact']
    missing_columns = [col for col in required_columns if col not in columns]
    
    if missing_columns:
        # Drop and recreate the users table with enhanced health profile
        cursor.execute("DROP TABLE IF EXISTS users")
        st.success("🔄 Updating database with enhanced health profiles...")
    
    # Create enhanced users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            height REAL,
            weight REAL,
            blood_type TEXT,
            allergies TEXT DEFAULT '',
            medications TEXT DEFAULT '',
            emergency_contact TEXT DEFAULT '',
            medical_history TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Fix symptom logs table
    fix_symptom_table()
    
    # Health trends table for additional metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            metric_type TEXT NOT NULL,
            metric_value REAL NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database
initialize_enhanced_db()

# Enhanced Multi-language support with more comprehensive translations
LANGS = {
    "English": {
        "title": "HealthVault",
        "subtitle": "Smart Symptom Tracker & AI Health Assistant",
        "welcome": "Welcome to HealthVault",
        "login": "Sign In",
        "register": "Create Account",
        "username": "Username",
        "email": "Email Address",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "age": "Age",
        "gender": "Gender",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "blood_type": "Blood Type",
        "allergies": "Known Allergies",
        "medications": "Current Medications",
        "emergency_contact": "Emergency Contact",
        "medical_history": "Medical History (Optional)",
        "symptom_desc": "Describe your symptoms",
        "severity": "Severity Level",
        "duration": "Duration (hours)",
        "pain_scale": "Pain Scale (1-10)",
        "temperature": "Temperature (°C)",
        "submit": "Submit Symptom",
        "triage": "AI Health Recommendation",
        "trend": "📈 Health Trends",
        "export": "💾 Export Data",
        "logout": "🚪 Sign Out",
        "profile": "👤 Health Profile",
        "dashboard": "🏠 Dashboard",
        "symptoms": "📝 Log Symptoms",
        #"analytics": "📊 Analytics",
        "settings": "⚙ Settings",
        "help": "❓ Help & Support",
        "navigation": "🧭 Navigation",
        "language": "🌐 Language",
        "dashboard_welcome": "Welcome to your Personal Health Dashboard",
        "recent_symptoms": "Recent Health Entries",
        "no_user": "❌ Invalid credentials. Please try again.",
        "success_reg": "✅ Account created successfully! Welcome to HealthVault.",
        "user_exists": "⚠ Username already exists. Please choose another.",
        "email_exists": "⚠ Email already registered. Please use another email.",
        "password_mismatch": "⚠ Passwords don't match. Please try again.",
        "fill_required": "Please fill in all required fields",
        "invalid_email": "Please enter a valid email address"
    },
    "తెలుగు": {
        "title": "హెల్త్‌వాల్ట్",
        "subtitle": "స్మార్ట్ లక్షణాల ట్రాకర్ & AI హెల్త్ అసిస్టెంట్",
        "welcome": "హెల్త్‌వాల్ట్‌కు స్వాగతం",
        "login": "లాగిన్",
        "register": "రిజిస్టర్",
        "username": "వాడుకరి పేరు",
        "email": "ఇమెయిల్ చిరునామా",
        "password": "పాస్‌వర్డ్",
        "confirm_password": "పాస్‌వర్డ్ నిర్ధారించండి",
        "age": "వయస్సు",
        "gender": "లింగం",
        "height": "ఎత్తు (సెం.మీ)",
        "weight": "బరువు (కిలోలు)",
        "blood_type": "రక్త వర్గం",
        "allergies": "తెలిసిన అలర్జీలు",
        "medications": "ప్రస్తుత మందులు",
        "emergency_contact": "అత్యవసర సంప్రదింపు",
        "medical_history": "వైద్య చరిత్ర (ఐచ్ఛికం)",
        "symptom_desc": "మీ లక్షణాలను వివరించండి",
        "severity": "తీవ్రత స్థాయి",
        "duration": "వ్యవధి (గంటలు)",
        "pain_scale": "నొప్పి స్కేల్ (1-10)",
        "temperature": "ఉష్ణోగ్రత (°సెల్సియస్)",
        "submit": "లక్షణాన్ని సమర్పించండి",
        "triage": "AI ఆరోగ్య సిఫార్సు",
        "trend": "📈 ఆరోగ్య ధోరణులు",
        "export": "💾 డేటా ఎగుమతి",
        "logout": "🚪 సైన్ అవుట్",
        "profile": "👤 ఆరోగ్య ప్రొఫైల్",
        "dashboard": "🏠 డాష్‌బోర్డ్",
        "symptoms": "📝 లక్షణాలు నమోదు చేయండి",
       # "analytics": "📊 విశ్లేషణలు",
        "settings": "⚙ సెట్టింగ్‌లు",
        "help": "❓ సహాయం & మద్దతు",
        "navigation": "🧭 నావిగేషన్",
        "language": "🌐 భాష",
        "dashboard_welcome": "మీ వ్యక్తిగత ఆరోగ్య డాష్‌బోర్డ్‌కు స్వాగతం",
        "recent_symptoms": "ఇటీవలి ఆరోగ్య నమోదులు"
    },
    "हिंदी": {
        "title": "हेल्थवॉल्ट",
        "subtitle": "स्मार्ट लक्षण ट्रैकर और AI स्वास्थ्य सहायक",
        "welcome": "हेल्थवॉल्ट में आपका स्वागत है",
        "login": "साइन इन",
        "register": "साइन अप",
        "username": "उपयोगकर्ता नाम",
        "email": "ईमेल पता",
        "password": "पासवर्ड",
        "confirm_password": "पासवर्ड की पुष्टि करें",
        "age": "आयु",
        "gender": "लिंग",
        "height": "लंबाई (सेमी)",
        "weight": "वजन (किलो)",
        "blood_type": "रक्त समूह",
        "allergies": "ज्ञात एलर्जी",
        "medications": "वर्तमान दवाएं",
        "emergency_contact": "आपातकालीन संपर्क",
        "medical_history": "चिकित्सा इतिहास (वैकल्पिक)",
        "symptom_desc": "अपने लक्षणों का वर्णन करें",
        "severity": "गंभीरता स्तर",
        "duration": "अवधि (घंटे)",
        "pain_scale": "दर्द स्केल (1-10)",
        "temperature": "तापमान (°सेल्सियस)",
        "submit": "लक्षण सबमिट करें",
        "triage": "AI स्वास्थ्य सिफारिश",
        "trend": "📈 स्वास्थ्य रुझान",
        "export": "💾 डेटा निर्यात",
        "logout": "🚪 साइन आउट",
        "profile": "👤 स्वास्थ्य प्रोफाइल",
        "dashboard": "🏠 डैशबोर्ड",
        "symptoms": "📝 लक्षण लॉग करें",
        #"analytics": "📊 विश्लेषिकी",
        "settings": "⚙ सेटिंग्स",
        "help": "❓ सहायता एवं समर्थन",
        "navigation": "🧭 नेवीगेशन",
        "language": "🌐 भाषा",
        "dashboard_welcome": "आपके व्यक्तिगत स्वास्थ्य डैशबोर्ड में आपका स्वागत है",
        "recent_symptoms": "हाल की स्वास्थ्य प्रविष्टियां"
    }
}

# Session State initialization (enhanced)
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "show_success" not in st.session_state:
    st.session_state.show_success = False
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"
if "triage_result" not in st.session_state:
    st.session_state.triage_result = None
if "show_triage" not in st.session_state:
    st.session_state.show_triage = False
if "trend_view" not in st.session_state:
    st.session_state.trend_view = "overview"
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"
if "sidebar_navigation" not in st.session_state:
    st.session_state.sidebar_navigation = "dashboard"

# Enhanced NLP-based Triage System (keeping your existing function)
def analyze_symptoms_nlp(symptom_description, severity, duration_hours=None, pain_scale=None, temperature=None):
    """Enhanced NLP model with specific doctor consultation vs self-care recommendations"""
    symptoms = symptom_description.lower()
    blob = TextBlob(symptoms)
    sentiment = blob.sentiment.polarity
    
    emergency_keywords = [
        'chest pain', 'difficulty breathing', 'shortness of breath', 'severe headache',
        'unconscious', 'bleeding heavily', 'severe abdominal pain', 'heart attack',
        'stroke', 'seizure', 'cannot breathe', 'choking', 'allergic reaction',
        'anaphylaxis', 'overdose', 'suicide', 'severe burn', 'broken bone'
    ]
    
    doctor_keywords = [
        'fever', 'vomiting', 'diarrhea', 'rash', 'swelling', 'infection',
        'wound', 'cut', 'sprain', 'persistent cough', 'sore throat', 
        'ear pain', 'eye irritation', 'urinary pain', 'back pain',
        'joint pain', 'stomach pain', 'nausea', 'dizziness'
    ]
    
    selfcare_keywords = [
        'mild headache', 'fatigue', 'runny nose', 'sneezing', 'minor ache',
        'slight discomfort', 'dry skin', 'minor bruise', 'mild nausea',
        'congestion', 'stuffed nose', 'tired', 'sleepy'
    ]
    
    emergency_score = sum(1 for keyword in emergency_keywords if keyword in symptoms)
    doctor_score = sum(1 for keyword in doctor_keywords if keyword in symptoms)
    selfcare_score = sum(1 for keyword in selfcare_keywords if keyword in symptoms)
    
    severity_multiplier = {"Mild": 1, "Moderate": 2, "Severe": 3}
    base_score = emergency_score * 4 + doctor_score * 2 + selfcare_score * 1
    
    if severity:
        base_score *= severity_multiplier.get(severity, 1)
    
    if duration_hours and duration_hours > 48:
        base_score += 2
    elif duration_hours and duration_hours > 24:
        base_score += 1
    
    if pain_scale and pain_scale >= 8:
        base_score += 3
    elif pain_scale and pain_scale >= 6:
        base_score += 2
    elif pain_scale and pain_scale >= 4:
        base_score += 1
    
    if temperature and temperature >= 39.0:
        base_score += 2
    elif temperature and temperature >= 38.0:
        base_score += 1
    
    if base_score >= 8 or emergency_score > 0:
        triage = "🚨 EMERGENCY - SEEK IMMEDIATE MEDICAL ATTENTION\n\n"
        triage += "📞 Call emergency services or go to the nearest emergency room immediately.\n"
        triage += "⚠ This could be a serious medical emergency requiring urgent care."
        confidence = min(0.95, 0.7 + base_score * 0.03)
        
    elif base_score >= 4 or doctor_score > 0 or (pain_scale and pain_scale >= 6) or (temperature and temperature >= 38.0):
        triage = "👩‍⚕ CONSULT A DOCTOR\n\n"
        triage += "📅 Schedule an appointment with your healthcare provider within 24-48 hours.\n"
        triage += "🏥 Consider visiting urgent care if symptoms worsen or if it's after hours.\n"
        triage += "📝 Keep track of your symptoms and any changes."
        confidence = min(0.90, 0.6 + base_score * 0.05)
        
    elif base_score >= 1 or selfcare_score > 0:
        triage = "🏠 SELF-CARE RECOMMENDED\n\n"
        triage += "💊 Try home remedies and over-the-counter medications as appropriate.\n"
        triage += "📊 Monitor your symptoms for the next 24-48 hours.\n"
        triage += "⚠ See a doctor if symptoms worsen or persist beyond 3-5 days."
        confidence = min(0.85, 0.5 + base_score * 0.08)
        
    else:
        triage = "✅ GENERAL WELLNESS\n\n"
        triage += "🌟 Your symptoms appear mild and may resolve on their own.\n"
        triage += "💧 Stay hydrated, get adequate rest, and maintain good hygiene.\n"
        triage += "📞 Contact a healthcare provider if you have concerns or symptoms change."
        confidence = 0.65
    
    advice = []
    if 'fever' in symptoms:
        advice.append("🌡 Monitor temperature regularly, stay hydrated, and rest")
    if 'headache' in symptoms:
        advice.append("💊 Consider over-the-counter pain relief if appropriate")
    if 'cough' in symptoms or 'cold' in symptoms or 'sneezing' in symptoms:
        advice.append("🤧 Practice good hygiene, use tissues, and consider decongestants")
    if 'pain' in symptoms and pain_scale and pain_scale >= 7:
        advice.append("⚠ High pain levels - strong recommendation to see a doctor")
    if 'nausea' in symptoms or 'vomiting' in symptoms:
        advice.append("🥤 Stay hydrated with small sips of clear fluids")
    if 'rash' in symptoms or 'swelling' in symptoms:
        advice.append("👀 Monitor for spreading or worsening - may need medical evaluation")
    
    if duration_hours and duration_hours > 72:
        advice.append("⏰ Symptoms lasting over 3 days - consider medical consultation")
    
    if advice:
        triage += f"\n\n💡 Specific Recommendations:\n" + "\n".join(f"• {tip}" for tip in advice)
    
    if (pain_scale and pain_scale >= 7) or (temperature and temperature >= 38.5) or (duration_hours and duration_hours > 48):
        triage += f"\n\n⚠ Important: Multiple concerning factors detected. Consider medical evaluation even if recommendation is self-care."
    
    return triage, confidence

# Database functions (keeping all your existing functions)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_user(username, email, password, age, gender, height=None, weight=None, 
                 blood_type="", allergies="", medications="", emergency_contact="", medical_history=""):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            return "username_exists"
        
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            conn.close()
            return "email_exists"
        
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, age, gender, height, weight, 
                             blood_type, allergies, medications, emergency_contact, medical_history) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, password_hash, int(age), gender, height, weight,
              blood_type, allergies, medications, emergency_contact, medical_history))
        
        conn.commit()
        conn.close()
        return "success"
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return "error"

def login_user(username, password):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute("""
            SELECT id, username, email FROM users 
            WHERE username=? AND password_hash=?
        """, (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id=?", (user[0],))
            conn.commit()
        
        conn.close()
        return user if user else None
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def get_user_profile(user_id):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, email, age, gender, height, weight, blood_type, 
                   allergies, medications, emergency_contact, medical_history 
            FROM users WHERE id=?
        """, (user_id,))
        
        profile = cursor.fetchone()
        conn.close()
        return profile
        
    except Exception as e:
        print(f"Profile error: {str(e)}")
        return None

def save_symptom_entry(user_id, description, severity, duration_hours, pain_scale, temperature, triage_result, confidence, additional_notes=""):
    try:
        fix_symptom_table()
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO symptom_logs (user_id, date, description, severity, duration_hours, 
                                    pain_scale, temperature, triage_result, triage_confidence, additional_notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, str(date.today()), description, severity, duration_hours, 
              pain_scale, temperature, triage_result, confidence, additional_notes or ""))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Save symptom error: {str(e)}")
        return False

def get_user_stats(user_id):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM symptom_logs WHERE user_id=?", (user_id,))
        total_symptoms = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT description, severity, date, triage_result, duration_hours, pain_scale, temperature 
            FROM symptom_logs 
            WHERE user_id=? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (user_id,))
        recent_symptoms = cursor.fetchall()
        
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM symptom_logs 
            WHERE user_id=? 
            GROUP BY severity
        """, (user_id,))
        severity_data = dict(cursor.fetchall())
        
        conn.close()
        return total_symptoms, recent_symptoms, severity_data
        
    except Exception as e:
        print(f"Stats error: {str(e)}")
        return 0, [], {}

# Comprehensive Health Trends Visualization System (keeping your existing function)
def render_health_trends_dashboard(user_id):
    """
    Complete Health Trends Dashboard with multiple visualizations and analytics
    """
    try:
        conn = sqlite3.connect("database.db")
        
        # Get all symptom data for comprehensive analysis
        df = pd.read_sql_query("""
            SELECT date, severity, pain_scale, temperature, duration_hours, 
                   description, triage_result, triage_confidence, created_at
            FROM symptom_logs 
            WHERE user_id=?
            ORDER BY date
        """, conn, params=(user_id,))
        
        conn.close()
        
        if df.empty:
            st.info("📊 No health data available yet. Start logging symptoms to see comprehensive trends and insights!")
            
            # Show sample visualization
            st.markdown("### 📈 Sample Health Trends Preview")
            st.markdown("This is what your health trends will look like once you start logging symptoms:")
            
            # Create sample data for demonstration
            sample_dates = pd.date_range(start='2025-08-27', end='2025-09-10', freq='D')
            sample_data = {
                'date': sample_dates,
                'avg_severity': [1.2, 1.5, 1.4, 1.3, 1.6, 1.5, 1.7, 1.8, 1.6, 1.5, 1.7, 1.9, 2.0, 2.1, 2.0],
                'avg_pain': [3, 4, 3.5, 3, 4.2, 3.8, 4.1, 4.5, 4, 3.9, 4.2, 4.6, 4.8, 5, 4.9],
                'avg_temperature': [36.5, 36.6, 36.7, 36.5, 36.8, 36.9, 37.0, 37.1, 37.0, 37.0, 37.1, 37.2, 37.3, 37.4, 37.4]
            }
            sample_df = pd.DataFrame(sample_data)
            
            # Sample multi-line chart
            fig_sample = go.Figure()
            
            fig_sample.add_trace(go.Scatter(
                x=sample_df['date'], y=sample_df['avg_severity'],
                mode='lines+markers', name='Severity Level',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8)
            ))
            
            fig_sample.add_trace(go.Scatter(
                x=sample_df['date'], y=sample_df['avg_pain'],
                mode='lines+markers', name='Pain Scale',
                line=dict(color='#f59e0b', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            fig_sample.update_layout(
                title='Sample Health Trends Over Time',
                xaxis_title='Date',
                yaxis_title='Severity Level',
                yaxis2=dict(
                    title='Pain Scale',
                    overlaying='y',
                    side='right'
                ),
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_sample, use_container_width=True)
            return
        
        # Convert date columns and prepare data
        df['date'] = pd.to_datetime(df['date'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Map severity to numeric values
        severity_map = {'Mild': 1, 'Moderate': 2, 'Severe': 3}
        df['severity_numeric'] = df['severity'].map(severity_map)
        
        # 1. TRENDS OVERVIEW SECTION
        st.markdown("### 🎯 Health Trends Overview")
        
        # Time period selector
        col_period, col_view = st.columns([1, 1])
        
        with col_period:
            time_period = st.selectbox(
                "📅 Select Analysis Period:", 
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                key="trend_period"
            )
        
        with col_view:
            view_type = st.selectbox(
                "📊 View Type:",
                ["Overview", "Detailed Analysis", "Correlations", "Patterns"],
                key="trend_view_type"
            )
        
        # Filter data based on selected period
        if time_period == "Last 7 days":
            cutoff_date = datetime.now() - timedelta(days=7)
        elif time_period == "Last 30 days":
            cutoff_date = datetime.now() - timedelta(days=30)
        elif time_period == "Last 90 days":
            cutoff_date = datetime.now() - timedelta(days=90)
        else:
            cutoff_date = df['date'].min()
        
        filtered_df = df[df['date'] >= cutoff_date]
        
        if filtered_df.empty:
            st.warning(f"⚠ No data available for {time_period.lower()}.")
            return
        
        # Calculate daily aggregates for trends
        daily_stats = filtered_df.groupby('date').agg({
            'severity_numeric': 'mean',
            'pain_scale': 'mean', 
            'temperature': 'mean',
            'duration_hours': 'mean',
            'created_at': 'count'
        }).reset_index()
        
        daily_stats.columns = ['date', 'avg_severity', 'avg_pain', 'avg_temperature', 'avg_duration', 'symptom_count']
        
        # 2. KEY METRICS CARDS
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_severity = daily_stats['avg_severity'].mean()
            severity_color = "#ef4444" if avg_severity > 2.0 else "#f59e0b" if avg_severity > 1.5 else "#10b981"
            st.markdown(f"""
            <div class="trend-stat-card">
                <div class="trend-stat-value" style="color: {severity_color};">{avg_severity:.1f}</div>
                <div class="trend-stat-label">Avg Severity</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_pain = daily_stats['avg_pain'].mean()
            pain_color = "#ef4444" if avg_pain > 7 else "#f59e0b" if avg_pain > 4 else "#10b981"
            st.markdown(f"""
            <div class="trend-stat-card">
                <div class="trend-stat-value" style="color: {pain_color};">{avg_pain:.1f}</div>
                <div class="trend-stat-label">Avg Pain Level</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_temp = daily_stats['avg_temperature'].mean()
            temp_color = "#ef4444" if avg_temp > 37.5 else "#f59e0b" if avg_temp > 37.0 else "#10b981"
            st.markdown(f"""
            <div class="trend-stat-card">
                <div class="trend-stat-value" style="color: {temp_color};">{avg_temp:.1f}°C</div>
                <div class="trend-stat-label">Avg Temperature</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_entries = daily_stats['symptom_count'].sum()
            st.markdown(f"""
            <div class="trend-stat-card">
                <div class="trend-stat-value" style="color: #6366f1;">{total_entries}</div>
                <div class="trend-stat-label">Total Entries</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 3. MAIN TRENDS VISUALIZATIONS
        if view_type == "Overview":
            # Multi-metric trends chart
            fig_trends = make_subplots(
                rows=2, cols=2,
                subplot_titles=('📈 Severity Trend', '🩹 Pain Level Trend', 
                              '🌡 Temperature Trend', '📊 Daily Symptom Count'),
                vertical_spacing=0.15,
                horizontal_spacing=0.12
            )
            
            # Severity trend
            fig_trends.add_trace(
                go.Scatter(x=daily_stats['date'], y=daily_stats['avg_severity'],
                          mode='lines+markers', name='Severity',
                          line=dict(color='#10b981', width=3),
                          marker=dict(size=8)),
                row=1, col=1
            )
            
            # Pain scale trend
            fig_trends.add_trace(
                go.Scatter(x=daily_stats['date'], y=daily_stats['avg_pain'],
                          mode='lines+markers', name='Pain Scale',
                          line=dict(color='#f59e0b', width=3),
                          marker=dict(size=8)),
                row=1, col=2
            )
            
            # Temperature trend
            fig_trends.add_trace(
                go.Scatter(x=daily_stats['date'], y=daily_stats['avg_temperature'],
                          mode='lines+markers', name='Temperature',
                          line=dict(color='#ef4444', width=3),
                          marker=dict(size=8)),
                row=2, col=1
            )
            
            # Symptom frequency
            fig_trends.add_trace(
                go.Bar(x=daily_stats['date'], y=daily_stats['symptom_count'],
                       name='Symptom Count', marker_color='#8b5cf6'),
                row=2, col=2
            )
            
            fig_trends.update_layout(
                height=600,
                title_text=f"📈 Health Trends Analysis - {time_period}",
                showlegend=False,
                title_x=0.5
            )
            
            # Update y-axes
            fig_trends.update_yaxes(tickvals=[1, 2, 3], ticktext=['Mild', 'Moderate', 'Severe'], row=1, col=1)
            fig_trends.update_yaxes(range=[0, 10], row=1, col=2)
            fig_trends.update_yaxes(range=[36, 40], row=2, col=1)
            
            st.plotly_chart(fig_trends, use_container_width=True)
            
        elif view_type == "Detailed Analysis":
            # Combined trends in single chart
            fig_combined = go.Figure()
            
            # Normalize data for comparison (0-10 scale)
            normalized_severity = (daily_stats['avg_severity'] - 1) * 5  # Scale 1-3 to 0-10
            normalized_pain = daily_stats['avg_pain']  # Already 0-10
            normalized_temp = (daily_stats['avg_temperature'] - 36) * 2.5  # Scale 36-40 to 0-10
            
            fig_combined.add_trace(go.Scatter(
                x=daily_stats['date'], y=normalized_severity,
                mode='lines+markers', name='Severity (Normalized)',
                line=dict(color='#10b981', width=3)
            ))
            
            fig_combined.add_trace(go.Scatter(
                x=daily_stats['date'], y=normalized_pain,
                mode='lines+markers', name='Pain Scale',
                line=dict(color='#f59e0b', width=3)
            ))
            
            fig_combined.add_trace(go.Scatter(
                x=daily_stats['date'], y=normalized_temp,
                mode='lines+markers', name='Temperature (Normalized)',
                line=dict(color='#ef4444', width=3)
            ))
            
            fig_combined.update_layout(
                title="📊 Detailed Health Metrics Comparison (Normalized Scale 0-10)",
                xaxis_title="Date",
                yaxis_title="Normalized Value (0-10)",
                height=500
            )
            
            st.plotly_chart(fig_combined, use_container_width=True)
            
        elif view_type == "Correlations":
            # Correlation analysis
            if len(daily_stats) > 3:
                st.markdown("#### 🔗 Health Metrics Correlation Analysis")
                
                corr_data = daily_stats[['avg_severity', 'avg_pain', 'avg_temperature', 'symptom_count']].corr()
                
                fig_corr = px.imshow(
                    corr_data.values,
                    labels=dict(x="Metrics", y="Metrics", color="Correlation"),
                    x=['Severity', 'Pain', 'Temperature', 'Frequency'],
                    y=['Severity', 'Pain', 'Temperature', 'Frequency'],
                    color_continuous_scale="RdBu",
                    aspect="auto"
                )
                fig_corr.update_layout(height=400, title="Correlation Matrix of Health Metrics")
                
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Correlation insights
                severity_pain_corr = corr_data.loc['avg_severity', 'avg_pain']
                if abs(severity_pain_corr) > 0.7:
                    correlation_strength = "strong" if severity_pain_corr > 0 else "strong negative"
                    st.markdown(f"""
                    <div class="trend-insight">
                        🔍 <strong>Key Insight:</strong> There's a {correlation_strength} correlation ({severity_pain_corr:.2f}) between severity and pain levels in your symptoms.
                    </div>
                    """, unsafe_allow_html=True)
            
        elif view_type == "Patterns":
            # Weekly and monthly patterns
            if len(filtered_df) > 7:
                st.markdown("#### 📅 Weekly Pattern Analysis")
                
                # Add day of week analysis
                filtered_df['day_of_week'] = filtered_df['created_at'].dt.day_name()
                filtered_df['hour_of_day'] = filtered_df['created_at'].dt.hour
                
                day_analysis = filtered_df.groupby('day_of_week')['severity_numeric'].mean().reindex([
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
                ])
                
                fig_weekly = px.bar(
                    x=day_analysis.index, 
                    y=day_analysis.values,
                    title="📊 Average Symptom Severity by Day of Week",
                    color=day_analysis.values,
                    color_continuous_scale="RdYlGn_r"
                )
                fig_weekly.update_layout(height=400, showlegend=False)
                fig_weekly.update_yaxes(tickvals=[1, 2, 3], ticktext=['Mild', 'Moderate', 'Severe'])
                
                st.plotly_chart(fig_weekly, use_container_width=True)
                
                # Time of day analysis
                if len(filtered_df) > 10:
                    st.markdown("#### 🕐 Time of Day Pattern Analysis")
                    
                    hour_analysis = filtered_df.groupby('hour_of_day')['severity_numeric'].mean()
                    
                    fig_hourly = px.line(
                        x=hour_analysis.index,
                        y=hour_analysis.values,
                        title="⏰ Average Symptom Severity by Hour of Day",
                        markers=True
                    )
                    fig_hourly.update_layout(height=300)
                    fig_hourly.update_xaxis(title="Hour of Day (24h)")
                    fig_hourly.update_yaxis(title="Average Severity", tickvals=[1, 2, 3], ticktext=['Mild', 'Moderate', 'Severe'])
                    
                    st.plotly_chart(fig_hourly, use_container_width=True)
        
        # 4. HEALTH INSIGHTS AND RECOMMENDATIONS
        st.markdown("#### 🔍 AI Health Insights & Recommendations")
        
        if len(daily_stats) > 1:
            # Calculate trends
            severity_trend = "improving ✅" if daily_stats['avg_severity'].iloc[-1] < daily_stats['avg_severity'].iloc[0] else "needs attention ⚠"
            pain_trend = "decreasing ✅" if daily_stats['avg_pain'].iloc[-1] < daily_stats['avg_pain'].iloc[0] else "increasing ⚠"
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                trend_class = "trend-positive" if "✅" in severity_trend else "trend-warning"
                st.markdown(f"""
                <div class="trend-insight {trend_class}">
                    <strong>📈 Severity Trend:</strong> {severity_trend}<br>
                    <strong>📊 Current Average:</strong> {avg_severity:.1f}/3<br>
                    <strong>📋 Analysis Period:</strong> {time_period}
                </div>
                """, unsafe_allow_html=True)
            
            with col_insight2:
                trend_class = "trend-positive" if "✅" in pain_trend else "trend-warning"
                st.markdown(f"""
                <div class="trend-insight {trend_class}">
                    <strong>🩹 Pain Trend:</strong> {pain_trend}<br>
                    <strong>📊 Current Average:</strong> {avg_pain:.1f}/10<br>
                    <strong>🎯 Total Entries:</strong> {total_entries}
                </div>
                """, unsafe_allow_html=True)
            
            # Generate personalized recommendations
            recommendations = []
            
            if avg_severity > 2.0:
                recommendations.append("🩺 Consider scheduling a follow-up with your healthcare provider - your average severity is elevated.")
            
            if avg_pain > 6.0:
                recommendations.append("💊 Pain management consultation recommended - consistently high pain levels detected.")
            
            if avg_temp > 37.2:
                recommendations.append("🌡 Monitor temperature closely - elevated average temperature detected.")
            
            if "improving" in severity_trend and "decreasing" in pain_trend:
                recommendations.append("🎉 Great progress! Your symptoms are trending in a positive direction. Keep up your current treatment plan.")
            
            if not recommendations:
                recommendations.append("✨ Maintain current wellness routine - your health metrics appear stable.")
            
            if recommendations:
                st.markdown("#### 💡 Personalized Recommendations")
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"{i}. {rec}")
        
        # 5. EXPORT TRENDS DATA
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📊 Export Detailed Trends", key="export_detailed_trends"):
                trends_filename = f"detailed_health_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                # Prepare comprehensive export data
                export_data = daily_stats.copy()
                export_data['period'] = time_period
                export_data['export_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                export_data.to_csv(trends_filename, index=False)
                
                st.success("📈 Trends data exported successfully!")
                st.download_button(
                    label="📥 Download Trends CSV",
                    data=open(trends_filename, "rb").read(),
                    file_name=trends_filename,
                    mime="text/csv"
                )
        
        with col_export2:
            if st.button("📋 Generate Health Report", key="generate_health_report"):
                report_filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                # Generate comprehensive text report
                report_content = f"""
🏥 HEALTHVAULT - COMPREHENSIVE HEALTH REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: {time_period}

📊 KEY METRICS:
- Average Severity: {avg_severity:.1f}/3
- Average Pain Level: {avg_pain:.1f}/10  
- Average Temperature: {avg_temp:.1f}°C
- Total Symptom Entries: {total_entries}

📈 TRENDS:
- Severity Trend: {severity_trend}
- Pain Trend: {pain_trend}

💡 RECOMMENDATIONS:
{chr(10).join(f"• {rec.replace('*', '').replace('🩺', '').replace('💊', '').replace('🌡', '').replace('🎉', '').replace('✨', '')}" for rec in recommendations)}

📋 NOTES:
This report is generated based on your logged symptoms and is for informational purposes only. 
Always consult with healthcare professionals for medical advice.
                """
                
                with open(report_filename, 'w') as f:
                    f.write(report_content)
                
                st.success("📋 Health report generated!")
                st.download_button(
                    label="📥 Download Health Report",
                    data=report_content,
                    file_name=report_filename,
                    mime="text/plain"
                )
    
    except Exception as e:
        st.error(f"❌ Error generating health trends: {str(e)}")
        print(f"Trends error: {str(e)}")

def export_health_data(user_id):
    try:
        conn = sqlite3.connect("database.db")
        
        profile_df = pd.read_sql_query("""
            SELECT username, email, age, gender, height, weight, blood_type, 
                   allergies, medications, emergency_contact, medical_history 
            FROM users WHERE id=?
        """, conn, params=(user_id,))
        
        symptoms_df = pd.read_sql_query("""
            SELECT date, description, severity, duration_hours, pain_scale, 
                   temperature, triage_result, triage_confidence, additional_notes, created_at
            FROM symptom_logs 
            WHERE user_id=?
            ORDER BY created_at DESC
        """, conn, params=(user_id,))
        
        conn.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        profile_filename = f"health_profile_{timestamp}.csv"
        profile_df.to_csv(profile_filename, index=False)
        
        symptoms_filename = f"symptom_logs_{timestamp}.csv"
        symptoms_df.to_csv(symptoms_filename, index=False)
        
        return profile_filename, symptoms_filename
        
    except Exception as e:
        print(f"Export error: {str(e)}")
        return None, None

# Enhanced Language and Navigation Sidebar
def render_enhanced_sidebar():
    """Enhanced sidebar with navigation and language selection"""
    with st.sidebar:
        T = LANGS[st.session_state.selected_language]
        
        # App branding
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏥</div>
            <h2 style="margin: 0; color: white; font-weight: 800;">{T['title']}</h2>
            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9rem;">{T['subtitle']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile Section (only show if logged in)
        if st.session_state.user_id:
            profile = get_user_profile(st.session_state.user_id)
            if profile:
                st.markdown(f"""
                <div class="sidebar-profile">
                    <div class="profile-avatar">👤</div>
                    <div class="profile-name">{st.session_state.username}</div>
                    <div class="profile-role">Health Tracker User</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Language Selector
        st.markdown(f"""
        <div class="language-selector">
            <div class="language-title">{T['language']}</div>
        """, unsafe_allow_html=True)
        
        languages = list(LANGS.keys())
        for i, lang in enumerate(languages):
            if st.button(
                lang,
                key=f"lang_{i}",
                use_container_width=True,
                type="primary" if lang == st.session_state.selected_language else "secondary"
            ):
                st.session_state.selected_language = lang
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Navigation Menu (only show if logged in)
        if st.session_state.user_id:
            st.markdown(f"""
            <div class="sidebar-nav-header">
                {T['navigation']}
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation items
            nav_items = [
                ("dashboard", T['dashboard'], "🏠"),
                ("symptoms", T['symptoms'], "📝"),
                ("trends", T['trend'], "📈"),
                ("profile", T['profile'], "👤"),
                #("analytics", T['analytics'], "📊"),
                ("export", T['export'], "💾"),
                ("settings", T['settings'], "⚙"),
                ("help", T['help'], "❓")
            ]
            
            for nav_key, nav_label, nav_icon in nav_items:
                active_class = "active" if st.session_state.current_page == nav_key else ""
                if st.button(
                    f"{nav_icon} {nav_label}",
                    key=f"nav_{nav_key}",
                    use_container_width=True,
                    type="primary" if active_class else "secondary"
                ):
                    st.session_state.current_page = nav_key
                    st.rerun()
            
            # Logout button
            st.markdown("<br>" * 2, unsafe_allow_html=True)
            if st.button(T['logout'], key="logout_btn", use_container_width=True, type="primary"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    if key not in ['selected_language']:  # Keep language preference
                        del st.session_state[key]
                st.session_state.user_id = None
                st.session_state.current_page = "dashboard"
                st.rerun()

# Render the enhanced sidebar
render_enhanced_sidebar()

# Main Application Logic
T = LANGS[st.session_state.selected_language]  # Get current language translations

if not st.session_state.user_id:
    # Authentication Page
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="main-container">
            <div class="logo-container">
                <div class="logo">🏥</div>
                <div class="app-title">{T['title']}</div>
                <div class="app-subtitle">{T['subtitle']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Toggle buttons
        st.markdown(f"""
        <div class="toggle-container">
            <div class="toggle-btn {'active' if st.session_state.auth_mode == 'login' else ''}" onclick="document.getElementById('login_toggle').click()">
                {T['login']}
            </div>
            <div class="toggle-btn {'active' if st.session_state.auth_mode == 'register' else ''}" onclick="document.getElementById('register_toggle').click()">
                {T['register']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_login, col_register = st.columns(2)
        
        with col_login:
            if st.button("", key="login_toggle"):
                st.session_state.auth_mode = "login"
                st.session_state.show_success = False
                st.rerun()
                
        with col_register:
            if st.button("", key="register_toggle"):
                st.session_state.auth_mode = "register"
                st.session_state.show_success = False
                st.rerun()
        
        st.markdown("<hr style='margin: 1.5rem 0; border: none; height: 1px; background: linear-gradient(to right, transparent, #e5e7eb, transparent);'>", unsafe_allow_html=True)
        
        if st.session_state.show_success:
            st.markdown(f'<div class="success-message">{T["success_reg"]}</div>', unsafe_allow_html=True)
        
        # Login Form
        if st.session_state.auth_mode == "login":
            st.markdown(f"<h3 style='text-align: center; color: #1f2937; margin-bottom: 1.5rem; font-weight: 700;'>{T['welcome']} 👋</h3>", unsafe_allow_html=True)
            
            username = st.text_input("", placeholder=T["username"], key="login_username")
            password = st.text_input("", placeholder=T["password"], type="password", key="login_password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button(T["login"], key="login_btn", use_container_width=True):
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.session_state.email = user[2]
                        st.session_state.current_page = "dashboard"
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message">{T["no_user"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-message">{T["fill_required"]}</div>', unsafe_allow_html=True)
                    
        # Enhanced Register Form with Health Profile
        else:
            st.markdown(f"<h3 style='text-align: center; color: #1f2937; margin-bottom: 1.5rem; font-weight: 700;'>{T['register']} 🚀</h3>", unsafe_allow_html=True)
            
            # Basic Info
            col_user, col_email = st.columns(2)
            with col_user:
                username = st.text_input("", placeholder=T["username"], key="reg_username")
            with col_email:
                email = st.text_input("", placeholder=T["email"], key="reg_email")
            
            col_pass, col_confirm = st.columns(2)
            with col_pass:
                password = st.text_input("", placeholder=T["password"], type="password", key="reg_password")
            with col_confirm:
                confirm_password = st.text_input("", placeholder=T.get("confirm_password", "Confirm Password"), type="password", key="reg_confirm_password")
            
            col_age, col_gender = st.columns(2)
            with col_age:
                age = st.number_input(T["age"], min_value=1, max_value=120, value=25, key="reg_age")
            with col_gender:
                gender = st.selectbox(T["gender"], ["Male", "Female", "Other", "Prefer not to say"], key="reg_gender")
            
            # Health Profile (Optional)
            st.markdown(f"### 🏥 {T['medical_history']}")
            col_height, col_weight = st.columns(2)
            with col_height:
                height = st.number_input(T.get("height", "Height (cm)"), min_value=0.0, max_value=300.0, value=0.0, key="reg_height")
            with col_weight:
                weight = st.number_input(T.get("weight", "Weight (kg)"), min_value=0.0, max_value=500.0, value=0.0, key="reg_weight")
            
            blood_types = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            blood_type = st.selectbox(T.get("blood_type", "Blood Type"), blood_types, key="reg_blood_type")
            
            allergies = st.text_input("", placeholder=T.get("allergies", "Known Allergies"), key="reg_allergies")
            medications = st.text_input("", placeholder=T.get("medications", "Current Medications"), key="reg_medications")
            emergency_contact = st.text_input("", placeholder=T.get("emergency_contact", "Emergency Contact"), key="reg_emergency")
            medical_history = st.text_area("", placeholder=T["medical_history"], key="reg_history", height=80)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button(T["register"], key="register_btn", use_container_width=True):
                if not username or not username.strip():
                    st.markdown('<div class="error-message">Please enter a username</div>', unsafe_allow_html=True)
                elif not email or not email.strip():
                    st.markdown('<div class="error-message">Please enter an email address</div>', unsafe_allow_html=True)
                elif not password:
                    st.markdown('<div class="error-message">Please enter a password</div>', unsafe_allow_html=True)
                elif not confirm_password:
                    st.markdown('<div class="error-message">Please confirm your password</div>', unsafe_allow_html=True)
                elif age <= 0:
                    st.markdown('<div class="error-message">Please enter a valid age</div>', unsafe_allow_html=True)
                elif not validate_email(email.strip()):
                    st.markdown(f'<div class="error-message">{T["invalid_email"]}</div>', unsafe_allow_html=True)
                elif password != confirm_password:
                    st.markdown(f'<div class="error-message">{T["password_mismatch"]}</div>', unsafe_allow_html=True)
                elif len(password) < 6:
                    st.markdown('<div class="error-message">Password must be at least 6 characters long</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Creating your account..."):
                        result = register_user(
                            username.strip(), email.strip(), password, int(age), gender,
                            height if height > 0 else None, weight if weight > 0 else None,
                            blood_type, allergies.strip(), medications.strip(), 
                            emergency_contact.strip(), medical_history.strip()
                        )
                    
                    if result == "success":
                        st.session_state.show_success = True
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    elif result == "username_exists":
                        st.markdown(f'<div class="error-message">{T["user_exists"]}</div>', unsafe_allow_html=True)
                    elif result == "email_exists":
                        st.markdown(f'<div class="error-message">{T["email_exists"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message">Registration failed. Please try again.</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Enhanced Dashboard with Page Navigation
    current_page = st.session_state.current_page
    
    if current_page == "dashboard":
        # Dashboard content
        st.markdown(f"""
        <div class="dashboard-header">
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800;">🏥 {T['title']}</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 500;">{T['dashboard_welcome']}</p>
            <p style="margin: 0.3rem 0 0 0; font-size: 1rem; opacity: 0.8;">Hello, <strong>{st.session_state.username}</strong>! 👋</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get user stats
        total_symptoms, recent_symptoms, severity_data = get_user_stats(st.session_state.user_id)
        
        # Enhanced metrics row (only show if there's data)
        if total_symptoms > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_symptoms}</div>
                    <div class="metric-label">Total Entries</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                mild_count = severity_data.get("Mild", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{mild_count}</div>
                    <div class="metric-label">Mild</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                moderate_count = severity_data.get("Moderate", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{moderate_count}</div>
                    <div class="metric-label">Moderate</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                severe_count = severity_data.get("Severe", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{severe_count}</div>
                    <div class="metric-label">Severe</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Recent symptoms overview
        if recent_symptoms:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown(f"### 📋 {T['recent_symptoms']}")
            
            for symptom in recent_symptoms:
                severity_color = {"Mild": "#10b981", "Moderate": "#f59e0b", "Severe": "#ef4444"}.get(symptom[1], "#6b7280")
                st.markdown(f"""
                <div style="padding: 1rem; margin: 0.5rem 0; background: #f9fafb; border-radius: 8px; border-left: 4px solid {severity_color};">
                    <strong>{symptom[0][:60]}{'...' if len(symptom[0]) > 60 else ''}</strong><br>
                    <small style="color: #6b7280;">
                        {symptom[2]} • Severity: {symptom[1]}
                        {f" • Pain: {symptom[5]}/10" if symptom[5] else ""}
                        {f" • Temp: {symptom[6]:.1f}°C" if symptom[6] else ""}
                    </small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif current_page == "symptoms":
        # Symptom logging page
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown(f"### 📝 {T['symptom_desc']}")
        
        symptom_desc = st.text_area("", placeholder="Describe your symptoms in detail (e.g., headache started this morning, sharp pain behind eyes, sensitivity to light)", height=120)
        
        col_sev, col_dur = st.columns(2)
        with col_sev:
            severity = st.selectbox(T["severity"], ["Mild", "Moderate", "Severe"])
        with col_dur:
            duration_hours = st.number_input(T.get("duration", "Duration (hours)"), min_value=0, max_value=720, value=1)
        
        col_pain, col_temp = st.columns(2)
        with col_pain:
            pain_scale = st.slider(T.get("pain_scale", "Pain Scale (1-10)"), 1, 10, 3)
        with col_temp:
            temperature = st.number_input(T.get("temperature", "Temperature (°C)"), min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        
        additional_notes = st.text_area("Additional Notes (Optional)", placeholder="Any other relevant information...", height=60)
        
        # Display persistent triage result if exists
        if st.session_state.show_triage and st.session_state.triage_result:
            st.markdown(f'<div class="triage-result">{st.session_state.triage_result}</div>', unsafe_allow_html=True)
        
        if st.button(T["submit"], key="submit_symptom", use_container_width=True):
            if symptom_desc.strip():
                with st.spinner("🤖 Analyzing symptoms..."):
                    triage_result, confidence = analyze_symptoms_nlp(
                        symptom_desc, severity, duration_hours, pain_scale, temperature
                    )
                
                # Save to database
                if save_symptom_entry(
                    st.session_state.user_id, symptom_desc, severity, 
                    duration_hours, pain_scale, temperature, 
                    triage_result, confidence, additional_notes
                ):
                    st.session_state.triage_result = triage_result
                    st.session_state.show_triage = True
                    st.success("✅ Symptom logged successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save symptom. Please try again.")
            else:
                st.error("Please describe your symptoms before submitting.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif current_page == "trends":
        # Health trends page
        render_health_trends_dashboard(st.session_state.user_id)
    
    elif current_page == "profile":
        # Health profile page
        profile = get_user_profile(st.session_state.user_id)
        if profile:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown(f"### 👤 {T['profile']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                st.markdown(f"*Username:* {profile[0]}")
                st.markdown(f"*Email:* {profile[1]}")
                st.markdown(f"*Age:* {profile[2]} years")
                st.markdown(f"*Gender:* {profile[3]}")
            
            with col2:
                st.markdown("#### Health Information")
                if profile[4]:  # height
                    st.markdown(f"*Height:* {profile[4]} cm")
                if profile[5]:  # weight
                    st.markdown(f"*Weight:* {profile[5]} kg")
                if profile[6]:  # blood_type
                    st.markdown(f"*Blood Type:* {profile[6]}")
                if profile[7]:  # allergies
                    st.markdown(f"*Allergies:* {profile[7]}")
            
            if profile[8]:  # medications
                st.markdown("#### Current Medications")
                st.markdown(profile[8])
            
            if profile[9]:  # emergency_contact
                st.markdown("#### Emergency Contact")
                st.markdown(profile[9])
            
            if profile[10]:  # medical_history
                st.markdown("#### Medical History")
                st.markdown(profile[10])
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    #elif current_page == "analytics":
        # Analytics page
        #st.markdown(f"### 📊 {T['analytics']}")
        #st.info("🔬 Advanced analytics and AI insights coming soon!")
        
        # Show basic analytics for now
        #total_symptoms, recent_symptoms, severity_data = get_user_stats(st.session_state.user_id)
        
        #if total_symptoms > 0:
            #st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            
            # Severity distribution chart
            #if severity_data:
               # fig = px.pie(
                    #values=list(severity_data.values()),
                    #names=list(severity_data.keys()),
                    #title="Symptom Severity Distribution"
               # )
            #    st.plotly_chart(fig, use_container_width=True)
            
            #st.markdown('</div>', unsafe_allow_html=True)
    
    elif current_page == "export":
        # Export data page
        st.markdown(f"### 💾 {T['export']}")
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Health Profile", use_container_width=True):
                profile_file, symptoms_file = export_health_data(st.session_state.user_id)
                if profile_file and symptoms_file:
                    st.success("✅ Data exported successfully!")
                    
                    with open(profile_file, 'rb') as f:
                        st.download_button(
                            label="📥 Download Health Profile",
                            data=f.read(),
                            file_name=profile_file,
                            mime="text/csv"
                        )
                else:
                    st.error("❌ Export failed. Please try again.")
        
        with col2:
            if st.button("📋 Generate Health Summary", use_container_width=True):
                total_symptoms, recent_symptoms, severity_data = get_user_stats(st.session_state.user_id)
                
                summary = f"""
                🏥 HEALTHVAULT - HEALTH SUMMARY
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                📊 OVERVIEW:
                - Total Symptom Entries: {total_symptoms}
                - Mild Symptoms: {severity_data.get('Mild', 0)}
                - Moderate Symptoms: {severity_data.get('Moderate', 0)}
                - Severe Symptoms: {severity_data.get('Severe', 0)}
                
                📋 RECENT SYMPTOMS:
                """
                
                for symptom in recent_symptoms[:3]:
                    summary += f"- {symptom[0][:50]} ({symptom[1]}) - {symptom[2]}\n"
                
                st.text_area("Health Summary", summary, height=300)
                
                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name=f"health_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif current_page == "settings":
        # Settings page
        st.markdown(f"### ⚙ {T['settings']}")
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        st.markdown("#### Language Settings")
        st.info(f"Current Language: *{st.session_state.selected_language}*")
        st.markdown("Use the language selector in the sidebar to change languages.")
        
        st.markdown("#### Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Dashboard", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑 Clear Triage Result", use_container_width=True):
                st.session_state.triage_result = None
                st.session_state.show_triage = False
                st.success("✅ Triage result cleared!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif current_page == "help":
        # Help and support page
        st.markdown(f"### ❓ {T['help']}")
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        st.markdown("#### How to Use HealthVault")
        
        help_sections = [
            ("🏠 Dashboard", "View your health overview, recent symptoms, and key metrics."),
            ("📝 Log Symptoms", "Record new symptoms with detailed information for AI analysis."),
            ("📈 Health Trends", "Analyze your health patterns over time with comprehensive charts."),
            ("👤 Health Profile", "View and manage your personal health information."),
            ("📊 Analytics", "Get insights and trends from your health data."),
            ("💾 Export Data", "Download your health data and generate reports."),
            ("⚙ Settings", "Manage app preferences and data settings."),
            ("🌐 Languages", "Switch between English, Telugu, and Hindi.")
        ]
        
        for title, description in help_sections:
            st.markdown(f"{title}")
            st.markdown(description)
            st.markdown("")
        
        st.markdown("#### AI Health Triage")
        st.markdown("""
        Our AI system analyzes your symptoms and provides recommendations:
        - 🚨 *Emergency*: Seek immediate medical attention
        - 👩‍⚕ *Doctor Consultation*: Schedule an appointment within 24-48 hours
        - 🏠 *Self-Care*: Try home remedies and monitor symptoms
        - ✅ *General Wellness*: Symptoms appear mild
        """)
        
        st.markdown("#### Important Notes")
        st.warning("⚠ *Medical Disclaimer*: This app is for informational purposes only. Always consult healthcare professionals for medical advice.")
        
        st.markdown('</div>', unsafe_allow_html=True)