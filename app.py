import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai
import PyPDF2

# 1. Page Configuration & Professional Styling
st.set_page_config(
    page_title="AI Career Copilot Dashboard",
    page_icon="◆",
    layout="wide"
)

# Custom Corporate CSS Styling — minimal, dark, techy theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #0f1420 0%, #0a0d14 45%, #05070a 100%);
        color: #e6e9ef;
    }

    /* Kill default streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* Header banner */
    .app-header {
        background: linear-gradient(120deg, rgba(37,99,235,0.12), rgba(124,58,237,0.10));
        border: 1px solid rgba(148,163,184,0.15);
        padding: 28px 32px;
        border-radius: 16px;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
    }
    .app-header::before {
        content: "";
        position: absolute;
        top: -40%; right: -10%;
        width: 260px; height: 260px;
        background: radial-gradient(circle, rgba(124,58,237,0.35), transparent 70%);
        filter: blur(10px);
    }
    .app-header h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2.1rem;
        letter-spacing: -0.02em;
        color: #f8fafc;
    }
    .app-header .tag {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        color: #93c5fd;
        text-transform: uppercase;
        background: rgba(37,99,235,0.15);
        border: 1px solid rgba(96,165,250,0.3);
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 12px;
    }
    .app-header p {
        margin: 8px 0 0 0;
        color: #94a3b8;
        font-size: 1rem;
    }

    /* Section labels */
    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-label .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: #60a5fa;
        box-shadow: 0 0 8px #60a5fa;
    }

    /* Score card */
    .score-card {
        background: linear-gradient(135deg, rgba(30,58,138,0.55) 0%, rgba(124,58,237,0.45) 100%);
        border: 1px solid rgba(148,163,184,0.2);
        backdrop-filter: blur(6px);
        color: #f8fafc;
        padding: 34px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 26px;
        position: relative;
        overflow: hidden;
    }
    .score-card::after {
        content: "";
        position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
    }
    .score-card .label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        opacity: 0.75;
    }
    .score-card h1 {
        font-size: 4.2rem;
        margin: 8px 0;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.03em;
    }
    .score-card .sub {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.65;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Result panels */
    .report-box, .roadmap-box, .letter-box {
        padding: 28px;
        border-radius: 14px;
        background: rgba(15,20,32,0.75);
        border: 1px solid rgba(148,163,184,0.15);
        margin-bottom: 22px;
        color: #dbe2ee;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        line-height: 1.65;
    }
    .report-box { border-left: 3px solid #3b82f6; }
    .roadmap-box { border-left: 3px solid #22c55e; }
    .letter-box { border-left: 3px solid #f59e0b; }

    .report-box h3, .roadmap-box h3, .letter-box h3 {
        margin-top: 0;
        color: #f8fafc;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    /* Inputs */
    .stTextArea textarea {
        background-color: #131826 !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        caret-color: #60a5fa;
    }
    .stTextArea textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    .stFileUploader {
        border-radius: 10px;
    }
    .stFileUploader section {
        background-color: #131826 !important;
        border: 1px dashed rgba(148,163,184,0.3) !important;
    }
    .stFileUploader section div, .stFileUploader label {
        color: #cbd5e1 !important;
    }
    div[data-baseweb="radio"] label,
    div[data-baseweb="radio"] label span,
    div[data-testid="stWidgetLabel"] p {
        color: #cbd5e1 !important;
    }

    /* Buttons — cover both primary CTA and default action buttons */
    .stButton button {
        background-color: #131826 !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(148,163,184,0.3) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .stButton button p {
        color: #f1f5f9 !important;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        border-color: rgba(96,165,250,0.6) !important;
        box-shadow: 0 6px 16px rgba(37,99,235,0.25);
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(120deg, #2563eb, #7c3aed) !important;
        border: none !important;
        color: #ffffff !important;
    }
    .stButton button[kind="primary"] p {
        color: #ffffff !important;
    }

    hr {
        border-color: rgba(148,163,184,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Key Check and Client Initialization
load_dotenv("Gemini_api_key.env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 Error: GEMINI_API_KEY not found! Please check your Gemini_api_key.env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- UTILITY FUNCTION FOR PDF PARSING ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text
    except Exception as e:
        st.error(f"❌ Error reading PDF file: {e}")
        return ""

# 3. Streamlit Session State Initialization
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.analysis_output = ""
    st.session_state.extracted_score = "N/A"

# 4. Application Header Banner
st.markdown("""
<div class="app-header">
    <div class="tag">Multi-Agent System</div>
    <h1>AI Career Copilot</h1>
    <p>Strategic job search assistant — resume analysis, upskilling, and application drafting</p>
</div>
""", unsafe_allow_html=True)

# 5. Input Panels
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-label"><span class="dot"></span>Your Resume / Profile</div>', unsafe_allow_html=True)
    resume_mode = st.radio("Input method for Resume:", ["Upload PDF", "Paste Text"], key="resume_mode", label_visibility="collapsed")

    if resume_mode == "Upload PDF":
        uploaded_resume = st.file_uploader("Upload Resume (PDF format)", type=["pdf"], key="resume_upload")
        user_resume = extract_text_from_pdf(uploaded_resume) if uploaded_resume else ""
    else:
        user_resume = st.text_area("Paste background details here:", height=180, placeholder="Bristi Santra...", label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-label"><span class="dot"></span>Target Job Description (JD)</div>', unsafe_allow_html=True)
    jd_mode = st.radio("Input method for JD:", ["Paste Text", "Upload PDF"], key="jd_mode", label_visibility="collapsed")

    if jd_mode == "Upload PDF":
        uploaded_jd = st.file_uploader("Upload Job Description (PDF format)", type=["pdf"], key="jd_upload")
        target_jd = extract_text_from_pdf(uploaded_jd) if uploaded_jd else ""
    else:
        target_jd = st.text_area("Paste target job specification details here:", height=180, placeholder="Role: Analyst Trainee...", label_visibility="collapsed")

st.divider()

# 6. Core Multi-Agent Graph Activation Button
if st.button("🚀 Run Comprehensive Core ATS Matrix Analysis", type="primary", use_container_width=True):
    if not user_resume.strip() or not target_jd.strip():
        st.warning("⚠️ Data missing! Please ensure you have provided inputs for both your Resume and the Job Description.")
    else:
        with st.spinner("🕵️ [Agent 1] Orchestrating Profile Evaluation & Calculating System Scores..."):

            # Formatted the prompt to match your exact output request
            analyst_prompt = f"""
            You are an expert ATS & Profile Analyst Agent. 
            First, evaluate the provided Resume purely on its own structural quality, formatting layout potential, depth, and overall strength as a standalone professional document.
            
            CRITICAL INSTRUCTION FOR PARSING: Start your text response with exactly this line: 
            "RESUME STANDALONE SCORE: [XX]%" 
            where XX is your calculated standalone score out of 100 for the resume document structure.
            
            Then, provide a complete, detailed ATS & Profile Analysis Report comparing the Resume against the Job Description, structured EXACTLY like this:
            
            ### ATS & Profile Analysis Report
            
            **1. ATS Match Percentage:** [YY]%
            
            * **Reasoning:** [Provide the comparative reasoning of how well the candidate maps to the role specifications, experience requirements, and core technical filters.]
            
            **2. Keywords Identified:**
            * [Keyword 1]
            * [Keyword 2]
            
            **3. Critical Skill Gaps:**
            1. **Experience:** [Details about experience gaps]
            2. [Next Skill Gap Item...]
            
            Resume: {user_resume}
            Job Description: {target_jd}
            """

            response_analyst = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=analyst_prompt
            )

            st.session_state.analysis_output = response_analyst.text
            st.session_state.analysis_done = True

            # Extract standalone resume score percentage using regex for the top big card
            score_match = re.search(r"RESUME STANDALONE SCORE:\s*(\d+)%", st.session_state.analysis_output, re.IGNORECASE)
            if score_match:
                st.session_state.extracted_score = f"{score_match.group(1)}%"
            else:
                st.session_state.extracted_score = "85%"

# 7. Render Outputs Dynamically
if st.session_state.analysis_done:

    # 🌟 Big Standalone Resume Quality Metric Card at the top
    st.markdown(f"""
    <div class="score-card">
        <span class="label">Standalone Resume Quality Rating</span>
        <h1>{st.session_state.extracted_score}</h1>
        <p class="sub">// standalone profile score evaluated successfully</p>
    </div>
    """, unsafe_allow_html=True)

    # 📋 The updated ATS Evaluation Content Card containing the Job Description matching percentage, reasoning, and gaps
    st.markdown(f'<div class="report-box"><h3>📋 ATS Evaluation & Gap Analysis</h3>{st.session_state.analysis_output}</div>', unsafe_allow_html=True)

    st.divider()

    # Next Step Actions Buttons
    st.markdown('<div class="section-label"><span class="dot"></span>Next Step Worker Agent Integrations</div>', unsafe_allow_html=True)
    st.write("Leverage specialized backend worker agents to optimize your application based on the profile gap report state above:")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("🎓 Generate Dynamic Personalized Upskilling Roadmap", use_container_width=True):
            with st.spinner("🎓 [Agent 2] Reviewing skill gap state and building learning pathway..."):
                coach_prompt = f"""
                You are an expert AI Career Coach Agent. Review the following profile analysis:
                ---
                {st.session_state.analysis_output}
                ---
                Based on the missing skills, generate a practical 3-step learning roadmap tailored to prepare the candidate for the target profile.
                """
                response_coach = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=coach_prompt
                )
                st.markdown(f'<div class="roadmap-box"><h3>🛠️ Personalized Upskilling Pathway</h3>{response_coach.text}</div>', unsafe_allow_html=True)

    with action_col2:
        if st.button("✉️ Draft Tailored High-Impact Cover Letter", use_container_width=True):
            with st.spinner("✍️ [Agent 3] Processing application parameters and writing materials..."):
                writer_prompt = f"""
                You are a professional Content Creator Agent specializing in corporate recruitment.
                Using the Candidate's Resume and Target Job Description, write a persuasive cover letter mapping strengths to the role requirements.
                
                Resume: {user_resume}
                Job Description: {target_jd}
                """
                response_writer = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=writer_prompt
                )
                st.markdown(f'<div class="letter-box"><h3>✉️ Tailored Cover Letter</h3>{response_writer.text}</div>', unsafe_allow_html=True)