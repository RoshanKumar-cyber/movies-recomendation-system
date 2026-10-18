<<<<<<< HEAD
"""CinePick — a Streamlit interface for the notebook's content-based movie recommender."""

from pathlib import Path
import os
import pickle
import ast

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
MOVIE_FILE = BASE_DIR / "movie_list.pkl"
SIMILARITY_FILE = BASE_DIR / "similarity.pkl"
MOVIES_CSV = BASE_DIR / "tmdb_5000_movies.csv"
CREDITS_CSV = BASE_DIR / "tmdb_5000_credits.csv"

st.set_page_config(
    page_title="CinePick · Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: radial-gradient(ellipse at 80% -10%, #31205c 0%, transparent 38%), #0b0b12; color: #f6f4fb; }
.block-container { max-width: 1450px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #11111b; border-right: 1px solid #272536; }
.brand { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.5rem; letter-spacing: -.06em; }
.brand span { color: #b7a0ff; }
.eyebrow { color: #b7a0ff; font-size: .74rem; font-weight: 700; text-transform: uppercase; letter-spacing: .18em; }
.hero { padding: 2rem 0 1.2rem; }
.hero h1 { font-family: 'Space Grotesk', sans-serif; font-size: clamp(2.4rem, 5vw, 4.7rem); line-height: 1.03; letter-spacing: -.065em; margin: .55rem 0 1rem; }
.hero h1 em { color: #b7a0ff; font-style: normal; }
.subtle { color: #a6a4b5; font-size: 1.02rem; max-width: 650px; }
.panel { background: linear-gradient(135deg, rgba(32,29,48,.96), rgba(18,18,29,.96)); border: 1px solid #302b45; border-radius: 22px; padding: 1.2rem 1.35rem; }
.stat { color:#aaa7bd; font-size:.82rem; }
.stat strong { display:block; color:#fff; font-family:'Space Grotesk',sans-serif; font-size:1.45rem; margin-top:.2rem; }
.movie-card { background: #151520; border: 1px solid #2a2939; border-radius: 16px; padding: 1rem; min-height: 168px; height: 100%; transition: transform .2s, border-color .2s; }
.movie-card:hover { transform: translateY(-3px); border-color: #8e72ee; }
.movie-index { color:#b7a0ff; font-size:.72rem; font-weight:700; letter-spacing:.12em; }
.movie-title { font-family:'Space Grotesk',sans-serif; font-size:1.08rem; font-weight:700; line-height:1.25; margin:.55rem 0 .7rem; }
.score-track { background:#302b40; height:5px; border-radius:8px; overflow:hidden; margin:.45rem 0; }
.score-fill { background:linear-gradient(90deg,#8061e8,#c0a9ff); height:100%; border-radius:8px; }
.score-label { color:#b7b3c8; font-size:.76rem; }
.section-title { font-family:'Space Grotesk',sans-serif; font-size:1.55rem; font-weight:700; letter-spacing:-.04em; }
div.stButton > button { border-radius: 12px; font-weight: 700; border: 1px solid #7f65db; }
div.stButton > button[kind="primary"] { background: linear-gradient(100deg,#7856df,#9a7af2); color:white; }
.stSelectbox div[data-baseweb="select"] > div, .stTextInput input { background:#151520; border-color:#343047; border-radius:12px; }
hr { border-color:#292637; }
.footer { color:#777488; font-size:.78rem; padding-top:2rem; }
</style>
""",
    unsafe_allow_html=True,
)


def _convert_names(value):
    try:
        return [x.get("name", "") for x in ast.literal_eval(value)]
    except (ValueError, SyntaxError, TypeError):
        return []


def _convert_cast(value):
    return _convert_names(value)[:3]


def _directors(value):
    try:
        return [
            x.get("name", "")
            for x in ast.literal_eval(value)
            if x.get("job") == "Director"
        ]
    except (ValueError, SyntaxError, TypeError):
        return []


def build_model():
    """Build the same CountVectorizer/cosine-similarity model used in the notebook."""
    if not MOVIES_CSV.exists() or not CREDITS_CSV.exists():
        raise FileNotFoundError(
            "Dataset files not found. Add tmdb_5000_movies.csv and tmdb_5000_credits.csv beside app.py."
        )
    movies = pd.read_csv(MOVIES_CSV)
    credits = pd.read_csv(CREDITS_CSV)
    movies = movies.merge(credits, on="title")
    required = ["movie_id", "title", "genres", "keywords", "overview", "cast", "crew"]
    movies = movies[required].dropna().copy()
    movies["genres"] = movies["genres"].apply(_convert_names)
    movies["keywords"] = movies["keywords"].apply(_convert_names)
    movies["cast"] = movies["cast"].apply(_convert_cast)
    movies["crew"] = movies["crew"].apply(_directors)
    for col in ["genres", "keywords", "cast", "crew"]:
        movies[col] = movies[col].apply(
            lambda items: [name.replace(" ", "") for name in items if name]
        )
    movies["overview"] = movies["overview"].astype(str).apply(str.split)
    movies["tags"] = (
        movies["genres"]
        + movies["cast"]
        + movies["crew"]
        + movies["keywords"]
        + movies["overview"]
    )
    new_df = movies[["movie_id", "title", "tags"]].copy()
    new_df["tags"] = new_df["tags"].apply(lambda items: " ".join(items))
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = CountVectorizer(max_features=5000, stop_words="english")
    vectors = vectorizer.fit_transform(new_df["tags"]).toarray()
    similarity = cosine_similarity(vectors)
    with MOVIE_FILE.open("wb") as f:
        pickle.dump(new_df, f)
    with SIMILARITY_FILE.open("wb") as f:
        pickle.dump(similarity, f)
    return new_df, similarity


@st.cache_resource(show_spinner="Loading movie data and preparing recommendations…")
def load_model():
    if MOVIE_FILE.exists() and SIMILARITY_FILE.exists():
        try:
            with MOVIE_FILE.open("rb") as f:
                movie_df = pickle.load(f)
            with SIMILARITY_FILE.open("rb") as f:
                similarity = pickle.load(f)
            if len(movie_df) == len(similarity):
                return movie_df, similarity
        except (pickle.UnpicklingError, EOFError, AttributeError, ValueError):
            pass
    return build_model()


def recommend(title, movie_df, similarity, count=5):
    matches = movie_df.index[
        movie_df["title"].astype(str).str.casefold() == title.casefold()
    ].tolist()
    if not matches:
        return []
    index = matches[0]
    distances = sorted(
        enumerate(similarity[index]), key=lambda pair: pair[1], reverse=True
    )
    return [(movie_df.iloc[i], float(score)) for i, score in distances if i != index][
        :count
    ]


def movie_card(title, rank, score):
    pct = max(0, min(100, round(score * 100)))
    st.markdown(
        f"""<div class="movie-card"><div class="movie-index">MATCH {rank:02d}</div><div class="movie-title">{title}</div><div class="score-label">Similarity · {pct}%</div><div class="score-track"><div class="score-fill" style="width:{pct}%"></div></div><div class="score-label">Based on shared movie features</div></div>""",
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        '<div class="brand">cine<span>pick</span> ✦</div>', unsafe_allow_html=True
    )
    st.caption("YOUR PERSONAL MOVIE DISCOVERY ENGINE")
    st.markdown("---")
    st.markdown("**How it works**")
    st.write(
        "Choose a movie you like. CinePick compares its genres, keywords, cast, director and overview with other movies to find similar titles."
    )
    st.markdown("---")
    st.markdown("**Recommendation settings**")
    recommendation_count = st.slider(
        "Number of recommendations", min_value=3, max_value=10, value=5
    )
    st.caption("Powered by CountVectorizer + cosine similarity.")

st.markdown(
    '<div class="hero"><div class="eyebrow">✦ Your next favourite is waiting</div><h1>Less scrolling.<br><em>More cinema.</em></h1><p class="subtle">Discover films that match your taste. Pick a movie you love and let the recommendation engine find your next watch.</p></div>',
    unsafe_allow_html=True,
)

try:
    movie_df, similarity = load_model()
except Exception as exc:
    st.error("CinePick couldn't load the recommendation model.")
    st.markdown(
        "**How to fix it:** Put `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` in the same folder as `app.py`, then restart the app. If you already have `movie_list.pkl` and `similarity.pkl`, place those files beside `app.py` instead."
    )
    with st.expander("Technical details"):
        st.code(str(exc))
    st.stop()

movie_titles = movie_df["title"].astype(str).drop_duplicates().sort_values().tolist()
col_a, col_b = st.columns([3, 1])
with col_a:
    selected_movie = st.selectbox(
        "Find a movie to start with",
        movie_titles,
        index=(movie_titles.index("Batman") if "Batman" in movie_titles else 0),
        help="Start typing a movie title to search the dataset.",
    )
with col_b:
    st.markdown("<div style='height:29px'></div>", unsafe_allow_html=True)
    discover = st.button(
        "✦ Find similar movies", type="primary", use_container_width=True
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="panel"><div class="eyebrow">YOUR DISCOVERY STATS</div>',
    unsafe_allow_html=True,
)
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(
        f'<div class="stat">MOVIES IN LIBRARY<strong>{len(movie_titles):,}</strong></div>',
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        '<div class="stat">ENGINE<strong>Content-based</strong></div>',
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        '<div class="stat">MATCH METHOD<strong>Cosine similarity</strong></div>',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

if "last_movie" not in st.session_state:
    st.session_state.last_movie = None
if discover:
    st.session_state.last_movie = selected_movie

if st.session_state.last_movie:
    target = st.session_state.last_movie
    results = recommend(target, movie_df, similarity, recommendation_count)
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="eyebrow">BECAUSE YOU PICKED</div><div class="section-title">{target}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if results:
        st.markdown(
            '<div class="section-title">Your next watchlist ✦</div><p class="subtle" style="font-size:.9rem">Ranked by how closely each movie matches your selection.</p>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, (row, score) in enumerate(results):
            with cols[i % len(cols)]:
                movie_card(str(row["title"]), i + 1, score)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        with st.expander("View recommendation scores"):
            score_df = pd.DataFrame(
                [
                    {
                        "Rank": i + 1,
                        "Movie": str(row["title"]),
                        "Similarity": f"{score:.4f}",
                    }
                    for i, (row, score) in enumerate(results)
                ]
            )
            st.dataframe(score_df, hide_index=True, use_container_width=True)
    else:
        st.info("No recommendations found for this title. Try another movie.")
else:
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Ready for your next favourite?</div><p class="subtle" style="font-size:.92rem">Select any title above and click <b>Find similar movies</b> to get started.</p>',
        unsafe_allow_html=True,
    )
    examples = [
        "The Dark Knight",
        "Inception",
        "Interstellar",
        "The Avengers",
        "Avatar",
    ]
    examples = [x for x in examples if x in movie_titles]
    if examples:
        st.caption("Try one of these popular picks")
        example_cols = st.columns(len(examples))
        for col, example in zip(example_cols, examples):
            with col:
                if st.button(f"🎬 {example}", use_container_width=True):
                    st.session_state.last_movie = example
                    st.rerun()

st.markdown(
    '<div class="footer">CINEPICK · Made for movie lovers · Recommendations are generated from your local content-based model.</div>',
    unsafe_allow_html=True,
=======
"""CinePick — a Streamlit interface for the notebook's content-based movie recommender."""

from pathlib import Path
import os
import pickle
import ast

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
MOVIE_FILE = BASE_DIR / "movie_list.pkl"
SIMILARITY_FILE = BASE_DIR / "similarity.pkl"
MOVIES_CSV = BASE_DIR / "tmdb_5000_movies.csv"
CREDITS_CSV = BASE_DIR / "tmdb_5000_credits.csv"

st.set_page_config(
    page_title="CinePick · Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: radial-gradient(ellipse at 80% -10%, #31205c 0%, transparent 38%), #0b0b12; color: #f6f4fb; }
.block-container { max-width: 1450px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #11111b; border-right: 1px solid #272536; }
.brand { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.5rem; letter-spacing: -.06em; }
.brand span { color: #b7a0ff; }
.eyebrow { color: #b7a0ff; font-size: .74rem; font-weight: 700; text-transform: uppercase; letter-spacing: .18em; }
.hero { padding: 2rem 0 1.2rem; }
.hero h1 { font-family: 'Space Grotesk', sans-serif; font-size: clamp(2.4rem, 5vw, 4.7rem); line-height: 1.03; letter-spacing: -.065em; margin: .55rem 0 1rem; }
.hero h1 em { color: #b7a0ff; font-style: normal; }
.subtle { color: #a6a4b5; font-size: 1.02rem; max-width: 650px; }
.panel { background: linear-gradient(135deg, rgba(32,29,48,.96), rgba(18,18,29,.96)); border: 1px solid #302b45; border-radius: 22px; padding: 1.2rem 1.35rem; }
.stat { color:#aaa7bd; font-size:.82rem; }
.stat strong { display:block; color:#fff; font-family:'Space Grotesk',sans-serif; font-size:1.45rem; margin-top:.2rem; }
.movie-card { background: #151520; border: 1px solid #2a2939; border-radius: 16px; padding: 1rem; min-height: 168px; height: 100%; transition: transform .2s, border-color .2s; }
.movie-card:hover { transform: translateY(-3px); border-color: #8e72ee; }
.movie-index { color:#b7a0ff; font-size:.72rem; font-weight:700; letter-spacing:.12em; }
.movie-title { font-family:'Space Grotesk',sans-serif; font-size:1.08rem; font-weight:700; line-height:1.25; margin:.55rem 0 .7rem; }
.score-track { background:#302b40; height:5px; border-radius:8px; overflow:hidden; margin:.45rem 0; }
.score-fill { background:linear-gradient(90deg,#8061e8,#c0a9ff); height:100%; border-radius:8px; }
.score-label { color:#b7b3c8; font-size:.76rem; }
.section-title { font-family:'Space Grotesk',sans-serif; font-size:1.55rem; font-weight:700; letter-spacing:-.04em; }
div.stButton > button { border-radius: 12px; font-weight: 700; border: 1px solid #7f65db; }
div.stButton > button[kind="primary"] { background: linear-gradient(100deg,#7856df,#9a7af2); color:white; }
.stSelectbox div[data-baseweb="select"] > div, .stTextInput input { background:#151520; border-color:#343047; border-radius:12px; }
hr { border-color:#292637; }
.footer { color:#777488; font-size:.78rem; padding-top:2rem; }
</style>
""",
    unsafe_allow_html=True,
)


def _convert_names(value):
    try:
        return [x.get("name", "") for x in ast.literal_eval(value)]
    except (ValueError, SyntaxError, TypeError):
        return []


def _convert_cast(value):
    return _convert_names(value)[:3]


def _directors(value):
    try:
        return [
            x.get("name", "")
            for x in ast.literal_eval(value)
            if x.get("job") == "Director"
        ]
    except (ValueError, SyntaxError, TypeError):
        return []


def build_model():
    """Build the same CountVectorizer/cosine-similarity model used in the notebook."""
    if not MOVIES_CSV.exists() or not CREDITS_CSV.exists():
        raise FileNotFoundError(
            "Dataset files not found. Add tmdb_5000_movies.csv and tmdb_5000_credits.csv beside app.py."
        )
    movies = pd.read_csv(MOVIES_CSV)
    credits = pd.read_csv(CREDITS_CSV)
    movies = movies.merge(credits, on="title")
    required = ["movie_id", "title", "genres", "keywords", "overview", "cast", "crew"]
    movies = movies[required].dropna().copy()
    movies["genres"] = movies["genres"].apply(_convert_names)
    movies["keywords"] = movies["keywords"].apply(_convert_names)
    movies["cast"] = movies["cast"].apply(_convert_cast)
    movies["crew"] = movies["crew"].apply(_directors)
    for col in ["genres", "keywords", "cast", "crew"]:
        movies[col] = movies[col].apply(
            lambda items: [name.replace(" ", "") for name in items if name]
        )
    movies["overview"] = movies["overview"].astype(str).apply(str.split)
    movies["tags"] = (
        movies["genres"]
        + movies["cast"]
        + movies["crew"]
        + movies["keywords"]
        + movies["overview"]
    )
    new_df = movies[["movie_id", "title", "tags"]].copy()
    new_df["tags"] = new_df["tags"].apply(lambda items: " ".join(items))
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = CountVectorizer(max_features=5000, stop_words="english")
    vectors = vectorizer.fit_transform(new_df["tags"]).toarray()
    similarity = cosine_similarity(vectors)
    with MOVIE_FILE.open("wb") as f:
        pickle.dump(new_df, f)
    with SIMILARITY_FILE.open("wb") as f:
        pickle.dump(similarity, f)
    return new_df, similarity


@st.cache_resource(show_spinner="Loading movie data and preparing recommendations…")
def load_model():
    if MOVIE_FILE.exists() and SIMILARITY_FILE.exists():
        try:
            with MOVIE_FILE.open("rb") as f:
                movie_df = pickle.load(f)
            with SIMILARITY_FILE.open("rb") as f:
                similarity = pickle.load(f)
            if len(movie_df) == len(similarity):
                return movie_df, similarity
        except (pickle.UnpicklingError, EOFError, AttributeError, ValueError):
            pass
    return build_model()


def recommend(title, movie_df, similarity, count=5):
    matches = movie_df.index[
        movie_df["title"].astype(str).str.casefold() == title.casefold()
    ].tolist()
    if not matches:
        return []
    index = matches[0]
    distances = sorted(
        enumerate(similarity[index]), key=lambda pair: pair[1], reverse=True
    )
    return [(movie_df.iloc[i], float(score)) for i, score in distances if i != index][
        :count
    ]


def movie_card(title, rank, score):
    pct = max(0, min(100, round(score * 100)))
    st.markdown(
        f"""<div class="movie-card"><div class="movie-index">MATCH {rank:02d}</div><div class="movie-title">{title}</div><div class="score-label">Similarity · {pct}%</div><div class="score-track"><div class="score-fill" style="width:{pct}%"></div></div><div class="score-label">Based on shared movie features</div></div>""",
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        '<div class="brand">cine<span>pick</span> ✦</div>', unsafe_allow_html=True
    )
    st.caption("YOUR PERSONAL MOVIE DISCOVERY ENGINE")
    st.markdown("---")
    st.markdown("**How it works**")
    st.write(
        "Choose a movie you like. CinePick compares its genres, keywords, cast, director and overview with other movies to find similar titles."
    )
    st.markdown("---")
    st.markdown("**Recommendation settings**")
    recommendation_count = st.slider(
        "Number of recommendations", min_value=3, max_value=10, value=5
    )
    st.caption("Powered by CountVectorizer + cosine similarity.")

st.markdown(
    '<div class="hero"><div class="eyebrow">✦ Your next favourite is waiting</div><h1>Less scrolling.<br><em>More cinema.</em></h1><p class="subtle">Discover films that match your taste. Pick a movie you love and let the recommendation engine find your next watch.</p></div>',
    unsafe_allow_html=True,
)

try:
    movie_df, similarity = load_model()
except Exception as exc:
    st.error("CinePick couldn't load the recommendation model.")
    st.markdown(
        "**How to fix it:** Put `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` in the same folder as `app.py`, then restart the app. If you already have `movie_list.pkl` and `similarity.pkl`, place those files beside `app.py` instead."
    )
    with st.expander("Technical details"):
        st.code(str(exc))
    st.stop()

movie_titles = movie_df["title"].astype(str).drop_duplicates().sort_values().tolist()
col_a, col_b = st.columns([3, 1])
with col_a:
    selected_movie = st.selectbox(
        "Find a movie to start with",
        movie_titles,
        index=(movie_titles.index("Batman") if "Batman" in movie_titles else 0),
        help="Start typing a movie title to search the dataset.",
    )
with col_b:
    st.markdown("<div style='height:29px'></div>", unsafe_allow_html=True)
    discover = st.button(
        "✦ Find similar movies", type="primary", use_container_width=True
    )

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="panel"><div class="eyebrow">YOUR DISCOVERY STATS</div>',
    unsafe_allow_html=True,
)
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(
        f'<div class="stat">MOVIES IN LIBRARY<strong>{len(movie_titles):,}</strong></div>',
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        '<div class="stat">ENGINE<strong>Content-based</strong></div>',
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        '<div class="stat">MATCH METHOD<strong>Cosine similarity</strong></div>',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

if "last_movie" not in st.session_state:
    st.session_state.last_movie = None
if discover:
    st.session_state.last_movie = selected_movie

if st.session_state.last_movie:
    target = st.session_state.last_movie
    results = recommend(target, movie_df, similarity, recommendation_count)
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="eyebrow">BECAUSE YOU PICKED</div><div class="section-title">{target}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    if results:
        st.markdown(
            '<div class="section-title">Your next watchlist ✦</div><p class="subtle" style="font-size:.9rem">Ranked by how closely each movie matches your selection.</p>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for i, (row, score) in enumerate(results):
            with cols[i % len(cols)]:
                movie_card(str(row["title"]), i + 1, score)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        with st.expander("View recommendation scores"):
            score_df = pd.DataFrame(
                [
                    {
                        "Rank": i + 1,
                        "Movie": str(row["title"]),
                        "Similarity": f"{score:.4f}",
                    }
                    for i, (row, score) in enumerate(results)
                ]
            )
            st.dataframe(score_df, hide_index=True, use_container_width=True)
    else:
        st.info("No recommendations found for this title. Try another movie.")
else:
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Ready for your next favourite?</div><p class="subtle" style="font-size:.92rem">Select any title above and click <b>Find similar movies</b> to get started.</p>',
        unsafe_allow_html=True,
    )
    examples = [
        "The Dark Knight",
        "Inception",
        "Interstellar",
        "The Avengers",
        "Avatar",
    ]
    examples = [x for x in examples if x in movie_titles]
    if examples:
        st.caption("Try one of these popular picks")
        example_cols = st.columns(len(examples))
        for col, example in zip(example_cols, examples):
            with col:
                if st.button(f"🎬 {example}", use_container_width=True):
                    st.session_state.last_movie = example
                    st.rerun()

st.markdown(
    '<div class="footer">CINEPICK · Made for movie lovers · Recommendations are generated from your local content-based model.</div>',
    unsafe_allow_html=True,
>>>>>>> c2b0633 (procfile)
)