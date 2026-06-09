import os
import json
import re
import anthropic
from typing import List, Dict


def analyze_news(articles: List[Dict], watchlist: List[Dict]) -> Dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    news_text = "\n\n".join(
        f"[{i+1}] {a['source']} | {a['published']}\n{a['title']}\n{a['summary']}"
        for i, a in enumerate(articles[:60])
    )

    watchlist_text = ", ".join(
        f"{s['symbol']} ({s['name']}, {s['sector']})" for s in watchlist
    )

    prompt = f"""You are a sharp equity analyst at a top Indian brokerage. Write a morning market brief.

NEWS FROM MONEYCONTROL & ECONOMIC TIMES (last 20 hours):

{news_text}

---
WATCHLIST STOCKS: {watchlist_text}

---
Return ONLY a valid JSON object with this exact structure (no markdown, no preamble):

{{
  "morning_macro": "3-4 sentences: global overnight cues, domestic macro themes, key Nifty/Sensex levels, overall tone for today.",
  "nifty_outlook": "BULLISH",
  "nifty_reasoning": "1-2 sentences on today's specific catalysts.",
  "stories": [
    {{
      "headline": "Sharp specific headline",
      "source": "source name",
      "what_it_means": "Exactly 2 sentences on direct impact for Indian equities — sectors, flows, sentiment.",
      "pros": ["specific positive"],
      "cons": ["specific risk"],
      "watchlist_stocks": {{
        "SYMBOL": "concise 1-line reason"
      }}
    }}
  ],
  "watchlist_summary": {{
    "SYMBOL": {{
      "sentiment": "BULLISH",
      "trigger": "brief reason or NOT IMPACTED"
    }}
  }}
}}

Rules:
- Cover ALL meaningfully impactful stories for Indian equity markets — do not artificially cap the count (typically 10-15)
- what_it_means: exactly 2 sentences — be tight, specific, no padding
- pros/cons: max 2 points each; use empty array [] if genuinely not applicable
- watchlist_stocks per story: only stocks directly impacted (can be empty {{}})
- watchlist_summary: include ALL watchlist stocks, no exceptions
- nifty_outlook: must be BULLISH, BEARISH, or NEUTRAL
- Name sectors, companies, policies, numbers — no generic statements"""

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    if not raw.startswith("{"):
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)

    return json.loads(raw)
