"""Visual identity for RegRadar.

Design language: a legal statute. Cool paper, a Libre Baskerville serif, an
oxblood accent, and cited passages set like references in a law report — the
register of a regulation, not a chat app.
"""

import streamlit as st

INK = "#1c1b1a"
OXBLOOD = "#1e6f52"
MUTED = "#6a665e"
PAPER = "#f4f3ef"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="st-"], [data-testid="stMarkdownContainer"], input, button, select {
  font-family: 'Inter', -apple-system, sans-serif;
}
[data-testid="stAppViewContainer"] { background: #f4f3ef; }

h1 {
  font-family: 'Libre Baskerville', Georgia, serif !important;
  font-weight: 700 !important; font-size: 2.3rem !important;
  letter-spacing: -0.01em; color: #1c1b1a !important;
}
h2, h3 {
  font-family: 'Libre Baskerville', Georgia, serif !important;
  font-weight: 700 !important; color: #1c1b1a !important;
}

[data-testid="stMetric"] {
  background: #faf9f5; border: 1px solid #ddd9cc; border-radius: 3px;
  padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: #6a665e !important; }
[data-testid="stMetricValue"] {
  font-family: 'Libre Baskerville', serif !important; color: #1c1b1a !important;
}

[data-testid="stSidebar"] { background: #edebe3; border-right: 1px solid #d8d3c4; }
[data-testid="stTabs"] button[role="tab"] { font-weight: 600; color: #6a665e; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: #1e6f52; }
[data-testid="stIconMaterial"] { font-family: 'Material Symbols Rounded' !important; }
div[data-testid="stExpander"] { border: 1px solid #ddd9cc; border-radius: 3px; background: #faf9f5; }
.stButton button { border-radius: 3px; border: 1px solid #c8c1ad; background: #faf9f5; color: #1e6f52; }
.stButton button:hover { border-color: #1e6f52; }

.masthead-rule { height: 3px; background: #1e6f52; width: 54px; margin: 6px 0 4px; }
.eyebrow {
  text-transform: uppercase; letter-spacing: 0.2em; font-size: 0.72rem;
  color: #c8851f; font-weight: 600;
}

/* the synthesised answer reads like an opinion: serif, justified, lead rule */
.answer {
  font-family: 'Libre Baskerville', Georgia, serif;
  font-size: 1.02rem; line-height: 1.65; color: #23211f;
  border-left: 3px solid #1e6f52; padding: 4px 0 4px 18px; margin: 8px 0 4px;
}

/* a cited passage, set like a law-report extract */
.passage {
  background: #faf9f5; border: 1px solid #e2ddd0; border-radius: 3px;
  padding: 12px 16px; margin: 8px 0;
}
.passage .cite {
  font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.78rem;
  text-transform: uppercase; letter-spacing: 0.06em; color: #1e6f52;
}
.passage .score { float: right; color: #9a958a; font-size: 0.75rem; font-weight: 500; }
.passage .body {
  font-family: 'Libre Baskerville', Georgia, serif; font-size: 0.92rem;
  line-height: 1.55; color: #34312d; margin-top: 6px;
}

.refusal {
  border-left: 3px solid #b08900; background: rgba(176,137,0,0.07);
  padding: 12px 16px; border-radius: 0 3px 3px 0; color: #4a4534;
  font-size: 0.96rem;
}

.dl-step { background: #faf9f5; border: 1px solid #ddd9cc; border-radius: 3px; padding: 18px; height: 100%; }
.dl-step b { color: #1e6f52; font-family: 'Libre Baskerville', serif; }
.dl-step .n {
  display: inline-block; font-family: 'Libre Baskerville', serif; font-weight: 700;
  color: #c8851f; font-size: 1.5rem; margin-bottom: 4px;
}
a { color: #1e6f52; }
table { font-size: 0.9rem; }
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def eyebrow(text: str):
    st.markdown(f'<p class="eyebrow">{text}</p><div class="masthead-rule"></div>',
                unsafe_allow_html=True)


def answer_block(text: str):
    st.markdown(f'<div class="answer">{text}</div>', unsafe_allow_html=True)


def refusal(text: str):
    st.markdown(f'<div class="refusal">{text}</div>', unsafe_allow_html=True)


def passage(ref: str, body: str, score: float, url: str):
    st.markdown(
        f'<div class="passage"><span class="score">relevance {score:.2f}</span>'
        f'<a class="cite" href="{url}" target="_blank">{ref}</a>'
        f'<div class="body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def step(n, title, body):
    st.markdown(
        f'<div class="dl-step"><span class="n">{n:02d}</span><br/>'
        f'<b>{title}</b><br/><span style="color:#5c594f;font-size:0.92rem">{body}</span></div>',
        unsafe_allow_html=True,
    )


def footer(repo: str):
    st.divider()
    st.markdown(
        f'<p style="color:#7a7568;font-size:0.85rem">Built by '
        f'<a href="https://drishtantleuva.github.io" target="_blank">'
        f'<b style="font-family:\'Fraunces\',Georgia,serif">Drishtant Leuva</b></a> '
        f'— Data Scientist · GenAI &amp; RegTech &nbsp;·&nbsp; '
        f'<a href="https://github.com/drishtantleuva/{repo}" target="_blank">Source on GitHub</a> '
        f'&nbsp;·&nbsp; <a href="https://www.linkedin.com/in/drishtant-leuva/" '
        f'target="_blank">LinkedIn</a></p>',
        unsafe_allow_html=True,
    )
