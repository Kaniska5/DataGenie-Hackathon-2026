import streamlit as st
import re
import random
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from agent import (
    step1_research,
    step2_kpi_mapping,
    step3_top_stories,
    generate_confidence_score,
)

st.set_page_config(
    page_title="DataGenie Sales Agent",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def generate_pdf(company, research, story):
    filename = f"{company}_DataGenie_Report.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"<b>Company:</b> {company}", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Research Summary</b>", styles["Heading2"]))
    content.append(Paragraph(research.replace(
        "\n", "<br/>"), styles["BodyText"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Selected Top Story</b>", styles["Heading2"]))
    content.append(Paragraph(story.get("title", ""), styles["BodyText"]))
    content.append(Spacer(1, 8))
    content.append(Paragraph(story.get("what", ""), styles["BodyText"]))
    content.append(Spacer(1, 8))
    content.append(Paragraph(story.get("plain", ""), styles["BodyText"]))

    doc.build(content)

    return filename


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.main .block-container { padding: 2rem 3rem; max-width: 1100px; }
#MainMenu, footer, header { visibility: hidden; }

.dg-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 2rem; padding-bottom: 1.25rem;
    border-bottom: 1px solid #e5e7eb;
}
.dg-logo { font-size: 1.4rem; font-weight: 600; color: #2563eb; }
.dg-logo span { color: #2563eb; }
.dg-tagline { font-size: 0.75rem; color: #9ca3af; margin-left: auto; text-transform: uppercase; letter-spacing: 0.08em; }

.step-bar {
    display: flex; margin-bottom: 2rem;
    border-radius: 8px; overflow: hidden;
    border: 1px solid #e5e7eb;
}
.step-item {
    flex: 1; padding: 0.55rem 0.5rem;
    font-size: 0.72rem; font-weight: 500;
    text-align: center; background: #f9fafb;
    color: #9ca3af; border-right: 1px solid #e5e7eb;
}
.step-item:last-child { border-right: none; }
.step-item.active { background: #2563eb; color: white; }
.step-item.done   { background: #f0fdf4; color: #15803d; }

.card {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1rem;
}
.card-title {
    font-size: 0.68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #6b7280; margin-bottom: 0.5rem;
}
.card-body { font-size: 0.875rem; color: #1f2937; line-height: 1.65; }

.story-card {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 1.5rem; margin-bottom: 0.5rem;
}
.story-card:hover { border-color: #93c5fd; }
.story-number {
    display: inline-block; font-size: 0.68rem; font-weight: 600;
    color: #2563eb; background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 20px; padding: 2px 10px; margin-bottom: 0.6rem;
}
.story-title { font-size: 1rem; font-weight: 600; color: #111827; margin-bottom: 0.75rem; line-height: 1.4; }
.story-what {
    font-size: 0.855rem; color: #374151; line-height: 1.65;
    padding: 0.75rem 1rem; background: #f8faff;
    border-radius: 8px; border-left: 3px solid #2563eb;
    margin-bottom: 0.85rem;
}
.section-label {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.1em; color: #9ca3af; margin-bottom: 0.35rem; margin-top: 0.5rem;
}
.kpi-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0.6rem; }
.kpi-chip { font-size: 0.73rem; padding: 3px 10px; border-radius: 20px; font-weight: 500; }
.kpi-down { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.kpi-up   { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.kpi-neu  { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
.contrib-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 0.6rem; }
.contrib-tag {
    font-size: 0.7rem; padding: 2px 9px; border-radius: 20px;
    background: #f3f4f6; color: #6b7280; border: 1px solid #e5e7eb;
}
.knowledge-box {
    background: #f8faff; border: 1px solid #dbeafe;
    border-radius: 8px; padding: 0.875rem 1rem; margin-top: 0.65rem;
}
.knowledge-label {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.1em; color: #2563eb; margin-bottom: 0.35rem;
}
.knowledge-text { font-size: 0.82rem; color: #1e3a8a; line-height: 1.6; }
.plain-english {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 0.875rem 1rem; margin-top: 0.65rem;
}
.plain-label {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.1em; color: #15803d; margin-bottom: 0.35rem;
}
.plain-text { font-size: 0.82rem; color: #14532d; line-height: 1.6; }

.fit-high   { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.fit-medium { background: #fffbeb; color: #b45309; border: 1px solid #fcd34d; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.fit-low    { background: #fef2f2; color: #b91c1c; border: 1px solid #fca5a5; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }

.conf-score { font-size: 2.4rem; font-weight: 600; color: #2563eb; }
.conf-reason { font-size: 0.82rem; color: #374151; line-height: 1.6; }

.kpi-block {
    background: white; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 1.1rem 1.4rem; margin-bottom: 0.85rem;
}
.kpi-name { font-size: 0.95rem; font-weight: 600; color: #111827; margin-bottom: 0.4rem; }
.kpi-desc { font-size: 0.84rem; color: #374151; margin-bottom: 0.5rem; line-height: 1.5; }
.kpi-sql {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem;
    background: #f3f4f6; padding: 8px 12px; border-radius: 6px;
    color: #1e3a8a; margin-bottom: 0.5rem; word-break: break-all;
}
.kpi-meta { font-size: 0.78rem; color: #6b7280; display: flex; gap: 1.5rem; flex-wrap: wrap; }

.auto-pill {
    display: inline-block; font-size: 0.72rem; padding: 3px 10px;
    border-radius: 20px; margin: 3px; font-weight: 500;
}
.auto-yes   { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
.auto-human { background: #fff7ed; color: #c2410c; border: 1px solid #fdba74; }

.dg-divider { border: none; border-top: 1px solid #f3f4f6; margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)

for k, v in [
    ("step", "input"), ("company", ""), ("research", ""),
    ("kpis_raw", ""), ("stories_raw", ""),
    ("selected_idx", None), ("confidence_raw", ""),
]:
    if k not in st.session_state:
        st.session_state[k] = v


def parse_research(text):
    """Split LLM research text into {title: body} ordered list."""
    parts = re.split(r'\n##\s+', text)
    sections = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split('\n', 1)
        title = lines[0].strip().lstrip('#').strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if title:
            sections.append((title, body))
    return sections


def parse_confidence(text):
    """Extract score and reasons from LLM confidence output."""
    score_match = re.search(r'SCORE:\s*(\d+)', text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else None

    r1_match = re.search(r'REASON_1:\s*(.+?)(?=REASON_2:|$)',
                         text, re.IGNORECASE | re.DOTALL)
    r2_match = re.search(r'REASON_2:\s*(.+?)$', text,
                         re.IGNORECASE | re.DOTALL)

    r1 = r1_match.group(1).strip() if r1_match else ""
    r2 = r2_match.group(1).strip() if r2_match else ""
    return score, r1, r2


def parse_kpis(text):
    """Parse KPI blocks between KPI_START / KPI_END markers, with fallback."""
    blocks = re.findall(r'KPI_START(.*?)KPI_END', text,
                        re.DOTALL | re.IGNORECASE)

    if not blocks:
        # Fallback: try numbered blocks like "1." or "KPI 1" or "**KPI 1**"
        blocks = re.split(
            r'\n(?=\*{0,2}KPI\s*\d|\d+\.\s+\*{0,2}KPI|\d+\.\s+[A-Z])', text)
        blocks = [b for b in blocks if len(b.strip()) > 20]

    kpis = []
    for block in blocks[:5]:
        def field(label, fallback="—"):
            m = re.search(
                rf'(?:{label}|{label.lower()})\s*[:\-]\s*(.+?)(?=\n[A-Za-z_]+\s*[:\-]|\Z)',
                block, re.IGNORECASE | re.DOTALL
            )
            return m.group(1).strip() if m else fallback

        name = field("Name")
        desc = field("Description")
        sql = field("SQL")
        dims = field("Dimensions")
        gran = field("Granularity")

        # If name is still "—", try first non-empty line as name
        if name == "—":
            for line in block.strip().split('\n'):
                line = re.sub(r'[\*#\d\.\-]', '', line).strip()
                if len(line) > 3:
                    name = line
                    break

        if name != "—":
            kpis.append({"name": name, "desc": desc,
                        "sql": sql, "dims": dims, "gran": gran})

    return kpis


def parse_stories(text):
    """Parse story blocks between STORY_START / STORY_END markers, with fallback."""
    blocks = re.findall(r'STORY_START(.*?)STORY_END',
                        text, re.DOTALL | re.IGNORECASE)

    if not blocks:
        # Fallback: split on "DataGenie Top Story Card" or numbered headings
        blocks = re.split(
            r'\*{0,2}DataGenie Top Story Card\s*\d+[:\*]*\s*|\n(?=Story\s*\d|STORY\s*\d|\*\*Story)',
            text, flags=re.IGNORECASE
        )
        blocks = [b for b in blocks if len(b.strip()) > 40]

    stories = []
    for block in blocks[:3]:

        def field(label, fallback=""):
            m = re.search(
                rf'(?:{label})\s*[:\-]\s*(.+?)(?=\n[A-Za-z_]+\s*[:\-]|\Z)',
                block, re.IGNORECASE | re.DOTALL
            )
            return m.group(1).strip() if m else fallback

        title = field("Title")
        what = field("What_Happened|What Happened|What happened")
        pain = field("Pain_Point|Pain Point|Pain point|Business impact")
        plain = field(
            "Plain_English|Plain English|Plain english|Plain language")
        contribs_s = field("Contributors")

        # KPI lines — look for KPI_1/KPI_2/KPI_3 or bullet lines with % signs
        kpi_lines = []
        kpi_matches = re.findall(r'KPI_\d+:\s*(.+)', block, re.IGNORECASE)
        if kpi_matches:
            kpi_lines = kpi_matches
        else:
            # Fallback: lines with % in them
            for line in block.split('\n'):
                line = line.strip().lstrip('*-').strip()
                if '%' in line and len(line) > 5:
                    kpi_lines.append(line)
        kpi_lines = kpi_lines[:4]

        contribs = [c.strip() for c in re.split(r'[,;]', contribs_s)
                    if c.strip()] if contribs_s else []

        # If title is empty, grab first meaningful line
        if not title:
            for line in block.strip().split('\n'):
                line = re.sub(r'[\*#]', '', line).strip()
                if len(line) > 10:
                    title = line
                    break

        if title:
            stories.append({
                "title":       title,
                "what":        what or "Anomaly detected across key metrics.",
                "kpis":        kpi_lines,
                "contributors": contribs,
                "pain":        pain or "This pattern has significant business impact.",
                "plain":       plain or "A key metric dropped unexpectedly in a specific segment.",
            })

    return stories


def kpi_dir(kpi_line):
    if re.search(r'\+\d', kpi_line):
        return "up"
    if re.search(r'-\d',  kpi_line):
        return "down"
    return "neu"


def extract_numbers(text):
    vals = [abs(int(n.replace('%', '')))
            for n in re.findall(r'[-+]?\d+%', text)]
    while len(vals) < 4:
        vals.append(random.randint(8, 25))
    return vals[:4]


def gen_series(base, drift, n=12):
    v, data = base, []
    for i in range(n):
        v += random.uniform(-drift * 0.35, drift * 0.35)
        if i >= 9:
            v -= drift * 0.55
        data.append(round(max(1, v), 1))
    return data


STEP_LABELS = ["Company", "Research", "KPIs", "Top Stories", "Dashboard"]
STEP_KEYS = ["input",   "research", "kpis", "stories",     "dashboard"]


def render_header():
    st.markdown("""
    <div class="dg-header">
        <div class="dg-logo">DataGenie Sales Agent</div>
        <div class="dg-tagline">Milestone 4 — Agentic Workflow</div>
    </div>""", unsafe_allow_html=True)


def render_steps():
    cur_idx = STEP_KEYS.index(st.session_state.step)
    html = '<div class="step-bar">'
    for i, (label, key) in enumerate(zip(STEP_LABELS, STEP_KEYS)):
        cls = "active" if i == cur_idx else ("done" if i < cur_idx else "")
        html += f'<div class="step-item {cls}">{label}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_story_card(story, idx):
    kpi_html = "".join(
        f'<span class="kpi-chip kpi-{kpi_dir(k)}">{k}</span>'
        for k in story["kpis"]
    )
    contrib_html = "".join(
        f'<span class="contrib-tag">{c}</span>'
        for c in story["contributors"]
    )
    st.markdown(f"""
    <div class="story-card">
        <div class="story-number">Story {idx + 1}</div>
        <div class="story-title">{story["title"]}</div>
        <div class="section-label">What happened</div>
        <div class="story-what">{story["what"]}</div>
        <div class="section-label">KPI signals</div>
        <div class="kpi-row">{kpi_html if kpi_html else "<span style='color:#9ca3af;font-size:0.8rem;'>No KPI signals extracted</span>"}</div>
        <div class="section-label">Contributors</div>
        <div class="contrib-row">{contrib_html if contrib_html else "<span style='color:#9ca3af;font-size:0.8rem;'>—</span>"}</div>
        <div class="knowledge-box">
            <div class="knowledge-label">Pain point &amp; DataGenie impact</div>
            <div class="knowledge-text">{story["pain"]}</div>
        </div>
        <div class="plain-english">
            <div class="plain-label">Plain English summary</div>
            <div class="plain-text">{story["plain"]}</div>
        </div>
    </div>""", unsafe_allow_html=True)


render_header()
render_steps()

if st.session_state.step == "input":
    st.markdown("### Prospect company")
    st.caption("Select from the AI summit attendees or type a custom name.")

    presets = ["Experian", "Trivago", "Maruti Suzuki", "Rolex", "Latham Pools"]
    cols = st.columns(len(presets))
    for i, name in enumerate(presets):
        if cols[i].button(name, use_container_width=True):
            st.session_state.company = name

    st.markdown("<hr class='dg-divider'>", unsafe_allow_html=True)
    typed = st.text_input("Or type a company name", value=st.session_state.company,
                          label_visibility="collapsed", placeholder="e.g. Trivago")
    if typed:
        st.session_state.company = typed

    if st.session_state.company:
        st.markdown(f"**Selected:** {st.session_state.company}")

    col_run, _ = st.columns([1, 3])
    if col_run.button("▶ Run analysis", type="primary", disabled=not st.session_state.company):
        with st.spinner(f"Researching {st.session_state.company}..."):
            brief, _ = step1_research(st.session_state.company)
            st.session_state.research = brief
        st.session_state.step = "research"
        st.rerun()


elif st.session_state.step == "research":
    st.markdown(f"### {st.session_state.company} — research")

    sections = parse_research(st.session_state.research)

    if not sections:
        st.markdown(st.session_state.research)
    else:
        for title, body in sections:
            is_fit = "fit" in title.lower()
            if is_fit:
                body_lower = body.lower()
                level = "high" if "high" in body_lower else (
                    "low" if "low" in body_lower else "medium")
                badge = f'<span class="fit-{level}">{level.upper()} FIT</span>'
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{title} &nbsp;{badge}</div>
                    <div class="card-body">{body}</div>
                </div>""", unsafe_allow_html=True)
            else:
                body_rendered = re.sub(
                    r'^(\s*[-•*]\s*)([A-Z][^:.\n]{2,30}:)',
                    r'\1<strong>\2</strong>',
                    body, flags=re.MULTILINE
                )
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{title}</div>
                    <div class="card-body">{body_rendered}</div>
                </div>""", unsafe_allow_html=True)

    if not st.session_state.confidence_raw:
        with st.spinner("Calculating confidence score..."):
            st.session_state.confidence_raw = generate_confidence_score(
                st.session_state.research)

    score, r1, r2 = parse_confidence(st.session_state.confidence_raw)
    score_display = f"{score}%" if score is not None else "—"

    st.markdown(f"""
    <div class="card" style="display:flex;align-items:flex-start;gap:1.5rem;">
        <div style="min-width:80px;">
            <div class="card-title">Confidence</div>
            <div class="conf-score">{score_display}</div>
        </div>
        <div>
            <div class="conf-reason">{'<br>'.join(filter(None, [r1, r2]))}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='dg-divider'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 3])

    if c1.button("✅ Approve & continue", type="primary"):
        with st.spinner("Mapping KPIs..."):
            st.session_state.kpis_raw = step2_kpi_mapping(
                st.session_state.company, st.session_state.research
            )
        st.session_state.step = "kpis"
        st.rerun()

    if c2.button("🔁 Regenerate"):
        st.session_state.confidence_raw = ""
        with st.spinner("Regenerating..."):
            brief, _ = step1_research(st.session_state.company)
            st.session_state.research = brief
        st.rerun()

    with st.expander("✏️ Edit research manually"):
        edited = st.text_area("Edit", st.session_state.research, height=250,
                              label_visibility="collapsed")
        if st.button("Save edits"):
            st.session_state.research = edited
            st.session_state.confidence_raw = ""
            st.success("Saved.")
            st.rerun()


elif st.session_state.step == "kpis":
    st.markdown(f"### {st.session_state.company} — KPI mapping")

    kpis = parse_kpis(st.session_state.kpis_raw)

    if not kpis:
        st.warning("KPI parsing failed. Showing raw output.")
        st.code(st.session_state.kpis_raw)
    else:
        for i, k in enumerate(kpis):
            st.markdown(f"""
            <div class="kpi-block">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem;">
                    <div class="story-number">KPI {i+1}</div>
                    <div class="kpi-name">{k['name']}</div>
                </div>
                <div class="kpi-desc">{k['desc']}</div>
                <div class="kpi-sql">{k['sql']}</div>
                <div class="kpi-meta">
                    <span><strong>Dimensions:</strong> {k['dims']}</span>
                    <span><strong>Granularity:</strong> {k['gran']}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='dg-divider'>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 3])

    if c1.button("✅ Approve & continue", type="primary"):
        with st.spinner("Generating top stories..."):
            st.session_state.stories_raw = step3_top_stories(
                st.session_state.company,
                st.session_state.research,
                st.session_state.kpis_raw,
            )
        st.session_state.step = "stories"
        st.rerun()

    if c2.button("🔁 Regenerate"):
        with st.spinner("Regenerating..."):
            st.session_state.kpis_raw = step2_kpi_mapping(
                st.session_state.company, st.session_state.research
            )
        st.rerun()


elif st.session_state.step == "stories":
    st.markdown(f"### {st.session_state.company} — top stories")
    st.caption(
        "Review the stories below. Select one to generate an analytics dashboard.")

    stories = parse_stories(st.session_state.stories_raw)

    if not stories:
        st.warning(
            "Could not parse story cards. Showing raw output — use Regenerate.")
        st.code(st.session_state.stories_raw)
    else:
        for i, story in enumerate(stories):
            render_story_card(story, i)
            if st.button(
                f" Build dashboard for Story {i+1}",
                key=f"sel_{i}",
                use_container_width=True,
            ):
                st.session_state.selected_idx = i
                st.session_state.step = "dashboard"
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<hr class='dg-divider'>", unsafe_allow_html=True)
    c1, _ = st.columns([1, 4])
    if c1.button("🔁 Regenerate stories"):
        with st.spinner("Regenerating..."):
            st.session_state.stories_raw = step3_top_stories(
                st.session_state.company,
                st.session_state.research,
                st.session_state.kpis_raw,
            )
        st.rerun()


elif st.session_state.step == "dashboard":
    stories = parse_stories(st.session_state.stories_raw)
    idx = st.session_state.selected_idx or 0
    story = stories[idx] if idx < len(
        stories) else (stories[0] if stories else {})

    st.markdown(f"### Dashboard — Story {idx + 1}")
    if story.get("title"):
        st.markdown(
            f"<div style='font-size:0.9rem;font-weight:600;color:#111827;margin-bottom:0.25rem;'>{story['title']}</div>",
            unsafe_allow_html=True,
        )

    st.caption(
        "What your analyst team sees **without DataGenie** — hours of manual slicing to find the root cause.")

    def extract_story_numbers(text):
        vals = [abs(int(n.replace('%', '')))
                for n in re.findall(r'[-+]?\d+%', text)]
        while len(vals) < 3:
            vals.append(10)
        return vals[:3]
    kpi_text = " ".join(story.get("kpis", []))
    n0, n1, n2 = extract_story_numbers(kpi_text)

    kpi_names = []
    for k in story.get("kpis", [])[:3]:
        name_part = k.split("|")[0].strip(
        ) if "|" in k else k.split(":")[0].strip()
        name_part = re.sub(r'[-+]\d+%', '', name_part).strip()
        kpi_names.append(name_part or f"KPI {len(kpi_names)+1}")
    while len(kpi_names) < 3:
        kpi_names.append(f"KPI {len(kpi_names)+1}")

    c1, c2, c3 = st.columns(3)
    c1.metric(kpi_names[0], f"↓ {n0}%", f"−{n0}% vs prior period")
    c2.metric(kpi_names[1], f"↑ {n1}%", f"+{n1}% vs prior period")
    c3.metric(kpi_names[2], f"↓ {n2}%", f"−{n2}% vs prior period")

    st.markdown("<hr class='dg-divider'>", unsafe_allow_html=True)

    def trend(base, change):
        step = change / 10
        data = []
        val = base
        for _ in range(12):
            val -= step
            data.append(round(val, 2))
        return data

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    ca, cb = st.columns(2)
    with ca:
        st.line_chart(pd.DataFrame({"Value": trend(100, n0)}, index=months))
    with cb:
        st.line_chart(pd.DataFrame({"Value": trend(80, -n1)}, index=months))

    cc, cd = st.columns(2)

    contribs = story.get(
        "contributors", ["Segment A", "Segment B", "Segment C"])[:3]

    kpi_impacts = []

    for k in story.get("kpis", [])[:3]:
        match = re.search(r'([+-]\d+)%', k)
        if match:
            val = int(match.group(1))
            kpi_impacts.append(val)
        else:
            kpi_impacts.append(0)

    while len(kpi_impacts) < 3:
        kpi_impacts.append(0)

    impacts = kpi_impacts[:len(contribs)]
    with cc:
        st.bar_chart(pd.DataFrame(
            {"Impact %": impacts[:len(contribs)]}, index=contribs))

    with cd:
        st.line_chart(pd.DataFrame({
            kpi_names[0]: trend(90, n0),
            kpi_names[1]: trend(70, -n1)
        }, index=months))

    st.markdown("<hr class='dg-divider'>", unsafe_allow_html=True)

    c1, c2, _ = st.columns([1, 1, 3])

    if c1.button("← Back to stories"):
        st.session_state.step = "stories"
        st.rerun()

    if c2.button("🔄 Start over"):
        for k, v in [
            ("step", "input"), ("company", ""), ("research", ""),
            ("kpis_raw", ""), ("stories_raw", ""),
            ("selected_idx", None), ("confidence_raw", ""),
        ]:
            st.session_state[k] = v
        st.rerun()
