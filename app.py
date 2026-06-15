"""RegRadar — a compliance copilot that answers only from the regulation.

Retrieval-augmented Q&A over the GDPR: every answer is grounded in specific
articles and cited, and the system refuses when a question isn't supported by
the text. Runs at zero cost with no API key (extractive answers); add a free
LLM key to turn on fluent synthesis.
"""

import streamlit as st

import branding
import rag

st.set_page_config(page_title="RegRadar — Compliance Copilot",
                   page_icon=":material/gavel:", layout="wide")
branding.inject()


@st.cache_resource(show_spinner="Loading the GDPR and building the index…")
def boot():
    chunks = rag.load_corpus()
    model = rag.load_model()
    emb = rag.embed_corpus(model, chunks)
    return model, emb, chunks


MODEL, EMB, CHUNKS = boot()


def get_api_key():
    import os
    try:
        return st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    except Exception:
        return os.environ.get("GROQ_API_KEY")


API_KEY = get_api_key()

branding.eyebrow("GenAI · Retrieval-Augmented Generation · RegTech")
st.title("RegRadar")
st.markdown(
    "<p style='font-size:1.05rem;color:#3a372f;margin-top:-6px'>A compliance copilot "
    "that answers <i>only</i> from the regulation — grounded in specific articles, "
    "cited, and willing to say when it doesn't know. Loaded here with the "
    "<b>GDPR</b>; the pipeline is corpus-agnostic.</p>",
    unsafe_allow_html=True,
)

tab_ask, tab_how, tab_corpus = st.tabs(["Ask", "How it works", "The corpus"])

# ================= TAB 1: ask =================

with tab_ask:
    st.caption("Ask a question about the GDPR, or try one of these:")
    cols = st.columns(3)
    if "q" not in st.session_state:
        st.session_state.q = rag.EXAMPLES[0]
    for i, ex in enumerate(rag.EXAMPLES):
        if cols[i % 3].button(ex, key=f"ex{i}", use_container_width=True):
            st.session_state.q = ex

    query = st.text_input("Your question", value=st.session_state.q)

    if query:
        passages = rag.retrieve(MODEL, EMB, CHUNKS, query, k=4)

        if not rag.is_grounded(passages):
            branding.refusal(
                "I can't answer that from the GDPR. The closest passages fall below "
                "the grounding threshold, so rather than guess, RegRadar declines — "
                "the behaviour you'd want from a compliance tool. Try a question "
                "about data subject rights, breaches, consent, transfers or fines."
            )
            with st.expander("Show the closest passages anyway"):
                for p in passages:
                    branding.passage(p["ref"], p["text"].split("\n\n", 1)[-1][:400] + " …",
                                     p["score"], p["url"])
        else:
            st.markdown("##### Answer")
            if API_KEY:
                try:
                    ans = rag.synthesize(query, passages, API_KEY)
                except Exception as e:
                    ans = rag.extractive_answer(passages) + \
                        f"<br/><span style='color:#9a958a;font-size:0.8rem'>(LLM synthesis unavailable: {e})</span>"
            else:
                ans = rag.extractive_answer(passages)
            branding.answer_block(ans)

            st.markdown("##### Grounded in")
            for p in passages:
                body = p["text"].split("\n\n", 1)[-1]
                snippet = body[:460] + (" …" if len(body) > 460 else "")
                branding.passage(p["ref"], snippet, p["score"], p["url"])

# ================= TAB 2: how it works =================

with tab_how:
    st.subheader("How a grounded answer is produced")
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        branding.step(1, "Parse the regulation",
                      "The official EUR-Lex text of the GDPR is parsed into its 99 "
                      "articles and split into 240 citable chunks, each tagged with "
                      "its article number and title.")
    with c2:
        branding.step(2, "Embed & index",
                      "Every chunk is embedded with model2vec static embeddings — "
                      "genuine semantic vectors, but CPU-only and dependency-light, "
                      "so the app runs free with fast cold starts.")
    with c3:
        branding.step(3, "Retrieve & gate",
                      "A question is embedded and matched by cosine similarity. If "
                      "the best match falls below the grounding threshold, RegRadar "
                      "refuses instead of guessing.")
    with c4:
        branding.step(4, "Ground the answer",
                      "Answers are built only from retrieved passages, each cited to "
                      "an article. With a free LLM key they're synthesised into prose; "
                      "without one, the passages are returned directly.")

    st.write("")
    st.subheader("Design decisions, and their why")
    with st.expander("Why a refusal threshold is the whole point"):
        st.markdown(
            "A compliance tool that confidently answers questions the regulation "
            "doesn't cover is worse than useless — it manufactures false assurance. "
            "RegRadar measures retrieval confidence and **declines** when grounding "
            "is weak (try *“What is the capital of France?”*). Knowing when **not** to "
            "answer is the hard, valuable part of applied RAG."
        )
    with st.expander("Why model2vec instead of a heavyweight embedding model"):
        st.markdown(
            "Transformer embedding models need PyTorch and a slow cold start — "
            "painful on free hosting. model2vec distils them into static vectors: "
            "real semantic search, pure-NumPy inference, ~30 MB, no GPU. The right "
            "tool when the demo must load instantly and cost nothing, without "
            "dropping to keyword search."
        )
    with st.expander("Why it works with no API key (and how to upgrade it)"):
        st.markdown(
            "The retrieval, citations and refusal — the parts that demonstrate RAG "
            "engineering — need no LLM and run at zero cost. Answer *synthesis* is an "
            "optional layer: drop a free Groq or Gemini key into Streamlit secrets "
            "and a one-line switch turns prose synthesis on. The grounding is "
            "identical either way, so the demo is honest about what the model adds."
        )
    with st.expander("Why this generalises beyond the GDPR"):
        st.markdown(
            "Nothing in the pipeline is GDPR-specific. Point `prep_corpus.py` at "
            "another regulation — an AML/CTF Act, AUSTRAC guidance, internal policy "
            "— and the same retrieval, citation and refusal apply. The GDPR is "
            "loaded here because it's openly licensed and universally recognised."
        )

    st.write("")
    st.subheader("Read the code")
    st.markdown(
        "Three files, cleanly separated — corpus, engine, interface.\n\n"
        "| Module | Responsibility |\n"
        "|---|---|\n"
        "| [`prep_corpus.py`](https://github.com/drishtantleuva/regradar/blob/main/prep_corpus.py) | Parses the EUR-Lex GDPR HTML into 240 article-tagged, citable chunks |\n"
        "| [`rag.py`](https://github.com/drishtantleuva/regradar/blob/main/rag.py) | Embedding, semantic retrieval, the grounding/refusal gate, and optional LLM synthesis |\n"
        "| [`app.py`](https://github.com/drishtantleuva/regradar/blob/main/app.py) | The interface you are using now |\n"
    )

# ================= TAB 3: the corpus =================

with tab_corpus:
    import pandas as pd

    c1, c2, c3 = st.columns(3)
    c1.metric("Articles", "99")
    c2.metric("Retrieval chunks", f"{len(CHUNKS)}")
    c3.metric("Grounding threshold", f"{rag.REFUSE_THRESHOLD:.2f}")

    st.subheader("Regulation (EU) 2016/679 — the GDPR")
    st.markdown(
        "The General Data Protection Regulation, the official consolidated text from "
        "[EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679). "
        "EU legal texts are reusable under Commission Decision 2011/833/EU with "
        "attribution. Below is every article RegRadar can cite."
    )
    articles = (
        pd.DataFrame(CHUNKS)[["article", "title"]]
        .drop_duplicates("article").sort_values("article")
        .rename(columns={"article": "Article", "title": "Title"})
    )
    st.dataframe(articles, hide_index=True, use_container_width=True, height=420)

branding.footer("regradar")
