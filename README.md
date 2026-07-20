# 🎬 YouTube AI Summarizer

An end-to-end project that takes any YouTube video URL, pulls its transcript, and generates a clean AI-powered summary of the video content — with a professional local GUI to interact with it.

The project is split into two parts:
1. **Backend (Kaggle Notebook)** — runs the summarization model and exposes it as a public API using ngrok.
2. **Frontend (Local `.py` file)** — a Streamlit GUI that runs on your own machine and talks to the backend.

---

## 🧠 How it works

1. A YouTube URL is submitted (either via the API directly or through the local GUI).
2. The backend extracts the video ID and fetches its transcript using `youtube-transcript-api`.
3. The transcript is cleaned (extra whitespace and repeated words from auto-generated captions are removed).
4. The transcript is split into chunks of complete sentences (not cut mid-sentence) to respect the model's token limit.
5. Each chunk is summarized individually using `facebook/bart-large-cnn`.
6. The individual summaries are combined, deduplicated, and — if long enough — summarized once more into a final, coherent summary.
7. The final summary is returned as JSON through a FastAPI endpoint, exposed publicly via ngrok.
8. The local Streamlit app calls that public endpoint and displays the result in a clean, styled interface.

---

## 🏗️ Architecture

- **Model**: `facebook/bart-large-cnn` (English-only summarization)
- **Transcript source**: `youtube-transcript-api`
- **Backend framework**: FastAPI + Uvicorn
- **Public tunnel**: pyngrok
- **Frontend**: Streamlit (runs locally)

---

## 📁 Project structure
---

## 🚀 Getting started

### Step 1 — Run the backend on Kaggle

> ⚠️ The backend **must be run on Kaggle first** (or any environment with GPU access), since it loads a transformer model and needs a public URL to be reachable from your local machine.

1. Open the notebook (`youtube_summarizer_backend.ipynb`) in a new Kaggle Notebook.
2. Enable GPU: **Settings → Accelerator → GPU**.
3. Get a free ngrok auth token from [ngrok.com](https://ngrok.com) and paste it into the `NGROK_TOKEN` variable in the notebook.
4. Run all cells in order, top to bottom.
5. At the end, the notebook will print a public URL, e.g.:
6. Keep the Kaggle notebook **running** — the API only stays alive as long as the notebook session is active.

### Step 2 — Run the GUI locally

1. Clone this repository:
```bash
   git clone <repo-url>
   cd <repo-folder>
```
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Open `app.py` and set the two constants at the top to match your Kaggle session:
```python
   API_KEY = "your-api-key"          # same value as API_KEY in the notebook
   PUBLIC_URL = "https://xxxx.ngrok-free.app"   # the URL printed by the notebook
```
4. Run the app:
```bash
   streamlit run app.py
```
5. Your browser will open automatically at `localhost:8501`. Paste a YouTube URL and click **Summarize video**.

---

## 🔌 API reference

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "running",
  "model": "facebook/bart-large-cnn"
}
```

### `POST /summarize`
Summarizes a YouTube video from its transcript.

**Headers:**
**Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Success response (200):**
```json
{
  "status": "success",
  "summary": "..."
}
```

**Client error (400)** — invalid URL, no English transcript, empty transcript, or video too long.

**Server error (500)** — unexpected failure.

---

## ⚠️ Known limitations

- **English-only**: the model does not support Arabic or other languages. Videos without an English transcript will return a clear error instead of crashing.
- **Video length cap**: very long videos are rejected to avoid excessive processing time (configurable via `MAX_CHUNKS`).
- **Session-dependent**: since the backend runs on a Kaggle notebook, the public URL becomes invalid once the notebook session stops or restarts — you'll need to re-run it and update `PUBLIC_URL` in the local app.
- **Ngrok free tier limits**: the free plan allows a limited number of simultaneous tunnels per account. If you hit `ERR_NGROK_324`, call `ngrok.kill()` before starting a new tunnel, or close old sessions from the [ngrok dashboard](https://dashboard.ngrok.com/agents).

---

## 🛠️ Tech stack

| Component | Technology |
|---|---|
| Summarization model | `facebook/bart-large-cnn` (Hugging Face Transformers) |
| Transcript fetching | `youtube-transcript-api` |
| Backend API | FastAPI + Uvicorn |
| Public tunneling | pyngrok |
| Frontend GUI | Streamlit |
| Hosting (backend) | Kaggle Notebooks (GPU) |

---

## 📌 Future improvements

- Support additional languages via a multilingual model (e.g. an instruction-tuned LLM).
- Filter out sponsor/ad segments from transcripts before summarizing.
- Add caching so re-summarizing the same video doesn't reprocess from scratch.
- Deploy the backend on a persistent server instead of a notebook session.
