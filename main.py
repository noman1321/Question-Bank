import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import time
import re
from question_generator import QuestionGenerator, get_openai_api_key
from image_processor import ImageProcessor

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image
import io
import base64

from dotenv import load_dotenv
import os



# Example: read env variables
api_key = os.getenv("OPENAI_API_KEY")
print("API Key:", api_key)

# Enhanced CSS for Glass Black theme with animations
def load_css():
    st.markdown("""
    <style>
    /* Import iOS system fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Updated to grey-based iOS glassmorphism color palette */
    :root {
        --ios-background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        --ios-surface: rgba(255, 255, 255, 0.25);
        --ios-surface-secondary: rgba(255, 255, 255, 0.15);
        --ios-border: rgba(255, 255, 255, 0.3);
        --ios-separator: rgba(255, 255, 255, 0.2);
        --ios-primary: #6c7b7f;
        --ios-secondary: #8e9aaf;
        --ios-success: #34C759;
        --ios-warning: #FF9500;
        --ios-error: #FF3B30;
        --ios-text-primary: #2c3e50;
        --ios-text-secondary: #5a6c7d;
        --ios-text-tertiary: #7f8c8d;
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --glass-border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Added keyframe animations for glassmorphism effects */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glassShimmer {
        0% {
            background-position: -200px 0;
        }
        100% {
            background-position: calc(200px + 100%) 0;
        }
    }
    
    @keyframes floatAnimation {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: var(--glass-shadow);
        }
        50% {
            box-shadow: var(--glass-shadow), 0 0 20px rgba(108, 123, 127, 0.3);
        }
    }
    
    /* Updated background with glassmorphism gradient */
    .stApp {
        background: var(--ios-background);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--ios-text-primary);
        min-height: 100vh;
        position: relative;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 226, 0.15) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Updated card styling with glassmorphism effects */
    .ios-card {
        background: var(--ios-surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: var(--glass-shadow);
        border: var(--glass-border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .ios-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        background: rgba(255, 255, 255, 0.35);
    }
    
    .ios-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }
    
    .ios-card:hover::before {
        left: 100%;
    }
    
    /* Enhanced header with glassmorphism and animations */
    .app-header {
        text-align: center;
        padding: 48px 0;
        background: var(--ios-surface);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border-radius: 24px;
        margin-bottom: 32px;
        border: var(--glass-border);
        box-shadow: var(--glass-shadow);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out, pulseGlow 4s ease-in-out infinite;
    }
    
    .app-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -200px;
        width: 200px;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.4),
            transparent
        );
        animation: glassShimmer 3s ease-in-out infinite;
    }
    
    /* Enhanced title styling with animations */
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        color: var(--ios-text-primary);
        margin-bottom: 16px;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        animation: fadeInUp 1s ease-out 0.2s both;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: var(--ios-text-secondary);
        font-weight: 400;
        margin-bottom: 0;
        position: relative;
        z-index: 1;
        animation: fadeInUp 1s ease-out 0.4s both;
    }
    
    /* Enhanced sidebar with glassmorphism */
    .css-1d391kg {
        background: var(--ios-surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: var(--glass-border);
    }
    
    /* Enhanced button styling with glassmorphism */
    .stButton > button {
        background: var(--ios-primary) !important;
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        font-size: 16px;
        box-shadow: 0 4px 15px 0 rgba(108, 123, 127, 0.4);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        );
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        background: #5a6b6f !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px 0 rgba(108, 123, 127, 0.6);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 4px 15px 0 rgba(108, 123, 127, 0.4);
    }
    
    /* Primary button with special effects */
    .primary-button {
        background: linear-gradient(135deg, #007AFF 0%, #5856D6 50%, #007AFF 100%) !important;
        box-shadow: 0 4px 20px rgba(0, 122, 255, 0.4) !important;
        animation: pulseGlow 3s ease-in-out infinite;
    }
    
    .primary-button:hover {
        box-shadow: 0 12px 40px rgba(0, 122, 255, 0.6) !important;
        animation: pulse 0.6s ease-in-out;
    }
    
    /* Updated input styling with glassmorphism */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--ios-surface) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: var(--glass-border) !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 16px !important;
        color: var(--ios-text-primary) !important;
        box-shadow: inset 0 2px 4px 0 rgba(31, 38, 135, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--ios-primary) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(108, 123, 127, 0.2), inset 0 2px 4px 0 rgba(31, 38, 135, 0.2) !important;
        background: rgba(255, 255, 255, 0.35) !important;
    }
    
    /* Enhanced select box styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid var(--glass-border) !important;
        border-radius: 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--ios-primary) !important;
        box-shadow: 0 0 15px rgba(142, 142, 147, 0.2) !important;
    }
    
    /* Enhanced file uploader with glassmorphism */
    .stFileUploader > div {
        background: var(--ios-surface-secondary) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 2px dashed var(--ios-separator) !important;
        border-radius: 16px !important;
        padding: 32px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--ios-primary) !important;
        background: var(--ios-surface) !important;
        transform: translateY(-2px);
        box-shadow: var(--glass-shadow);
    }
    
    .stFileUploader > div::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(transparent, rgba(142, 142, 147, 0.1), transparent);
        animation: spin 4s linear infinite;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Enhanced progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--ios-primary), var(--ios-secondary)) !important;
        background-size: 200% 100% !important;
        animation: glassShimmer 2s ease-in-out infinite !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(142, 142, 147, 0.3) !important;
    }
    
    /* Enhanced metrics styling with glassmorphism and animations */
    .metric-card {
        background: var(--ios-surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin: 12px 0;
        box-shadow: var(--glass-shadow);
        border: var(--glass-border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out, floatAnimation 6s ease-in-out infinite;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        background: rgba(255, 255, 255, 0.35);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-title {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 10px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Enhanced status indicators */
    .status-success {
        background: linear-gradient(135deg, var(--ios-success) 0%, #30D158 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 15px;
        margin: 15px 0;
        font-weight: 600;
        border-left: 5px solid var(--ios-success);
        box-shadow: 
            0 4px 20px rgba(52, 199, 89, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        animation: fadeInUp 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .status-success:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 25px rgba(52, 199, 89, 0.4);
    }
    
    .status-error {
        background: linear-gradient(135deg, var(--ios-error) 0%, #FF453A 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 15px;
        margin: 15px 0;
        font-weight: 600;
        border-left: 5px solid var(--ios-error);
        box-shadow: 
            0 4px 20px rgba(255, 59, 48, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        animation: fadeInUp 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .status-error:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 25px rgba(255, 59, 48, 0.4);
    }
    
    .status-warning {
        background: linear-gradient(135deg, var(--ios-warning) 0%, #FF9F0A 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 15px;
        margin: 15px 0;
        font-weight: 600;
        border-left: 5px solid var(--ios-warning);
        box-shadow: 
            0 4px 20px rgba(255, 149, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        animation: fadeInUp 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .status-warning:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 25px rgba(255, 149, 0, 0.4);
    }
    
    /* Enhanced tab styling with glassmorphism */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--ios-surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 4px;
        border: var(--glass-border);
        box-shadow: var(--glass-shadow);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--ios-text-secondary);
        border-radius: 12px;
        margin: 0 4px;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--ios-surface-secondary);
        color: var(--ios-text-primary);
        transform: translateY(-1px);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--ios-primary) !important;
        color: white !important;
        box-shadow: 0 4px 15px 0 rgba(108, 123, 127, 0.4);
        transform: translateY(-1px);
    }
    
    /* Enhanced question card with glassmorphism */
    .question-card {
        background: var(--ios-surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: var(--glass-shadow);
        border: var(--glass-border);
        border-left: 4px solid var(--ios-primary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .question-card:hover {
        background: rgba(255, 255, 255, 0.35);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    .question-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }
    
    .question-card:hover::before {
        left: 100%;
    }
    
    /* Enhanced glass containers */
    .glass-container {
        background: var(--ios-surface);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        border: var(--glass-border);
        padding: 24px;
        margin: 20px 0;
        box-shadow: var(--glass-shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .glass-container:hover {
        background: rgba(255, 255, 255, 0.35);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    .glass-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }
    
    .glass-container:hover::before {
        left: 100%;
    }
    
    /* Enhanced feature highlight with glassmorphism */
    .feature-highlight {
        background: var(--ios-surface-secondary);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: var(--glass-border);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .feature-highlight:hover {
        background: var(--ios-surface);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    .feature-highlight::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }
    
    .feature-highlight:hover::before {
        left: 100%;
    }
    
    /* Loading animations */
    .loading {
        animation: pulse 2s infinite;
    }
    
    .loading-shimmer {
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(255, 255, 255, 0.3) 50%,
            rgba(255, 255, 255, 0.1) 100%
        );
        background-size: 200% 100%;
        animation: glassShimmer 2s ease-in-out infinite;
    }
    
    /* Enhanced image styling with glassmorphism frame */
    .stImage > img {
        border-radius: 16px;
        box-shadow: var(--glass-shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stImage > img:hover {
        transform: scale(1.02);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Enhanced multiselect and radio with glassmorphism */
    .stMultiSelect > div > div,
    .stRadio > div {
        background: var(--ios-surface) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-radius: 12px !important;
        border: var(--glass-border) !important;
        padding: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stMultiSelect > div > div:hover,
    .stRadio > div:hover {
        border-color: var(--ios-primary) !important;
        background: rgba(255, 255, 255, 0.35) !important;
        transform: translateY(-1px);
    }
    
    /* Enhanced expander with glassmorphism */
    .streamlit-expanderHeader {
        background: var(--ios-surface) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-radius: 12px !important;
        border: var(--glass-border) !important;
        padding: 12px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.35) !important;
        border-color: var(--ios-primary) !important;
        transform: translateY(-1px);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Text color fixes */
    .stMarkdown, .stText, p, span, div {
        color: var(--ios-text-primary) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--ios-text-primary) !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Special glow effect for important elements */
    .glow-effect {
        animation: pulseGlow 2s ease-in-out infinite alternate;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .app-title {
            font-size: 2.5rem;
        }
        
        .app-subtitle {
            font-size: 1rem;
        }
        
        .ios-card, .glass-container {
            padding: 20px;
            margin: 15px 0;
        }
        
        .metric-card {
            padding: 15px;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }
    
    /* Focus visible for accessibility */
    *:focus-visible {
        outline: 2px solid var(--ios-primary);
        outline-offset: 2px;
        border-radius: 8px;
        box-shadow: 0 0 0 4px rgba(108, 123, 127, 0.2);
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    </style>
    """, unsafe_allow_html=True)

