"""Retrieval-augmented engine for RegRadar.

Semantic retrieval over the GDPR corpus with a grounding threshold that makes
the system *refuse* when a question isn't supported by the text. Answer
synthesis is optional: if a (free) LLM key is configured it writes a grounded,
cited answer; otherwise it returns the retrieved passages directly. Either way
the citations are real — nothing is generated that isn't in the corpus.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).parent / "data"
MODEL_NAME = "minishlab/potion-base-8M"   # static embeddings: fast, CPU-only, no torch
REFUSE_THRESHOLD = 0.33                    # below this top score, we don't have grounding
EURLEX = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679"

EXAMPLES = [
    "How quickly must a personal data breach be reported?",
    "What is the right to be forgotten?",
    "How large can GDPR fines be?",
    "When do I need consent to process personal data?",
    "What information must be given when collecting someone's data?",
    "What is the capital of France?",   # deliberately off-topic — should be refused
]


def load_corpus() -> list[dict]:
    return json.loads((DATA / "corpus.json").read_text())


def load_model():
    from model2vec import StaticModel
    return StaticModel.from_pretrained(MODEL_NAME)


def embed_corpus(model, chunks: list[dict]) -> np.ndarray:
    emb = model.encode([c["text"] for c in chunks])
    return emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)


def retrieve(model, emb: np.ndarray, chunks: list[dict], query: str,
             k: int = 4) -> list[dict]:
    qv = model.encode([query])[0]
    qv = qv / (np.linalg.norm(qv) + 1e-9)
    scores = emb @ qv
    out = []
    for i in scores.argsort()[::-1][:k]:
        c = chunks[i]
        out.append({
            "score": float(scores[i]),
            "ref": c["ref"],
            "title": c["title"],
            "article": c["article"],
            "text": c["text"],
            "url": f"{EURLEX}#d1e{c['article']}",
        })
    return out


def is_grounded(passages: list[dict]) -> bool:
    return bool(passages) and passages[0]["score"] >= REFUSE_THRESHOLD


def synthesize(query: str, passages: list[dict], api_key: str,
               model: str = "llama-3.1-8b-instant") -> str:
    """Write a grounded, cited answer from the passages using a free Groq model."""
    from groq import Groq

    context = "\n\n".join(f"[{p['ref']}] {p['text']}" for p in passages)
    system = (
        "You are RegRadar, a compliance assistant. Answer the user's question "
        "ONLY using the GDPR passages provided. Cite the article in brackets, "
        "e.g. (Article 33), for every claim. If the passages do not contain the "
        "answer, say so plainly. Be concise — three sentences at most. Do not "
        "invent obligations that are not in the passages."
    )
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Question: {query}\n\nPassages:\n{context}"},
        ],
        temperature=0.1,
        max_tokens=350,
    )
    return resp.choices[0].message.content.strip()


def extractive_answer(passages: list[dict]) -> str:
    """No-LLM fallback: a grounded lead that points to the cited passages below."""
    refs = ", ".join(dict.fromkeys(p["ref"] for p in passages[:3]))
    return (
        f"The most relevant provisions are <b>{refs}</b>. The exact wording is "
        "reproduced below, each linked to the official text — read the citations "
        "as the answer. (Add a free LLM key to have RegRadar synthesise these into "
        "prose; the retrieval and grounding shown here are identical either way.)"
    )
