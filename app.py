from flask import Flask, render_template, request, jsonify
import json, re, nltk, torch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# --- Load NASA data ---
with open("nasa_articles2.json", encoding="utf-8") as f:
    ARTICLES = json.load(f)
print(f"✅ Loaded {len(ARTICLES)} NASA research summaries.")

# --- Ensure NLTK ---
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

STOPWORDS = set(stopwords.words('english'))

# --- Load model ---
print("🔍 Loading SentenceTransformer model...")
model = SentenceTransformer('all-MiniLM-L12-v2')
summaries = [a["summary"] for a in ARTICLES]
embeddings = model.encode(summaries, convert_to_tensor=True)
print("✅ Model and embeddings ready.")


def extract_section(summary, section_keywords):
    """
    Extracts the text that starts after a keyword (e.g., 'Knowledge Gaps:')
    until the next section or end of summary.
    """
    pattern = rf"({'|'.join(section_keywords)}):([\s\S]*?)(?=(?:Impacts|Results|Areas_of Scientific Progress|Knowledge Gaps|Areas_of Consensus or Disagreement|Actionable Insights to Mission Planners):|$)"
    match = re.search(pattern, summary, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return None


@app.route("/")
def home():
    print("✅ Homepage loaded")
    return render_template("home.html")


@app.route("/nasa")
def nasa():
    print("✅ NASA bot page loaded")
    return render_template("index1.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_data = request.get_json()
    query = user_data.get("query", "").strip()
    if not query:
        return jsonify({"title": "", "summary": "Please enter a question."})

    # --- Find best article semantically ---
    query_embedding = model.encode(query, convert_to_tensor=True)
    sims = util.pytorch_cos_sim(query_embedding, embeddings)[0]
    idx = torch.argmax(sims).item()
    score = sims[idx].item()
    best = ARTICLES[idx]
    print(f"🔍 Best match: {best['title']} (score={score:.3f})")

    if score < 0.3:
        return jsonify({"title": "", "summary": "No relevant NASA summary found."})

    # --- Detect if user wants a specific section ---
    section_map = {
        "impact": ["Impact", "Impacts"],
        "result": ["Result", "Results"],
        "knowledge": ["Knowledge Gaps"],
        "progress": ["Areas_of Scientific Progress"],
        "consensus": ["Areas_of Consensus or Disagreement"],
        "insight": ["Actionable Insights to Mission Planners"]
    }

    for key, section_list in section_map.items():
        if key in query.lower():
            section = extract_section(best["summary"], section_list)
            if section:
                return jsonify({
                    "title": f"{best['title']} — {section_list[0]}",
                    "summary": section
                })

    # --- Default full summary ---
    return jsonify({"title": best["title"], "summary": best["summary"]})


if __name__ == "__main__":
    app.run(debug=True)
