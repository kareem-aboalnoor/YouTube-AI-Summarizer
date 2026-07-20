import re
import requests
import streamlit as st

# =========================================================
# Configuration - edit these values
# =========================================================
API_KEY = "secret123"
PUBLIC_URL = "https://coherent-endowment-outpost.ngrok-free.dev"  # example: https://your-api.example.com

# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# Professional dark theme CSS
# =========================================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: linear-gradient(180deg, #0f1117 0%, #161925 100%);
    }

    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #f5f5f7;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }

    .sub-title {
        font-size: 0.95rem;
        color: #9a9ba5;
        text-align: center;
        margin-bottom: 2rem;
    }

    div[data-testid="stTextInput"] input {
        background-color: #1c1f2b;
        color: #f5f5f7;
        border: 1px solid #2c2f3e;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        font-size: 0.95rem;
    }

    div[data-testid="stTextInput"] input:focus {
        border: 1px solid #6c63ff;
        box-shadow: 0 0 0 1px #6c63ff;
    }

    .stButton button {
        background: linear-gradient(90deg, #6c63ff, #5046e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(108, 99, 255, 0.35);
    }

    .result-card {
        background-color: #1c1f2b;
        border: 1px solid #2c2f3e;
        border-radius: 14px;
        padding: 1.6rem;
        margin-top: 1.5rem;
        color: #e4e4e9;
        line-height: 1.8;
        font-size: 0.98rem;
    }

    .result-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        color: #6c63ff;
        margin-bottom: 0.8rem;
        font-size: 1rem;
    }

    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .status-ok {
        background-color: rgba(52, 199, 89, 0.15);
        color: #34c759;
    }

    .status-error {
        background-color: rgba(255, 69, 58, 0.15);
        color: #ff453a;
    }

    .video-thumb {
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #2c2f3e;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Helper functions
# =========================================================
def extract_video_id(url: str):
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def call_summarize_api(youtube_url: str):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {"youtube_url": youtube_url}
    response = requests.post(
        f"{PUBLIC_URL}/summarize",
        headers=headers,
        json=payload,
        timeout=120,
    )
    return response


# =========================================================
# UI
# =========================================================
st.markdown('<div class="main-title">🎬 YouTube Summarizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Paste a YouTube link and get an instant summary</div>',
    unsafe_allow_html=True,
)

youtube_url = st.text_input(
    label="Video URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

video_id = extract_video_id(youtube_url) if youtube_url else None
if video_id:
    st.image(
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        use_container_width=True,
    )

submit = st.button("Summarize video", use_container_width=True)

if submit:
    if not youtube_url.strip():
        st.warning("Please enter a video URL first.")
    elif not video_id:
        st.error("This doesn't look like a valid YouTube URL. Please check it.")
    else:
        with st.spinner("Analyzing and summarizing the video..."):
            try:
                response = call_summarize_api(youtube_url)
                status_code = response.status_code

                try:
                    data = response.json()
                except ValueError:
                    data = {"raw": response.text}

                if status_code == 200:
                    st.markdown(
                        '<span class="status-pill status-ok">Success</span>',
                        unsafe_allow_html=True,
                    )
                    summary_text = (
                        data.get("summary")
                        or data.get("result")
                        or data.get("text")
                        or str(data)
                    )
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="result-header">📄 Summary</div>
                            {summary_text}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<span class="status-pill status-error">Error - status {status_code}</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                        <div class="result-card">
                            {data}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            except requests.exceptions.ConnectionError:
                st.error("Could not reach the server. Make sure PUBLIC_URL is correct and the server is running.")
            except requests.exceptions.Timeout:
                st.error("The request took too long. Please try again.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.markdown(
    '<div style="text-align:center; margin-top:2rem; color:#5c5d68; font-size:0.8rem;">'
    "Local GUI • Powered by your summarize API</div>",
    unsafe_allow_html=True,
)