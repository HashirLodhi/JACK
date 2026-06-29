import os
from dotenv import load_dotenv
from groq import Groq
from exa_py import Exa
from flask import Flask, request, jsonify, render_template, send_from_directory
from threading import Thread

load_dotenv()

# Clear proxy environment variables that may interfere with Groq client
for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(var, None)

# Initialize Groq client with safe error handling
groq_init_error = None
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=60.0)
except Exception as e:
    groq_client = None
    groq_init_error = str(e)

groq_model = "llama-3.3-70b-versatile"

# Initialize Exa client with safe error handling
try:
    exa_client = Exa(api_key=os.getenv("EXA_API"))
except Exception as e:
    exa_client = None
    print(f"Exa client initialization failed: {e}")

app = Flask(__name__, static_folder='static', template_folder='templates')


def generate_verification_query(text, speaker):
    prompt = f"""Someone said: "{text}"

The speaker is: {speaker}

Generate a specific, concise search query that would verify if this statement is factually true or false. The query should be specific enough to fact-check this exact claim. Return ONLY the search query, nothing else."""
    if not groq_client:
        return f"Error: Groq client initialization failed – {groq_init_error}"
    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model=groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt == 2:
                return f"Error generating query: {e}"
            import time; time.sleep(2)


def search_with_exa(query):
    if not exa_client:
        return "Error: Exa client not initialized. Check EXA_API environment variable."
    try:
        response = exa_client.search(
            query=query,
            num_results=10,
            type="neural"
        )
        sources = []
        for result in response.results:
            # Safely extract fields; some Result objects may not have an 'author' attribute.
            title = getattr(result, "title", "No title")
            url = getattr(result, "url", "")
            text = getattr(result, "text", "")
            # Truncate text for brevity
            snippet = text[:500] if text else ""
            sources.append({
                "title": title,
                "url": url,
                "text": snippet,
                # Include author if available for downstream use
                "author": getattr(result, "author", None)
            })
        return sources
    except Exception as e:
        return f"Error searching: {e}"


def agent_claim_made(claim, speaker, sources):
    sources_text = "\n\n".join([
        f"Source {i+1}: {s['title']}\nURL: {s['url']}\nContent: {s['text']}"
        for i, s in enumerate(sources)
    ])
    source_refs = "\n".join([f"Source {i+1}: [{s['title']}]({s['url']})" for i, s in enumerate(sources)])
    prompt = f"""Based on the verification sources below, answer ONLY this question:

CLAIM: "{claim}"
SPEAKER: {speaker}

SOURCES:
{sources_text}

## 1. Was this claim made by the sayer?
[Answer based on sources - did this person actually make this statement? Provide a clear, evidence-based answer with specific citations. 
IMPORTANT: Inline cite sources using markdown links like this: "According to [Source 1](URL), ..." or "As stated in [Source 2](URL), ..."
Use the exact source titles and URLs from this reference list:
{source_refs}]"""
    if not groq_client:
        return f"Error: Groq client initialization failed – {groq_init_error}"
    try:
        response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


def agent_action_done(claim, speaker, sources):
    sources_text = "\n\n".join([
        f"Source {i+1}: {s['title']}\nURL: {s['url']}\nContent: {s['text']}"
        for i, s in enumerate(sources)
    ])
    source_refs = "\n".join([f"Source {i+1}: [{s['title']}]({s['url']})" for i, s in enumerate(sources)])
    prompt = f"""Based on the verification sources below, answer ONLY this question:

CLAIM: "{claim}"
SPEAKER: {speaker}

SOURCES:
{sources_text}

## 2. Was this action/event done by the sayer?
[Answer based on sources - did the person actually do what they claimed? Provide a clear, evidence-based answer with specific citations. 
IMPORTANT: Inline cite sources using markdown links like this: "According to [Source 1](URL), ..." or "As stated in [Source 2](URL), ..."
Use the exact source titles and URLs from this reference list:
{source_refs}]"""
    try:
        response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


def agent_consequences(claim, speaker, sources):
    sources_text = "\n\n".join([
        f"Source {i+1}: {s['title']}\nURL: {s['url']}\nContent: {s['text']}"
        for i, s in enumerate(sources)
    ])
    source_refs = "\n".join([f"Source {i+1}: [{s['title']}]({s['url']})" for i, s in enumerate(sources)])
    prompt = f"""Based on the verification sources below, answer ONLY this question:

CLAIM: "{claim}"
SPEAKER: {speaker}

SOURCES:
{sources_text}

## 3. What were the consequences of this act/statement?
[Detail the consequences, outcomes, or impact based on sources. Provide a clear, evidence-based answer with specific citations. 
IMPORTANT: Inline cite sources using markdown links like this: "According to [Source 1](URL), ..." or "As stated in [Source 2](URL), ..."
Use the exact source titles and URLs from this reference list:
{source_refs}]"""
    try:
        response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


