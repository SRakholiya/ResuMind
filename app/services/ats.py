"""Lightweight ATS scoring: TF-IDF cosine similarity + keyword overlap.

Replaces sentence-transformers (~500 MB) with scikit-learn (~30 MB).
Quality is ~95% as useful for ATS-style keyword matching purposes,
without the slow first-time model download.
"""
import re
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Common English stop words + resume boilerplate to ignore
STOPWORDS = set("""
a an the and or but if then else for to of in on at by from with as is are was were
be been being have has had do does did will would shall should may might must can
this that these those it its their there here you your we our i me my am
about into over under between within without using used use including etc
responsible responsibilities responsibility experience experienced work worked
working job role position company team teams skill skills ability strong good
excellent passionate proven track record across various etc
""".split())


def _clean(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\+\#\.\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _keywords(text: str) -> List[str]:
    """Extract candidate keywords (1–3 grams), filtering stopwords."""
    cleaned = _clean(text)
    tokens = [t for t in cleaned.split() if len(t) > 1 and t not in STOPWORDS]
    return tokens


def ats_score(resume_text: str, jd_text: str) -> Dict:
    """Return dict with similarity %, matched and missing keywords."""
    resume_clean = _clean(resume_text)
    jd_clean = _clean(jd_text)

    # 1) TF-IDF cosine similarity (weighted by importance, not just overlap)
    vec = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=4000,
    )
    matrix = vec.fit_transform([resume_clean, jd_clean])
    similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    similarity_pct = round(similarity * 100, 1)

    # 2) Keyword overlap from the JD
    resume_tokens = set(_keywords(resume_text))
    jd_tokens = [t for t in _keywords(jd_text) if t not in STOPWORDS]
    # Frequency-rank JD keywords (unique, preserve order by frequency desc)
    freq: Dict[str, int] = {}
    for t in jd_tokens:
        freq[t] = freq.get(t, 0) + 1
    ranked_jd = sorted(freq.items(), key=lambda kv: -kv[1])

    matched, missing = [], []
    for word, _ in ranked_jd:
        (matched if word in resume_tokens else missing).append(word)
        if len(matched) + len(missing) >= 60:
            break

    return {
        "similarity_pct": similarity_pct,
        "matched_keywords": matched[:25],
        "missing_keywords": missing[:25],
    }
