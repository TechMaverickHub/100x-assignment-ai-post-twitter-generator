import gradio as gr
from groq import Groq
import time
import os
from dotenv import load_dotenv

load_dotenv()
# -------------------------
# Initialize Groq Client
# -------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # replace with your env var

# -------------------------
# Step 1: Ask Targeted Questions
# -------------------------
def ask_targeted_questions(topic, draft):
    if not topic:
        return "⚠️ Please enter a topic first."

    return f"""
You're writing about **{topic}**.
Before we generate, please clarify:

1️⃣ Who is your audience? (e.g., developers, founders, students)
2️⃣ What tone should the post have? (e.g., storytelling, technical, inspirational)
3️⃣ What’s your main goal? (e.g., share insight, promote project, provoke thought)
4️⃣ Any hashtags, links, or CTAs to include?

Type your answers below ⬇️
"""

# -------------------------
# Streaming Response Generator
# -------------------------
def stream_groq_response(prompt, topic, max_tokens=800, temperature=0.7, model="openai/gpt-oss-20b"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        stream=True
    )
    for chunk in response:
        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# -------------------------
# Step 2A: Generate LinkedIn Post (Streaming)
# -------------------------
def generate_linkedin_post(topic, draft, answers, progress=gr.Progress(track_tqdm=True)):
    if not topic:
        yield "⚠️ Topic is required.", ""
        return

    prompt = f"""
You are a professional LinkedIn content strategist.
Write a high-quality, scroll-stopping LinkedIn post.

Details:
- Topic: {topic}
- User draft: {draft}
- User answers/context: {answers}

Guidelines:
- 2–4 short paragraphs
- Clear line breaks
- Authentic, human tone
- Actionable insight + soft CTA at the end

Output only the LinkedIn post.
"""
    post = ""
    score = "Calculating..."  # placeholder
    yield post, score  # initial output

    for chunk in stream_groq_response(prompt, topic, max_tokens=800):
        post += chunk
        yield post, score

    # After streaming ends, compute engagement score
    score = evaluate_engagement(post)
    yield post, score

# -------------------------
# Step 2B: Generate Tweet (Streaming)
# -------------------------
def generate_tweet(topic, draft, answers):
    if not topic:
        yield "⚠️ Topic is required.", ""
        return

    prompt = f"""
You are a viral Twitter copywriter.
Write a catchy, insightful tweet.

Details:
- Topic: {topic}
- Draft: {draft}
- Context: {answers}

Guidelines:
- ≤ 280 chars
- Add 2–3 hashtags
- Tone: witty or wise
- Must feel scroll-stopping

Output only the tweet.
"""

    tweet = ""
    score = "Calculating..."  # placeholder
    yield tweet, score  # initial output

    for chunk in stream_groq_response(prompt, topic, max_tokens=300, model="llama-3.1-8b-instant"):
        tweet += chunk
        yield tweet, score

    # After streaming finishes, compute engagement
    score = evaluate_engagement(tweet)
    yield tweet, score  # final update with score


# -------------------------
# Step 3: Evaluate Engagement Score
# -------------------------
def evaluate_engagement(text):
    """Ask model to rate engagement 1–10 with short explanation."""
    if not text.strip():
        return "⚠️ No content generated yet."

    text = text[:500] # For LinkedIn posts, maybe only send the first 400–500 characters to the engagement scorer
    prompt = f"""
You are a social media strategist.
Evaluate the engagement potential (1–10) of this content based on:
- Hook strength
- Clarity
- Emotional pull
- Shareability
- Authentic tone

Text:
{text}

Respond as:
"Score: X/10 — short explanation"
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.4,
            max_completion_tokens=50,
            top_p=1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Engagement scoring failed:", e)
        return "⚠️ Could not calculate score"

# -------------------------
# Gradio UI
# -------------------------
with gr.Blocks(title="AI LinkedIn + Tweet Generator (Groq, Streaming)") as demo:
    gr.Markdown("## 🚀 AI LinkedIn + Tweet Generator\n### Powered by Groq + Llama 3.1\nCreate viral-ready posts and tweets, streamed in real-time.")

    # Topic & Draft Inputs
    with gr.Row():
        topic = gr.Textbox(label="🧠 Topic", placeholder="e.g., The future of AI in education")
        draft = gr.Textbox(label="📝 Optional Draft", placeholder="Paste your notes or rough idea...")

    # Accordion for constant targeted questions
    with gr.Accordion("🎯 Targeted Questions (Click to View)", open=True):
        gr.Markdown("""
1️⃣ Who is your audience? (e.g., developers, founders, students)  
2️⃣ What tone should the post have? (e.g., storytelling, technical, inspirational)  
3️⃣ What’s your main goal? (e.g., share insight, promote project, provoke thought)  
4️⃣ Any hashtags, links, or CTAs to include?
""")
        answers_box = gr.Textbox(label="✍️ Your Answers", placeholder="Type your answers here...", lines=5)

    # Side-by-side Layout: LinkedIn (Left) & Tweet (Right)
    with gr.Row():
        # LinkedIn Column
        with gr.Column():
            post_btn = gr.Button("Generate LinkedIn Post 🚀")
            linkedin_output = gr.Textbox(label="📄 LinkedIn Post", lines=10)
            linkedin_score = gr.Textbox(label="📊 Engagement Score (Post)")

        # Tweet Column
        with gr.Column():
            tweet_btn = gr.Button("Generate Tweet 🐦")
            tweet_output = gr.Textbox(label="🐦 Tweet", lines=5)
            tweet_score = gr.Textbox(label="📊 Engagement Score (Tweet)")

    # Button Click Events
    post_btn.click(
        generate_linkedin_post,
        inputs=[topic, draft, answers_box],
        outputs=[linkedin_output, linkedin_score]
    )

    tweet_btn.click(
        generate_tweet,
        inputs=[topic, draft, answers_box],
        outputs=[tweet_output, tweet_score]
    )

if __name__ == "__main__":
    demo.launch()