def agent_sources(sources):
    prompt = f"""Format these sources as clickable markdown links, one per line:

SOURCES:
{chr(10).join([f"{i+1}. {s['title']} - {s['url']}" for i, s in enumerate(sources)])}

Return ONLY the markdown list, nothing else."""
    try:
        response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "\n".join([f"- [{s['title']}]({s['url']})" for s in sources])


def verify_claim(text, speaker):
    if not text or not speaker:
        return "Please provide both claim and speaker name."

    query = generate_verification_query(text, speaker)
    if query.startswith("Error"):
        return query

    sources = search_with_exa(query)
    if isinstance(sources, str) and sources.startswith("Error"):
        return sources
    if not sources:
        return "No sources found for verification."

    part1 = agent_claim_made(text, speaker, sources)
    part2 = agent_action_done(text, speaker, sources)
    part3 = agent_consequences(text, speaker, sources)
    part4 = agent_sources(sources)

    return f"""## 1. Was this claim made by the sayer?
{part1}

## 2. Was this action/event done by the sayer?
{part2}

## 3. What were the consequences of this act/statement?
{part3}

## Sources
{part4}"""


def simple_query(question):
    if not question:
        return "Please provide a question."

    if not exa_client:
        return "Error: Exa client not initialized. Check EXA_API environment variable."

    try:
        response = exa_client.search(
            query=question,
            num_results=5,
            type="neural"
        )
        sources = []
        for result in response.results:
            title = getattr(result, "title", "No title")
            url = getattr(result, "url", "")
            text = getattr(result, "text", "")
            snippet = text[:500] if text else ""
            sources.append({
                "title": title,
                "url": url,
                "text": snippet
            })
    except Exception as e:
        return f"Error searching: {e}"

    if not sources:
        return "No sources found for your question."

    sources_text = "\n\n".join([
        f"Source {i+1}: {s['title']}\nURL: {s['url']}\nContent: {s['text']}"
        for i, s in enumerate(sources)
    ])
    source_refs = "\n".join([f"Source {i+1}: [{s['title']}]({s['url']})" for i, s in enumerate(sources)])

    prompt = f"""Answer the following question based on the sources below. Provide a clear, concise answer with inline citations using markdown links like: "According to [Source 1](URL), ..."

QUESTION: {question}

SOURCES:
{sources_text}

REFERENCE LIST:
{source_refs}"""

    if not groq_client:
        return f"Error: Groq client initialization failed – {groq_init_error}"

    try:
        response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800
        )
        answer = response.choices[0].message.content.strip()
        source_links = "\n".join([f"- [{s['title']}]({s['url']})" for s in sources])
        return f"{answer}\n\n## Sources\n{source_links}"
    except Exception as e:
        return f"Error: {e}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def api_verify():
    data = request.get_json()
    claim = data.get('claim', '')
    speaker = data.get('speaker', '')
    
    if not claim or not speaker:
        return jsonify({'error': 'Please provide both claim and speaker name.'}), 400
    
    query = generate_verification_query(claim, speaker)
    if query.startswith("Error"):
        return jsonify({'error': query}), 500
    
    sources = search_with_exa(query)
    if isinstance(sources, str) and sources.startswith("Error"):
        return jsonify({'error': sources}), 500
    
    if not sources:
        return jsonify({'error': 'No sources found for verification.'}), 404
    
    part1 = agent_claim_made(claim, speaker, sources)
    part2 = agent_action_done(claim, speaker, sources)
    part3 = agent_consequences(claim, speaker, sources)
    part4 = agent_sources(sources)
    
    result = f"""## 1. Was this claim made by the sayer?
{part1}

## 2. Was this action/event done by the sayer?
{part2}

## 3. What were the consequences of this act/statement?
{part3}

## Sources
{part4}"""
    
    return jsonify({
        'result': result,
        'sources': sources
    })

@app.route('/api/search-query', methods=['POST'])
def api_search_query():
    data = request.get_json()
    claim = data.get('claim', '')
    speaker = data.get('speaker', '')
    
    if not claim or not speaker:
        return jsonify({'error': 'Please provide both claim and speaker name.'}), 400
    
    query = generate_verification_query(claim, speaker)
    if query.startswith("Error"):
        return jsonify({'error': query}), 500
    
    return jsonify({'query': query})


@app.route('/api/query', methods=['POST'])
def api_query():
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Please provide a question.'}), 400
    
    result = simple_query(question)
    if result.startswith("Error"):
        return jsonify({'error': result}), 500
    
    return jsonify({'result': result})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)