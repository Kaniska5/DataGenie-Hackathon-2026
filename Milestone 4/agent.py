import time
import os
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def ask_llm(prompt, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=2500,
    )
    return response.choices[0].message.content


def search_web(query, max_results=5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        return f"Search failed: {e}"


def step1_research(company):
    searches = [
        f"{company} business model revenue streams 2024 2025",
        f"{company} data analytics tech stack infrastructure",
        f"{company} challenges pain points operations",
        f"{company} financials KPIs metrics performance",
    ]
    all_results = []
    for query in searches:
        result = search_web(query, max_results=4)
        all_results.append(result)
        time.sleep(1)

    combined = "\n\n".join(all_results)

    prompt = f"""Analyze {company} as a potential customer for DataGenie (an autonomous analytics insights platform).

Write your response using EXACTLY these section headers (copy them exactly including the ##):

## Company Overview
2-3 sentences on what the company does and its scale.

## Business Model & Revenue Streams
How they make money. Key revenue drivers.

## Key Business Metrics
The 4-6 most important KPIs this company tracks.

## Data & Analytics Pain Points
3-5 specific pain points related to their data or reporting.

## Tech Stack
Known or likely data/analytics tools they use.

## DataGenie Fit Assessment
State HIGH FIT, MEDIUM FIT, or LOW FIT on the first line, then 2-3 sentences explaining why.

Research Data:
{combined}"""

    result = ask_llm(
        prompt,
        "You are a senior B2B sales researcher. Be specific and concise. "
        "Always use the exact section headers provided with ## prefix."
    )
    return result, combined


def step2_kpi_mapping(company, research_brief):
    prompt = f"""Define 5 KPIs for {company} that DataGenie could track autonomously.

You MUST use exactly this format for each KPI. Copy the markers exactly:

KPI_START
Name: [KPI name here]
Description: [One sentence describing what it measures]
SQL: [Realistic SQL expression]
Dimensions: [comma separated dimensions]
Granularity: [Daily or Weekly or Monthly]
KPI_END

Repeat KPI_START...KPI_END exactly 5 times for 5 different KPIs.

Research context:
{research_brief}"""

    return ask_llm(
        prompt,
        "You are a data analytics expert. "
        "You MUST use KPI_START and KPI_END markers for every KPI. "
        "Do not write anything outside the KPI blocks."
    )


def step3_top_stories(company, research_brief, kpis):
    prompt = f"""Create 3 DataGenie Top Story cards for {company}.

You MUST use EXACTLY this format. Copy the markers exactly:

STORY_START
Title: [Specific anomaly with % change and which dimension or segment it affects]
What_Happened: [2-3 sentences describing the metric anomaly and observed pattern]
KPI_1: [KPI name] | [+XX% or -XX%] | [one line description]
KPI_2: [KPI name] | [+XX% or -XX%] | [one line description]
KPI_3: [KPI name] | [+XX% or -XX%] | [one line description]
Contributors: [Dimension1: Value1], [Dimension2: Value2], [Dimension3: Value3]
Pain_Point: [In 3 lines max: why this is a pain point and what DataGenie detection would achieve]
Plain_English: [In 3-4 sentences: explain what happened with zero technical jargon for a business executive]
STORY_END

Repeat STORY_START...STORY_END exactly 3 times for 3 different anomaly stories.

Research:
{research_brief}

KPIs:
{kpis}"""

    return ask_llm(
        prompt,
        "You are a DataGenie sales engineer. "
        "You MUST use STORY_START and STORY_END markers. "
        "Never deviate from the format. Every story must have all 8 fields."
    )


def generate_confidence_score(research_text):
    prompt = f"""Assess the quality of this company research for B2B sales purposes.

Respond in EXACTLY this format with these exact labels:
SCORE: [a number between 0 and 100, nothing else]
REASON_1: [one sentence about what makes this research strong]
REASON_2: [one sentence about what is missing or uncertain]

Research:
{research_text}"""

    return ask_llm(
        prompt,
        "You are a research quality analyst. "
        "Always respond with SCORE:, REASON_1:, REASON_2: labels on separate lines."
    )
