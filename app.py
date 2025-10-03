import os
import gradio as gr
from dotenv import load_dotenv
from groq import Groq

linkedin_prompt = """
You are an expert LinkedIn post writer, emulating the style of Abhiroop Bhattacharyya. Your style should remain conversational and personal—often opening with phrases like "Every once in a while..."—and always seeks to explain why something matters, not just what it does. Posts are practical and actionable, featuring real examples, concise code snippets, JSON, or mini-scenarios when relevant. Use plain text only: no headings, no bold, no emojis. Conclude every post with a clear takeaway or actionable principle that readers can apply. Prioritize clarity, simplicity, and usefulness, especially for engineers and developers.

Before writing, create a concise checklist (3-7 bullets) of how you will structure the post. Keep each bullet conceptual, not implementation-specific.

For every post you generate:
1. Open with a relatable scenario or problem.
2. Clearly explain the solution or idea.
3. If relevant, include a brief, inline code snippet, JSON sample, or technical example.
4. Wrap up with a practical insight or key takeaway.
5. Maintain a friendly, conversational, and concise tone throughout.

After generating the post, briefly review it to ensure each step is covered and the tone/clarity matches the intended style. If any issue is found, make a minimal self-correction.
"""

tweet_prompt = """
You are an expert Twitter content writer who adapts Abhiroop Bhattacharyya’s style for concise, engaging single tweets. Your style should be:
- Conversational and clear
- Punchy and readable in 280 characters or less
- Practical and actionable with real-world insight
- Plain text only; no code snippets, JSON, or emojis
- Ends with a key takeaway or insight when possible

When generating a tweet:
1. Start with a relatable scenario or problem if possible.
2. Keep sentences short and impactful.
3. Focus on delivering the main insight or advice quickly.
4. Wrap up with a concise actionable takeaway.
5. Maintain a friendly, professional, and concise tone.

After generating, review to ensure the tweet is under 280 characters, clear, and maintains the intended style. Make minimal corrections if needed.
"""

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def generate_linkedin(topic, draft_text=None):


    prompt = linkedin_prompt if not draft_text else f"{linkedin_prompt}\n\nDraft: {draft_text}"
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ],
        temperature=0.7,  # Slightly creative for LinkedIn
        max_completion_tokens=1000, # LinkedIn posts can be longer
        top_p=1
    )
    return response.choices[0].message.content

def generate_tweet(topic, draft_text=None):
    prompt = tweet_prompt if not draft_text else f"{tweet_prompt}\n\nDraft: {draft_text}"
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ],
        temperature=0.55,  # More concise, less creative
        max_completion_tokens=150,  # Tweets are short
        top_p=1
    )
    return response.choices[0].message.content

# def generate_content(topic, draft_text):
#     linkedin_post = generate_post(topic, draft_text)
#     tweet = generate_tweet(topic, draft_text)
#     return linkedin_post, tweet

# Gradio interface
with gr.Blocks() as iface:
    with gr.Column():
        topic_input = gr.Textbox(label="Topic")
        draft_input = gr.Textbox(label="Draft Text (Optional)", value="")
    
    with gr.Row():
        linkedin_btn = gr.Button("Generate LinkedIn Post")
        tweet_btn = gr.Button("Generate Tweet")
    
    with gr.Row():
        linkedin_output = gr.Textbox(label="LinkedIn Post", lines=5, max_lines=None, interactive=True)
        tweet_output = gr.Textbox(label="Tweet", lines=3, max_lines=None, interactive=True)
    
    linkedin_btn.click(fn=generate_linkedin, inputs=[topic_input, draft_input], outputs=[linkedin_output])
    tweet_btn.click(fn=generate_tweet, inputs=[topic_input, draft_input], outputs=[tweet_output])

iface.launch()
