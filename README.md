# AI Content Quality Evaluation & Multilingual Prompt Testing

A Streamlit web app for generating and reviewing AI-written content in English, Hindi, and Hinglish. It includes prompt templates, lightweight heuristic checks, and a side-by-side multilingual experiment workflow.

## Features

- Generate emails, blog introductions, and social media posts
- Choose English, Hindi, or Hinglish
- Try zero-shot, few-shot, role-based, and constraint-based prompting
- Adjust tone, target audience, temperature, and response length
- Run a multilingual comparison for the same topic
- Review simple structure/length/filler checks
- Export generated content as TXT and experiment results as CSV

## Tech stack

- Python
- Streamlit
- OpenAI Python SDK / Chat Completions API
- pandas

## Run locally

1. Install Python 3.10 or newer.
2. Clone/download this repository and open a terminal in the project folder.
3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Activate it:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create `.env` from `.env.example` and add your own OpenAI API key. The app reads environment variables and Streamlit secrets. If using `.env`, load it before launch with your shell or add `from dotenv import load_dotenv; load_dotenv()` at the top of `app.py` (see note below).

   **Easy .env setup:** this repository includes `python-dotenv`; add these two lines near the top of `app.py` if you want automatic `.env` loading:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

The app opens in your browser, usually at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Sign in to Streamlit Community Cloud and choose **Create app**.
3. Select the repository, branch, and `app.py` as the main file.
4. In the app's **Settings → Secrets**, add:

   ```toml
   OPENAI_API_KEY = "your_real_api_key_here"
   ```

5. Deploy. Do not put your real API key in source code, README, screenshots, or a public GitHub commit.

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial AI content quality evaluator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Create an empty repository on GitHub first, then replace the remote URL with your own repository URL.

## How the evaluation works

The current evaluator checks:
- approximate word-count ranges
- basic content-type structure (e.g., greeting and closing for email)
- a small list of common filler phrases
- a reminder that factual accuracy needs human review

These are **heuristics**, not a validated quality score or fact-checking system. They do not prove that content is correct, unbiased, culturally appropriate, or safe. For formal evaluation, use a documented human-rating rubric and multiple runs per language.

## Privacy and costs

Prompts are sent to the configured OpenAI API for generation. This version does not intentionally save content to a database, but the hosting platform and API provider may process operational logs under their own policies. Do not enter sensitive or confidential information. API use may incur charges depending on your account and model.

## Project structure

```text
ai-content-quality-evaluator/
├── app.py
├── prompts/
│   ├── __init__.py
│   └── templates.py
├── evaluation/
│   ├── __init__.py
│   └── heuristics.py
├── utils/
│   ├── __init__.py
│   └── openai_client.py
├── .streamlit/
│   └── config.toml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Future improvements

- Human rating forms and inter-rater agreement
- Repeated-run experiments and summary charts
- LLM-as-a-judge calibrated against human ratings
- Retrieval-augmented generation (RAG) for trusted reference material
- Additional Indian languages and culture-specific checks
