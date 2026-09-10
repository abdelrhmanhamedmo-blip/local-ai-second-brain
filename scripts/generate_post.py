#!/usr/bin/env python3
import requests
import json
import os

# 1. إعدادات Ollama المحلية
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def generate_linkedin_post(topic):
    prompt = f"""
    You are an expert Tech Content Creator and MLOps Engineer.
    Write an engaging, professional LinkedIn post about the following topic:
    "{topic}"

    Requirements:
    - Use clear structure with bullet points and emojis.
    - Highlight the technical stack (Linux, Cybersecurity, DevOps, Local AI).
    - Include a strong Call to Action.
    - Output language: English.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

if __name__ == "__main__":
    topic_input = input("Enter a topic or project update for your LinkedIn post: ")
    print("\n[+] Generating post using local Ollama model...\n")
    post_content = generate_linkedin_post(topic_input)
    
    print("=" * 50)
    print(post_content)
    print("=" * 50)
    
    # التأكد من وجود مجلد docs تلقائياً
    os.makedirs("docs", exist_ok=True)
    
    # حفظ النتيجة في ملف نصي جاهز للنشر
    with open("docs/draft_post.txt", "w", encoding="utf-8") as f:
        f.write(post_content)
    print("\n[✔] Draft saved to docs/draft_post.txt")
