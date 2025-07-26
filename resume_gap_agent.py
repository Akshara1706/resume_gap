import streamlit as st
import pdfplumber
import requests
import io

# 🔑 OpenRouter API Key
OPENROUTER_API_KEY = "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"

# OpenRouter API settings
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-app.com"  # Optional but recommended
}

# ========== 📄 PDF TEXT EXTRACTION ==========
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ========== 🔍 AI RESUME SUMMARY ==========
def summarize_resume(resume_text):
    prompt = f"Summarize the following resume in 4-5 concise sentences:\n\n\"\"\"\n{resume_text}\n\"\"\""
    data = {
        "model": "openrouter/openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a professional resume summarizer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as err:
        st.error(f"❌ API Error (Summary): {err}")
        return "API error while summarizing resume."

# ========== 📊 AI GAP ANALYSIS ==========
def analyze_resume_with_openrouter(resume_text, target_role):
    prompt = f"""
You are a career coach AI. Analyze the resume content provided below.
Compare it to a typical {target_role} profile.
Identify missing skills, experiences, or tools.
Suggest actionable improvements and a learning roadmap.

Resume:
\"\"\"{resume_text}\"\"\"
"""
    data = {
        "model": "openrouter/openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an expert resume analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as err:
        st.error(f"❌ API Error (Gap Analysis): {err}")
        return "API error while performing gap analysis."

# ========== ✅ MATCH VERDICT CHECK ==========
def judge_resume_fit(resume_text, target_role):
    prompt = f"""
Does the following resume match the requirements of a {target_role}?
Answer only with YES or NO.

Resume:
\"\"\"{resume_text}\"\"\"
"""
    data = {
        "model": "openrouter/openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an expert HR evaluator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip().upper()
    except requests.exceptions.HTTPError as err:
        st.error(f"❌ API Error (Match Verdict): {err}")
        return "API error while checking job match."

# ========== 💻 STREAMLIT UI ==========
st.set_page_config(page_title="Resume Gap Analysis Agent", layout="centered")
st.title("🧠 Resume Gap Analysis Agent (via OpenRouter API)")
st.write("Upload your resume and enter a target job role to receive improvement suggestions and a learning roadmap.")

uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type="pdf")
target_role = st.text_input("🎯 Target Job Role (e.g., Backend Developer, Data Scientist)")

if uploaded_file and target_role:
    with st.spinner("📃 Extracting resume content..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        word_count = len(resume_text.split())

    st.info(f"📊 **Resume Word Count:** {word_count} words")

    with st.spinner("🔍 Summarizing your resume..."):
        summary = summarize_resume(resume_text)
    st.markdown("### 🔍 Resume Summary")
    st.write(summary)

    with st.spinner("✅ Checking resume fit for the role..."):
        match_result = judge_resume_fit(resume_text, target_role)
        if "YES" in match_result:
            st.success("✅ Your resume is a good match for the selected role!")
        else:
            st.warning("❌ Your resume needs improvement to match the selected role.")

    with st.spinner("📊 Analyzing resume for missing skills and suggestions..."):
        gap_analysis = analyze_resume_with_openrouter(resume_text, target_role)

    st.markdown("### 📊 Resume Gap Analysis Result")
    st.write(gap_analysis)

    # 📥 Download full report
    full_report = f"""
Target Role: {target_role}

=====================
🔍 Resume Summary:
{summary}

=====================
✅ Resume Match Verdict:
{match_result}

=====================
📊 Gap Analysis:
{gap_analysis}
"""

    st.download_button(
        label="📥 Download Full Report",
        data=full_report,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )
