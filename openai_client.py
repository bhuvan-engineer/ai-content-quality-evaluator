import os
import streamlit as st
from openai import OpenAI

def get_api_key():
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        secret_key = ""
    return secret_key or os.getenv("OPENAI_API_KEY", "")

def get_client():
    key = get_api_key()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Locally, add it to a .env file. "
            "On Streamlit Community Cloud, add it in App settings → Secrets."
        )
    return OpenAI(api_key=key)

def generate_content(system_prompt, user_prompt, model="gpt-4o-mini", temperature=0.4, max_tokens=500):
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("The model returned an empty response.")
    return content.strip()