# Enhanced custom components with animations
def create_metric_card(title, value, icon="📊"):
    st.markdown(f"""
    <div class="metric-card glow-effect">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def create_status_message(message, status_type="success"):
    st.markdown(f"""
    <div class="status-{status_type}">
        {message}
    </div>
    """, unsafe_allow_html=True)

def create_feature_highlight(title, description, icon="✨"):
    st.markdown(f"""
    <div class="feature-highlight">
        <h3>{icon} {title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def create_animated_progress(text, progress_value):
    """Create animated progress indicator"""
    st.markdown(f"""
    <div class="glass-container">
        <h4 style="text-align: center; margin-bottom: 20px;">{text}</h4>
        <div style="background: rgba(255,255,255,0.2); border-radius: 20px; padding: 10px;">
            <div style="
                width: {progress_value}%; 
                height: 10px; 
                background: linear-gradient(90deg, var(--ios-primary), var(--ios-secondary));
                background-size: 200% 100%;
                animation: glassShimmer 2s ease-in-out infinite;
                border-radius: 15px;
                transition: width 0.8s ease;
                box-shadow: 0 0 20px rgba(142, 142, 147, 0.5);
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)



# Initialize session state
if 'generated_question_sets' not in st.session_state:
    st.session_state.generated_question_sets = []
if 'current_set' not in st.session_state:
    st.session_state.current_set = 0
if 'extracted_images' not in st.session_state:
    st.session_state.extracted_images = []

def generate_pdf_with_images(question_set_data, image_analyses, title="Question Set"):
    """Generate PDF with embedded images"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.black
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leftIndent=0
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.darkblue
    )
    
    # Add title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    # Process questions text
    questions_text = question_set_data['questions']
    
    # Split by sections
    sections = re.split(r'(Section [AB]:.*?)\n', questions_text)
    
    current_section = ""
    for section in sections:
        if not section.strip():
            continue
            
        # Check if this is a section header
        if section.startswith('Section'):
            current_section = section
            elements.append(Paragraph(f"<b>{section}</b>", header_style))
            elements.append(Spacer(1, 12))
            continue
            
        # Process questions in this section
        lines = section.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line == "---":
                continue
                
            # Check for image references
            image_pattern = r'\[IMAGE:img_(\d+)\]'
            image_matches = re.findall(image_pattern, line)
            
            if image_matches:
                # Add images first
                for match in image_matches:
                    img_num = int(match) - 1
                    if 0 <= img_num < len(image_analyses):
                        try:
                            # Convert PIL image to ReportLab Image
                            img_data = image_analyses[img_num]['image']
                            img_buffer = io.BytesIO()
                            
                            # Resize image if too large
                            max_width, max_height = 400, 300
                            if img_data.width > max_width or img_data.height > max_height:
                                img_data.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                            
                            img_data.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            # Use BytesIO instead of temporary files
                            img_buffer.seek(0)
                            
                            # Create ReportLab Image directly from BytesIO
                            rl_image = RLImage(img_buffer, width=img_data.width, height=img_data.height)
                            elements.append(rl_image)
                            elements.append(Spacer(1, 12))
                            
                            # Add image caption
                            caption = f"Image {img_num + 1}: {image_analyses[img_num]['source']}"
                            elements.append(Paragraph(f"<i>{caption}</i>", styles['Normal']))
                            elements.append(Spacer(1, 12))
                        except Exception as e:
                            st.warning(f"Could not embed image {img_num + 1}: {str(e)}")
                
                # Remove image references from text and add question
                clean_line = re.sub(image_pattern, '', line).strip()
                if clean_line:
                    elements.append(Paragraph(clean_line, question_style))
                    elements.append(Spacer(1, 8))
            else:
                # Regular text line
                if line:
                    # Check if it's a question number or important text
                    if re.match(r'^[AB]?\d+\.', line) or 'Correct Answer:' in line:
                        elements.append(Paragraph(f"<b>{line}</b>", question_style))
                    else:
                        elements.append(Paragraph(line, question_style))
                    elements.append(Spacer(1, 6))
    
    # Build PDF
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error building PDF: {str(e)}")
        return None

def create_enhanced_download_buttons(current_set_data, image_analyses, difficulty):
    """Create enhanced download buttons with professional styling"""
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.markdown("### 📥 Download Options")
    
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        st.markdown("**📄 Text Format**")
        # Text download
        st.download_button(
            f"📄 Set {current_set_data['set_number']} (TXT)",
            data=current_set_data['questions'],
            file_name=f"question_set_{current_set_data['set_number']}_{difficulty}_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # PDF download with images
        if image_analyses:
            try:
                with st.spinner("🔄 Generating PDF..."):
                    pdf_data = generate_pdf_with_images(
                        current_set_data, 
                        image_analyses, 
                        f"Question Set {current_set_data['set_number']} - {difficulty}"
                    )
                
                if pdf_data:
                    st.download_button(
                        f"📊 Set {current_set_data['set_number']} (PDF)",
                        data=pdf_data,
                        file_name=f"question_set_{current_set_data['set_number']}_with_images_{difficulty}_{int(time.time())}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("❌ PDF generation failed")
            except Exception as e:
                st.error(f"❌ PDF Error: {str(e)}")
    
    with col_d2:
        st.markdown("**📦 Complete Collection**")
        # All sets text download
        all_sets_combined = ""
        for i, set_data in enumerate(st.session_state.generated_question_sets):
            all_sets_combined += f"""
{'='*60}
QUESTION SET {set_data['set_number']}
{'='*60}
Generated: {set_data['timestamp']}

{set_data['questions']}

"""
        
        # Include image information in the header
        image_info = ""
        if st.session_state.extracted_images:
            image_info = f"""
Images Analyzed: {len(st.session_state.extracted_images)}
Image Sources: {', '.join(set(img['source'] for img in st.session_state.extracted_images))}
"""
        
        formatted_all = f"""
COMPLETE QUESTION BANK - ALL SETS
=================================
Difficulty: {difficulty if 'difficulty' in locals() else 'Medium'}
Total Sets: {len(st.session_state.generated_question_sets)}
Total Questions: Approximately {len(st.session_state.generated_question_sets) * 25}
{image_info}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

{all_sets_combined}
"""
        
        st.download_button(
            "📦 All Sets (TXT)",
            data=formatted_all,
            file_name=f"all_question_sets_complete_{difficulty}_{int(time.time())}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        # All sets PDF download
        if image_analyses:
            if st.button("📊 Generate Complete PDF", use_container_width=True):
                try:
                    with st.spinner("🔄 Creating comprehensive PDF..."):
                        # Generate combined PDF for all sets
                        combined_pdf_data = io.BytesIO()
                        doc = SimpleDocTemplate(combined_pdf_data, pagesize=A4)
                        elements = []
                        styles = getSampleStyleSheet()
                        
                        # Add title page
                        title_style = ParagraphStyle(
                            'MainTitle', parent=styles['Title'],
                            fontSize=20, spaceAfter=30, alignment=1
                        )
                        elements.append(Paragraph("Complete Question Bank - All Sets", title_style))
                        elements.append(Spacer(1, 50))
                        
                        # Process each set
                        for set_data in st.session_state.generated_question_sets:
                            set_title = f"Question Set {set_data['set_number']} - {difficulty}"
                            elements.append(Paragraph(set_title, styles['Heading1']))
                            elements.append(Spacer(1, 20))
                            
                            # Add set content (simplified)
                            elements.append(Paragraph(set_data['questions'][:1000] + "...", styles['Normal']))
                            elements.append(Spacer(1, 30))
                        
                        doc.build(elements)
                        combined_pdf_data.seek(0)
                        
                        st.download_button(
                            "📊 Download Complete PDF",
                            data=combined_pdf_data.getvalue(),
                            file_name=f"all_question_sets_complete_{difficulty}_{int(time.time())}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    with col_d3:
        st.markdown("**🔄 Navigation**")
        # Navigation buttons
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("⬅️ Previous", disabled=st.session_state.current_set == 0, use_container_width=True):
                st.session_state.current_set = max(0, st.session_state.current_set - 1)
                st.rerun()
        with col_nav2:
            if st.button("Next ➡️", disabled=st.session_state.current_set >= len(st.session_state.generated_question_sets) - 1, use_container_width=True):
                st.session_state.current_set = min(len(st.session_state.generated_question_sets) - 1, st.session_state.current_set + 1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_question_set_with_images(set_data, image_analyses):
    """Display questions with embedded images in styled cards"""
    questions_text = set_data['questions']
    
    # Split questions for processing
    question_blocks = questions_text.split('\n\nQ')
    if question_blocks:
        # Handle first question
        if question_blocks[0].startswith('Q'):
            first_q = question_blocks[0]
        else:
            first_q = 'Q' + question_blocks[0] if question_blocks[0] else ''
        
        # Handle remaining questions
        other_qs = ['Q' + block for block in question_blocks[1:] if block.strip()]
        
        all_questions = [first_q] + other_qs if first_q.strip() else other_qs
    else:
        all_questions = [questions_text]
    
    for i, question in enumerate(all_questions):
        if not question.strip():
            continue
        
        # Create question card
        with st.container():
            st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
            st.markdown(f"#### 💭 Question {i+1}")
            
            # Check for image references in this question
            image_pattern = r'\[IMAGE:img_(\d+)\]'
            matches = re.findall(image_pattern, question)
            
            if matches:
                # Display images first, then question
                for match in matches:
                    img_num = int(match) - 1
                    if 0 <= img_num < len(image_analyses):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(
                                image_analyses[img_num]['image'], 
                                caption=f"📸 Image {img_num + 1}: {image_analyses[img_num]['source']}",
                                width=300
                            )
                        with col2:
                            # Remove image reference from question text and display
                            clean_question = re.sub(image_pattern, '', question).strip()
                            st.markdown(clean_question)
            else:
                # Display question without image
                st.markdown(question)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="AI Question Generator Pro",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load enhanced CSS with animations
    load_css()
    
    # Animated app header
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">🎓 AI Question Generator Pro</h1>
        <p class="app-subtitle">Create intelligent question sets with advanced image analysis and professional PDF exports</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API key
    api_key = get_openai_api_key()
    if not api_key:
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        create_status_message("❌ OpenAI API key not found!", "error")
        st.markdown("""
        **🔑 Setup Instructions:**
        1. Create a `.env` file in your project folder
        2. Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`
        3. Or add it to Streamlit secrets if deploying to cloud
        
        📎 Get your API key from: https://platform.openai.com/account/api-keys
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    qg = QuestionGenerator()
    
    # Enhanced sidebar with animations
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        
        # API Status with animated indicators
        create_status_message("✅ API Key Active", "success")
        create_status_message("🖼️ Image Analysis Ready", "success")
        create_status_message("📊 PDF Export Ready", "success")
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        if st.button("🔄 Refresh App", use_container_width=True):
            st.rerun()
            
        if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
            st.session_state.generated_question_sets = []
            st.session_state.current_set = 0
            st.session_state.extracted_images = []
            st.rerun()
        
        st.markdown("---")
        
        # Question Set Navigation with enhanced styling
        if st.session_state.generated_question_sets:
            st.markdown("### 📚 Question Sets")
            set_options = [f"Set {i+1}" for i in range(len(st.session_state.generated_question_sets))]
            selected_set = st.selectbox("📂 Choose Set:", set_options, index=st.session_state.current_set)
            st.session_state.current_set = set_options.index(selected_set)
            
            # Animated set metrics
            current_set = st.session_state.generated_question_sets[st.session_state.current_set]
            create_metric_card("Characters", len(current_set['questions']))
            create_metric_card("Images", len(st.session_state.extracted_images), "🖼️")
        
        st.markdown("---")
        
        # Enhanced image preview
        if st.session_state.extracted_images:
            st.markdown("### 🖼️ Extracted Images")
            st.write(f"📊 Found {len(st.session_state.extracted_images)} images")
            
            with st.expander("👁️ Preview Images", expanded=False):
                for i, img_data in enumerate(st.session_state.extracted_images[:3]):
                    st.image(img_data['image'], caption=f"Image {i+1}: {img_data['source']}", width=200)
                if len(st.session_state.extracted_images) > 3:
                    st.caption(f"... and {len(st.session_state.extracted_images) - 3} more images")
        
        st.markdown("---")
        
        # Debug section with enhanced styling
        with st.expander("🐛 Debug Info", expanded=False):
            if st.button("Show API Status", use_container_width=True):
                if api_key:
                    st.success(f"✅ API Key: {api_key[:10]}...")
                else:
                    st.error("❌ No API Key")
            
            st.write(f"**Sessions:** {len(st.session_state.generated_question_sets)} sets")
            st.write(f"**Current Set:** {st.session_state.current_set + 1}")
            st.write(f"**Images:** {len(st.session_state.extracted_images)}")
    
    # Enhanced main content area with tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Generate", "📝 View Results", "📊 Analytics"])
    
    with tab1:
        # Enhanced upload section
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown("## 📤 Upload Study Materials")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "📁 Choose your files",
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True,
                help="Upload up to 10 study materials (PDFs and DOCX files will be scanned for images)"
)
            if uploaded_files and len(uploaded_files) > 10:
                create_status_message("⚠️ Maximum 10 files allowed. Using first 10 files.", "warning")
                uploaded_files = uploaded_files[:10]
        
        with col2:
            if uploaded_files:
                st.markdown("### 📋 File Summary")
                for i, file in enumerate(uploaded_files):
                    file_size = file.size / 1024
                    st.markdown(f"**File {i+1}:** {file.name}")
                    st.caption(f"Size: {file_size:.1f} KB | Type: {file.type.split('/')[-1].upper()}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced reference paper section
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown("## 📄 Reference Question Paper (Optional)")
        
        ref_files = st.file_uploader(
            "📎 Upload reference papers",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload up to 10 sample question papers to match the style"
)
        
        if ref_files:
            if len(ref_files) > 10:
                create_status_message("⚠️ Maximum 10 reference files allowed. Using first 10 files.", "warning")
                ref_files = ref_files[:10]
            create_status_message(f"✅ {len(ref_files)} reference paper(s) loaded", "success")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced web links section
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown("## 🔗 Web Resources (Optional)")
        st.markdown("**Enter up to 10 web URLs (one per line):**")
        urls_text = st.text_area(
            "🌐 Web URLs",
            placeholder="https://example.com/article1\nhttps://example.com/article2\n...",
            height=150,
            help="Enter each URL on a new line, up to 10 URLs total"
)
        web_urls = []
        if urls_text.strip():
            urls_list = [url.strip() for url in urls_text.split('\n') if url.strip()]
            web_urls = urls_list[:10]  # Limit to 10
    
            if len(urls_list) > 10:
                create_status_message("⚠️ Maximum 10 URLs allowed. Using first 10 URLs.", "warning")
    
            if web_urls:
                create_status_message(f"✅ {len(web_urls)} web resource(s) added", "success")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced settings section
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown("## ⚙️ Question Generation Settings")
        
        col_set1, col_set2, col_set3 = st.columns(3)
        
        with col_set1:
            difficulty = st.selectbox(
                "🎯 Difficulty Level", 
                ["Easy", "Medium", "Hard"], 
                index=1,
                help="Choose the complexity level for your questions"
            )
        
        with col_set2:
            num_questions = st.slider(
                "📝 Questions per Set", 
                min_value=5, 
                max_value=25, 
                value=12, 
                step=1,
                help="Number of questions in each set"
            )
        
        with col_set3:
            st.markdown("**🎲 Sets to Generate**")
            st.markdown('<div class="metric-card"><div class="metric-value">5</div></div>', unsafe_allow_html=True)
        
        st.markdown("### 📋 Question Types")
        question_types = st.multiselect(
            "Select question formats:",
            [
                "Multiple Choice Questions (MCQ)", 
                "Short Answer", 
                "Long Answer", 
                "Fill in the Blanks", 
                "True/False",
                "Case Studies",
                "Problem Solving"
            ],
            default=["Multiple Choice Questions (MCQ)", "Short Answer"],
            help="Choose the types of questions you want to generate"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced feature highlights with animations
        create_feature_highlight(
            "🎯 Smart Image Integration", 
            "Images are automatically analyzed and integrated into questions with visual context",
            "🖼️"
        )
        
        create_feature_highlight(
            "📊 Professional PDF Export", 
            "Download beautifully formatted PDFs with embedded images and proper styling",
            "📄"
        )
        
        # Enhanced generate button
        generate_disabled = not uploaded_files and not web_urls
        
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        if st.button(
            "🚀 Generate 5 Question Sets with AI Analysis", 
            type="primary", 
            use_container_width=True, 
            disabled=generate_disabled,
            help="Start the AI-powered question generation process"
):
            if generate_disabled:
                create_status_message("❌ Please upload at least one file or provide a URL", "error")
            else:
        # Enhanced processing with animated UI
                with st.container():
                    st.markdown("## 🔄 AI Processing Pipeline")
            
            # Create animated progress container
                    progress_container = st.container()
                    with progress_container:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        current_step = st.empty()
            
            # Initialize variables
                    all_content = ""
                    total_steps = 0
            
            # Calculate total steps
                    if uploaded_files:
                        total_steps += len(uploaded_files)
                    if web_urls:
                        total_steps += len(web_urls)
                    if ref_files:
                        total_steps += len(ref_files)
                    total_steps += 3  # Image processing, content analysis, question generation
            
                    current_step_num = 0
            
            # Process uploaded files with enhanced feedback
                    if uploaded_files:
                        for file in uploaded_files:
                            current_step_num += 1
                            current_step.markdown(f"**Step {current_step_num}/{total_steps}:** Processing {file.name}")
                            status_text.info(f"🔍 Extracting content from {file.name}...")
                    
                    # Show animated progress
                            create_animated_progress(f"Processing {file.name}", (current_step_num / total_steps) * 100)
                    
                            try:
                                if file.type == "application/pdf":
                                    text = qg.extract_text_from_pdf(file)
                                elif "wordprocessingml" in file.type:
                                    text = qg.extract_text_from_docx(file)
                                elif file.type == "text/plain":
                                    text = qg.extract_text_from_txt(file)
                                else:
                                    st.warning(f"⚠️ Unsupported file type: {file.type}")
                                    text = ""
                        
                                if text.strip():
                                    all_content += f"\n\n=== Content from {file.name} ===\n{text}"
                                    # st.success(f"✅ Extracted {len(text)} characters from {file.name}")
                                else:
                                    st.warning(f"⚠️ No text extracted from {file.name}")
                            
                            except Exception as e:
                                st.error(f"❌ Error processing {file.name}: {str(e)}")
                    
                            progress_bar.progress(current_step_num / total_steps)
                            time.sleep(0.3)  # Enhanced visual feedback
            
            # Process URLs with animations
            if web_urls:
                for i, url in enumerate(web_urls, 1):
                    if url.strip():
                        current_step_num += 1
                        current_step.markdown(f"**Step {current_step_num}/{total_steps}:** Processing Web URL {i}")
                        status_text.info(f"🌐 Fetching content from URL {i}...")

                        create_animated_progress(f"Fetching URL {i}", (current_step_num / total_steps) * 100)

                        try:
                            text = qg.extract_text_from_url(url.strip())

                            if text.strip():
                                all_content += f"\n\n=== Content from URL {i} ===\n{text}"
                                # st.success(f"✅ Extracted {len(text)} characters from URL {i}")
                            else:
                                st.warning(f"⚠️ No content extracted from URL {i}")
                                
                        except Exception as e:
                            st.error(f"❌ Error processing URL {i}: {str(e)}")

                        progress_bar.progress(current_step_num / total_steps)
                        time.sleep(0.3)
            
            # Process reference files with enhanced feedback
            reference_style = ""
            if ref_files:
                for i, ref_file in enumerate(ref_files, 1):
                    current_step_num += 1
                    current_step.markdown(f"**Step {current_step_num}/{total_steps}:** Processing Reference Paper {i}")
                    status_text.info(f"📄 Analyzing reference paper {i} style...")

                    create_animated_progress(f"Analyzing Reference Style {i}", (current_step_num / total_steps) * 100)

                    try:
                        ref_text = ""
                        if ref_file.type == "application/pdf":
                            ref_text = qg.extract_text_from_pdf(ref_file)
                        elif "wordprocessingml" in ref_file.type:
                            ref_text = qg.extract_text_from_docx(ref_file)
                        elif ref_file.type == "text/plain":
                            ref_text = qg.extract_text_from_txt(ref_file)

                        if ref_text.strip():
                            reference_style += f"\n\n=== Reference Style from {ref_file.name} ===\n{ref_text}"
                            # st.success(f"✅ Extracted {len(ref_text)} characters from reference paper {i}")
                        else:
                            st.warning(f"⚠️ No text extracted from reference paper {i}")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing reference paper {i}: {str(e)}")

                    progress_bar.progress(current_step_num / total_steps)
                    time.sleep(0.3)

                if reference_style.strip():
                    create_status_message(f"✅ {len(ref_files)} reference paper(s) style will be applied", "success")
            
            # Enhanced image processing
            current_step_num += 1
            current_step.markdown(f"**Step {current_step_num}/{total_steps}:** AI Image Analysis")
            status_text.info("🖼️ Analyzing images with AI...")
            
            create_animated_progress("AI Image Analysis", (current_step_num / total_steps) * 100)
            
            try:
                urls_list = web_urls if web_urls else []
                ref_files_list = ref_files if ref_files else []
                
                image_analyses = qg.image_processor.process_all_images(uploaded_files, urls_list, ref_files_list)
                st.session_state.extracted_images = image_analyses
                
                if image_analyses:
                    st.success(f"✅ Successfully analyzed {len(image_analyses)} images")
                else:
                    st.info("ℹ️ No images found to analyze")
                    
            except Exception as e:
                st.error(f"❌ Error during image processing: {str(e)}")
                image_analyses = []
                st.session_state.extracted_images = []
            
            progress_bar.progress(current_step_num / total_steps)
            time.sleep(0.3)
            
            # Enhanced content validation
            current_step_num += 1
            current_step.markdown(f"**Step {current_step_num}/{total_steps}:** Content Validation")
            status_text.info("✅ Validating extracted content...")
            
            create_animated_progress("Content Validation", (current_step_num / total_steps) * 100)
            
            progress_bar.progress(current_step_num / total_steps)
            
            if all_content.strip() or image_analyses:
                if all_content.strip():
                    create_status_message(f"✅ Extracted {len(all_content):,} characters from all sources", "success")
                if image_analyses:
                    create_status_message(f"✅ Analyzed {len(image_analyses)} images with AI", "success")
                
                # Enhanced question generation
                current_step_num += 1
                current_step.markdown(f"**Step {current_step_num}/{total_steps}:** Generating Question Sets")
                status_text.info("🧠 AI is generating 5 unique question sets...")
                
                create_animated_progress("AI Question Generation", (current_step_num / total_steps) * 100)
                
                try:
                    question_sets = qg.generate_multiple_question_sets(
                        all_content, difficulty, num_questions, question_types, reference_style, image_analyses, 5
                    )
                    
                    progress_bar.progress(1.0)
                    
                    if question_sets:
                        st.session_state.generated_question_sets = question_sets
                        st.session_state.current_set = 0
                        
                        # Clear progress indicators
                        progress_container.empty()
                        
                        # Enhanced success celebration
                        st.balloons()
                        create_status_message(f"🎉 Successfully generated {len(question_sets)} unique question sets!", "success")
                        
                        # Enhanced generation summary
                        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
                        st.markdown("### 📊 Generation Summary")
                        
                        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                        with col_sum1:
                            create_metric_card("Question Sets", len(question_sets), "📚")
                        with col_sum2:
                            create_metric_card("Total Questions", len(question_sets) * num_questions, "❓")
                        with col_sum3:
                            create_metric_card("Images Analyzed", len(image_analyses), "🖼️")
                        with col_sum4:
                            create_metric_card("Content Sources", len(uploaded_files or []) + len(web_urls), "📁")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    else:
                        progress_container.empty()
                        create_status_message("❌ Failed to generate question sets. Please try again.", "error")
                        
                except Exception as e:
                    progress_container.empty()
                    create_status_message(f"❌ Error during question generation: {str(e)}", "error")
                    
            else:
                progress_container.empty()
                create_status_message("❌ No content or images could be extracted. Please check your sources.", "error")
                
                # Enhanced debug information
                with st.expander("🐛 Debug Information", expanded=True):
                    st.write(f"**Files uploaded:** {len(uploaded_files) if uploaded_files else 0}")
                    st.write(f"**URLs provided:** {len(web_urls)}")
                    st.write(f"**Reference files:** {len(ref_files) if ref_files else 0}")
                    st.write(f"**Images found:** {len(image_analyses) if 'image_analyses' in locals() else 0}")
                    st.write(f"**Total content length:** {len(all_content)}")
                    
                    if uploaded_files:
                        st.write("**File details:**")
                        for file in uploaded_files:
                            st.write(f"- {file.name}: {file.size} bytes, type: {file.type}")
                    
                    if web_urls:
                        st.write("**URLs provided:**")
                        for i, url in enumerate(web_urls, 1):
                            st.write(f"- URL {i}: {url}")
                    
                    if ref_files:
                        st.write("**Reference files:**")
                        for file in ref_files:
                            st.write(f"- {file.name}: {file.size} bytes, type: {file.type}")    
    with tab2:
        # Enhanced results viewing tab
        if not st.session_state.generated_question_sets:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("## 📝 No Results Yet")
            st.info("🎯 Generate your first question set in the **Upload & Generate** tab to view results here!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            current_set_data = st.session_state.generated_question_sets[st.session_state.current_set]
            
            # Enhanced set header with metrics
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown(f"## 📝 Question Set {current_set_data['set_number']}")
            
            col_header1, col_header2, col_header3 = st.columns(3)
            with col_header1:
                create_metric_card("Characters", f"{len(current_set_data['questions']):,}", "📄")
            with col_header2:
                create_metric_card("Images", len(st.session_state.extracted_images), "🖼️")
            with col_header3:
                create_metric_card("Generated", current_set_data['timestamp'].split()[1][:5], "⏰")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced download section
            create_enhanced_download_buttons(current_set_data, st.session_state.extracted_images, difficulty if 'difficulty' in locals() else 'Medium')
            
            # Enhanced display mode selection
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            view_mode = st.radio(
                "🎨 Display Mode:",
                ["📖 Interactive View (with Images)", "📝 Raw Text View", "🎯 Question-by-Question"],
                horizontal=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display content based on selected mode
            if view_mode == "📖 Interactive View (with Images)":
                if st.session_state.extracted_images:
                    create_status_message("🖼️ Images will be displayed directly with related questions", "success")
                display_question_set_with_images(current_set_data, st.session_state.extracted_images)
                
            elif view_mode == "🎯 Question-by-Question":
                # Split questions and display individually with enhanced styling
                questions_text = current_set_data['questions']
                questions_list = [q.strip() for q in questions_text.split('\n\n') if q.strip()]
                
                for i, question in enumerate(questions_list):
                    if question:
                        with st.container():
                            st.markdown('<div class="question-card">', unsafe_allow_html=True)
                            st.markdown(f"### Question {i+1}")
                            st.markdown(question)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
            else:  # Raw text view
                st.markdown('<div class="glass-container">', unsafe_allow_html=True)
                st.text_area(
                    f"📝 Raw Questions - Set {current_set_data['set_number']}:",
                    value=current_set_data['questions'],
                    height=600,
                    help="Raw text format for easy copying"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced set overview
            if len(st.session_state.generated_question_sets) > 1:
                st.markdown('<div class="glass-container">', unsafe_allow_html=True)
                with st.expander(f"📚 Overview of All {len(st.session_state.generated_question_sets)} Sets", expanded=False):
                    for i, set_data in enumerate(st.session_state.generated_question_sets):
                        col_ov1, col_ov2, col_ov3 = st.columns([2, 1, 1])
                        with col_ov1:
                            st.write(f"**Set {set_data['set_number']}**")
                        with col_ov2:
                            st.write(f"{len(set_data['questions']):,} chars")
                        with col_ov3:
                            st.write(set_data['timestamp'].split()[1][:5])
                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        # Enhanced analytics tab
        if not st.session_state.generated_question_sets:
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("## 📊 No Analytics Data")
            st.info("📈 Generate question sets to view detailed analytics and insights!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("## 📊 Question Generation Analytics")
            
            # Enhanced overall metrics
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("### 🎯 Overall Performance")
            
            total_chars = sum(len(set_data['questions']) for set_data in st.session_state.generated_question_sets)
            avg_chars = total_chars // len(st.session_state.generated_question_sets)
            
            col_an1, col_an2, col_an3, col_an4 = st.columns(4)
            with col_an1:
                create_metric_card("Total Sets", len(st.session_state.generated_question_sets), "📚")
            with col_an2:
                create_metric_card("Avg Length", f"{avg_chars:,}", "📄")
            with col_an3:
                create_metric_card("Images Used", len(st.session_state.extracted_images), "🖼️")
            with col_an4:
                create_metric_card("Total Chars", f"{total_chars:,}", "💬")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced set comparison
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("### 📈 Set Comparison")
            
            # Create comparison chart data
            set_lengths = [len(set_data['questions']) for set_data in st.session_state.generated_question_sets]
            set_numbers = [f"Set {set_data['set_number']}" for set_data in st.session_state.generated_question_sets]
            
            # Display as bar chart using Streamlit's built-in charting
            import pandas as pd
            
            chart_data = pd.DataFrame({
                'Question Set': set_numbers,
                'Character Count': set_lengths
            })
            
            st.bar_chart(chart_data.set_index('Question Set'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced image analysis details
            if st.session_state.extracted_images:
                st.markdown('<div class="glass-container">', unsafe_allow_html=True)
                st.markdown("### 🖼️ Image Analysis Summary")
                
                # Group images by source
                source_counts = {}
                for img in st.session_state.extracted_images:
                    source = img['source']
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                col_img1, col_img2 = st.columns(2)
                
                with col_img1:
                    st.markdown("**📁 Images by Source:**")
                    for source, count in source_counts.items():
                        st.write(f"• {source}: {count} image(s)")
                
                with col_img2:
                    st.markdown("**🔍 Analysis Quality:**")
                    avg_analysis_length = sum(len(img['analysis']) for img in st.session_state.extracted_images) // len(st.session_state.extracted_images)
                    st.write(f"• Average analysis: {avg_analysis_length} characters")
                    st.write(f"• Total images processed: {len(st.session_state.extracted_images)}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced generation timeline
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("### ⏰ Generation Timeline")
            
            for i, set_data in enumerate(st.session_state.generated_question_sets):
                col_time1, col_time2, col_time3 = st.columns([1, 2, 1])
                with col_time1:
                    st.write(f"**Set {set_data['set_number']}**")
                with col_time2:
                    st.write(f"Generated: {set_data['timestamp']}")
                with col_time3:
                    st.write(f"{len(set_data['questions']):,} chars")
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()


