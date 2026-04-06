import streamlit as st
import os, re, string

st.set_page_config(
    page_title="TMDB Movie Search Engine",
    page_icon="🎬",
    layout="wide",
)

st.markdown("""
<style>
.title     { font-size: 2.4rem; font-weight: 900; text-align: center; color: #f59e0b; }
.subtitle  { text-align: center; color: #94a3b8; margin-bottom: 2rem; }
.movie-card {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    border: 1px solid #334155; border-radius: 12px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.8rem;
}
.movie-title { font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.3rem; }
.movie-meta  { font-size: 0.78rem; color: #94a3b8; margin-bottom: 0.5rem; }
.movie-desc  { font-size: 0.84rem; color: #cbd5e1; line-height: 1.55; }
.badge       { display:inline-block; background:#1d4ed8; color:#bfdbfe;
               font-size:0.72rem; padding:2px 9px; border-radius:999px; margin-right:4px; }
.badge-r     { background:#854d0e; color:#fef3c7; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎬 TMDB Movie Search Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">NLP-powered inverted index search over 5,000+ movies</div>', unsafe_allow_html=True)

ROOT = os.path.dirname(__file__)

# Accept both filenames Kaggle may produce
CSV_CANDIDATES = [
    os.path.join(ROOT, "tmdb_5000_movies.csv"),
]

@st.cache_resource(show_spinner="Building search index…")
def build_index():
    import pandas as pd
    from collections import defaultdict

    csv_path = next((p for p in CSV_CANDIDATES if os.path.exists(p)), None)
    if csv_path is None:
        return None, None, None

    df = pd.read_csv(csv_path)

    # Normalise column names across different Kaggle CSV variants
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    title_col    = next((c for c in df.columns if "title"    in c), None)
    overview_col = next((c for c in df.columns if "overview" in c), None)
    rating_col   = next((c for c in df.columns if "vote_average" in c or "rating" in c), None)
    runtime_col  = next((c for c in df.columns if "runtime"  in c), None)
    date_col     = next((c for c in df.columns if "release_date" in c or "release" in c), None)

    if title_col is None:
        return None, None, "No title column found in CSV."

    df = df[[c for c in [title_col, overview_col, rating_col, runtime_col, date_col] if c]].copy()
    df = df.rename(columns={
        title_col:    "title",
        overview_col: "overview",
        rating_col:   "rating",
        runtime_col:  "runtime",
        date_col:     "release_date",
    })
    df["overview"]     = df.get("overview", "").fillna("")
    df["rating"]       = pd.to_numeric(df.get("rating", 0), errors="coerce").fillna(0)
    df["runtime"]      = pd.to_numeric(df.get("runtime", 0), errors="coerce").fillna(0).astype(int)
    df["release_date"] = df.get("release_date", "").astype(str).str[:4]
    df = df.reset_index(drop=True)

    # Try spaCy, fall back to regex tokeniser
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        def tokenize(text):
            return [t.lemma_.lower() for t in nlp(text) if not t.is_stop and not t.is_punct and t.is_alpha and len(t) > 1]
    except Exception:
        STOP = {"the","a","an","and","or","of","in","to","for","is","are","was","were",
                "with","it","its","on","at","by","as","be","this","that","from","have","has","he","she","they"}
        def tokenize(text):
            toks = re.sub(r"[^a-z\s]", "", text.lower()).split()
            return [t for t in toks if t not in STOP and len(t) > 1]

    index = defaultdict(set)
    for i, row in df.iterrows():
        for tok in tokenize(str(row["title"]) + " " + str(row.get("overview", ""))):
            index[tok].add(i)

    return df, dict(index), None

df, index, err = build_index()

# ── search logic ──────────────────────────────────────────────────────────────
def search(query, df, index, top_k=12):
    STOP = {"the","a","an","and","or","of","in","to","for","is","are","was","were","with"}
    tokens = [t.lower().strip(string.punctuation) for t in query.split()
              if t.lower() not in STOP and len(t) > 1]
    if not tokens:
        return []
    counts = {}
    for tok in tokens:
        # exact match
        for idx in index.get(tok, set()):
            counts[idx] = counts.get(idx, 0) + 2
        # prefix match
        for key in index:
            if key.startswith(tok) and key != tok:
                for idx in index[key]:
                    counts[idx] = counts.get(idx, 0) + 1
    ranked = sorted(counts, key=lambda x: (-counts[x], -float(df.loc[x, "rating"])))
    return ranked[:top_k]

# ── UI ─────────────────────────────────────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])
with col_q:
    query = st.text_input("", placeholder="🔍  e.g. space adventure robot, romantic paris, horror ghost house", label_visibility="collapsed")
with col_btn:
    go = st.button("Search", type="primary", use_container_width=True)

st.markdown("**Try:** " + "  ·  ".join(f"`{q}`" for q in ["space adventure","dark knight","romantic comedy","horror house","heist detective","war hero"]))

if df is None and err is None:
    st.warning("""
**Dataset not found.** Place `tmdb_5000_movies.csv` in the project root:

```
tmdb-movie-search-engine/
└── tmdb_5000_movies.csv   ← put it here
└── streamlit_app.py
```

Download from Kaggle: [tmdb/tmdb-movie-metadata](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
    """)
elif err:
    st.error(f"Error loading dataset: {err}")
elif go or query:
    if not query.strip():
        st.warning("Enter a search query.")
    else:
        results = search(query, df, index, top_k=12)
        if not results:
            st.info(f'No results for **"{query}"**. Try broader keywords.')
        else:
            st.markdown(f"**{len(results)} results** for **\"{query}\"**")
            cols = st.columns(2)
            for i, idx in enumerate(results):
                row = df.loc[idx]
                year    = str(row.get("release_date", ""))[:4] or "N/A"
                rating  = f"{float(row.get('rating', 0)):.1f}" if row.get("rating") else "N/A"
                runtime = f"{int(row.get('runtime', 0))} min"  if row.get("runtime") else "N/A"
                overview = str(row.get("overview", ""))
                overview = overview[:230] + "…" if len(overview) > 230 else overview
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <div class="movie-title">{row['title']}</div>
                        <div class="movie-meta">
                            <span class="badge">{year}</span>
                            <span class="badge badge-r">⭐ {rating}</span>
                            <span class="badge">{runtime}</span>
                        </div>
                        <div class="movie-desc">{overview}</div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("**About:** Python NLP search engine using a TF-weighted inverted index over the TMDB 5,000 movie dataset. spaCy handles stop-word removal and lemmatisation.")
