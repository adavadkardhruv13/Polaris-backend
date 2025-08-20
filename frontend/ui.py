import streamlit as st
import base64

st.set_page_config(page_title="Dvault - Pitch Analyzer", layout="centered")

# Centered top navbar style
st.markdown("""
    <style>
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #000000;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        font-size: 20px;
    }
    .top-nav button {
        background-color: #6C47FF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.4rem 1rem;
        font-size: 16px;
        cursor: pointer;
    }
    .upload-box {
        border: 2px dashed #C3B5FF;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        color: #6C47FF;
        background-color: #FAF9FF;
        margin-top: 2rem;
    }
    .upload-box h4 {
        margin-top: 1rem;
        color: #444;
    }
    </style>
""", unsafe_allow_html=True)

# Top navigation bar
st.markdown("""
<div class="top-nav">
  <div><strong>Dvault</strong></div>
  <div><button>Upload</button></div>
</div>
""", unsafe_allow_html=True)

# Heading and subheading
st.markdown("""
<div style="text-align: center; margin-top: 4rem;">
    <h1 style="font-size: 2rem;">Elevate Your Pitch. Close More Deals.</h1>
    <p style="font-size: 1.1rem; color: #555; max-width: 600px; margin: auto;">
        Unlock the power of AI to analyze every aspect of your pitch deck, giving you the insights to impress investors.
    </p>
</div>
""", unsafe_allow_html=True)

# Upload box
st.markdown("""
<div class="upload-box">
    <div style="font-size: 36px;">⬆️</div>
    <h4>Click here to upload your file</h4>
    <p>Supported Formats: PDF</p>
</div>
""", unsafe_allow_html=True)

# Upload functionality
uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    st.success("✅ File uploaded successfully. Analysis will begin shortly...")
