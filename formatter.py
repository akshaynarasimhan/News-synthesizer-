from typing import Dict, List

_SENTIMENT_COLOR = {
    "BULLISH": "#16a34a",
    "BEARISH": "#dc2626",
    "NEUTRAL": "#d97706",
    "NOT IMPACTED": "#6b7280",
}

_OUTLOOK_ICON = {"BULLISH": "▲", "BEARISH": "▼", "NEUTRAL": "◆"}


def _build_company_news_html(company_articles: List[Dict]) -> str:
    if not company_articles:
        return ""

    # Group by company symbol, preserving insertion order
    groups: dict = {}
    for a in company_articles:
        sym = a.get("company", "OTHER")
        groups.setdefault(sym, []).append(a)

    groups_html = ""
    for sym, articles in groups.items():
        items_html = ""
        for a in articles:
            title = a.get("title", "")
            link = a.get("link", "")
            published = a.get("published", "")
            source = a.get("source", "").replace(f"[{sym}] ", "")
            summary = a.get("summary", "")

            title_tag = (
                f'<a href="{link}" style="color:#1d4ed8;text-decoration:none">{title}</a>'
                if link else title
            )
            items_html += f"""
      <div class="co-item">
        <div class="co-meta">{source} &middot; {published}</div>
        <div class="co-title">{title_tag}</div>
        {"" if not summary else f'<div class="co-summary">{summary}</div>'}
      </div>"""

        groups_html += f"""
    <div class="co-group">
      <div class="co-hdr">{sym}</div>
      {items_html}
    </div>"""

    return f"""
  <div class="sec">
    <div class="sec-lbl">Company News &mdash; Last 24h</div>
    {groups_html}
  </div>"""


def format_email(analysis: Dict, date_str: str, company_articles: List[Dict] | None = None) -> str:
    outlook = analysis.get("nifty_outlook", "NEUTRAL")
    outlook_color = _SENTIMENT_COLOR.get(outlook, "#d97706")
    outlook_icon = _OUTLOOK_ICON.get(outlook, "◆")

    stories_html = ""
    for story in analysis.get("stories", []):
        pros_items = "".join(f"<li>{p}</li>" for p in story.get("pros", []))
        cons_items = "".join(f"<li>{c}</li>" for c in story.get("cons", []))

        pros_block = (
            '<div class="pc-block"><div class="pc-label" style="color:#16a34a">↑ Pros</div>'
            f"<ul>{pros_items}</ul></div>"
            if pros_items else ""
        )
        cons_block = (
            '<div class="pc-block"><div class="pc-label" style="color:#dc2626">↓ Cons</div>'
            f"<ul>{cons_items}</ul></div>"
            if cons_items else ""
        )
        pc_row = f'<div class="pc-row">{pros_block}{cons_block}</div>' if (pros_block or cons_block) else ""

        chips = "".join(
            f'<span class="chip">{sym}: {reason}</span>'
            for sym, reason in story.get("watchlist_stocks", {}).items()
        )
        watchlist_block = (
            f'<div class="chips-row"><span class="chips-label">\U0001f4cc Watchlist:</span>{chips}</div>'
            if chips else ""
        )

        stories_html += f"""
    <div class="card">
      <div class="card-src">{story.get("source", "")}</div>
      <div class="card-headline">{story.get("headline", "")}</div>
      <div class="card-impact">{story.get("what_it_means", "")}</div>
      {pc_row}
      {watchlist_block}
    </div>"""

    wl_rows = ""
    for sym, data in analysis.get("watchlist_summary", {}).items():
        sentiment = data.get("sentiment", "NEUTRAL")
        color = _SENTIMENT_COLOR.get(sentiment, "#6b7280")
        trigger = data.get("trigger", "—")
        wl_rows += f"""
    <tr>
      <td class="wl-sym">{sym}</td>
      <td><span class="badge" style="background:{color}">{sentiment}</span></td>
      <td class="wl-trigger">{trigger}</td>
    </tr>"""

    company_news_section = _build_company_news_html(company_articles or [])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Morning Market Brief</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:14px;background:#f1f5f9;color:#1e293b}}
.wrap{{max-width:660px;margin:0 auto;background:#fff}}
.hdr{{background:#0f172a;color:#fff;padding:18px 24px}}
.hdr-title{{font-size:18px;font-weight:700;letter-spacing:-.3px}}
.hdr-date{{color:#94a3b8;font-size:12px;margin-top:3px}}
.outlook{{background:{outlook_color};color:#fff;padding:10px 24px;font-size:14px;font-weight:600;line-height:1.4}}
.sec{{padding:14px 24px}}
.sec-lbl{{font-size:10px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:#94a3b8;margin-bottom:8px}}
.macro{{background:#f8fafc;border-left:3px solid #0f172a;padding:11px 14px;font-size:14px;line-height:1.6;color:#334155;border-radius:0 5px 5px 0}}
.card{{border:1px solid #e2e8f0;border-radius:7px;padding:11px 13px;margin-bottom:8px}}
.card-src{{font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#64748b;margin-bottom:4px}}
.card-headline{{font-size:14px;font-weight:700;line-height:1.3;margin-bottom:7px;color:#0f172a}}
.card-impact{{font-size:14px;line-height:1.55;color:#475569;margin-bottom:8px}}
.pc-row{{display:flex;gap:10px;margin-bottom:7px}}
.pc-block{{flex:1;background:#f8fafc;border-radius:4px;padding:7px 10px}}
.pc-label{{font-size:11px;font-weight:700;margin-bottom:4px}}
.pc-block ul{{padding-left:15px;font-size:13px;color:#475569;line-height:1.45}}
.chips-row{{display:flex;flex-wrap:wrap;align-items:center;gap:4px}}
.chips-label{{font-size:11px;font-weight:600;color:#475569;margin-right:2px}}
.chip{{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:4px;padding:2px 7px;font-size:12px;font-weight:500}}
.wl-tbl{{width:100%;border-collapse:collapse;font-size:14px}}
.wl-tbl th{{text-align:left;padding:7px 9px;background:#f8fafc;font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#94a3b8;border-bottom:2px solid #e2e8f0}}
.wl-sym{{padding:8px 9px;font-weight:700;color:#0f172a}}
.wl-trigger{{padding:8px 9px;color:#475569;font-size:13px}}
.badge{{display:inline-block;padding:2px 7px;border-radius:20px;color:#fff;font-size:10px;font-weight:700;letter-spacing:.3px}}
.co-group{{border:1px solid #e2e8f0;border-radius:7px;overflow:hidden;margin-bottom:10px}}
.co-hdr{{background:#0f172a;color:#fff;padding:6px 12px;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase}}
.co-item{{padding:8px 12px;border-bottom:1px solid #f1f5f9}}
.co-item:last-child{{border-bottom:none}}
.co-meta{{font-size:10px;color:#94a3b8;margin-bottom:3px}}
.co-title{{font-size:13px;font-weight:600;color:#0f172a;margin-bottom:3px}}
.co-summary{{font-size:12px;color:#64748b;line-height:1.4}}
.ftr{{background:#f8fafc;padding:12px 24px;font-size:11px;color:#94a3b8;text-align:center;border-top:1px solid #e2e8f0}}
@media(max-width:480px){{.pc-row{{flex-direction:column}}}}
@media print{{
  @page{{size:A4 portrait;margin:12mm 16mm}}
  body{{background:#fff!important;font-size:14px}}
  .wrap{{max-width:100%;box-shadow:none}}
  .hdr,.outlook{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  .badge,.chip,.pc-block{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  .card{{break-inside:avoid;border-color:#ccc}}
  .co-group{{break-inside:avoid}}
  .ftr{{display:none}}
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <div class="hdr-title">Morning Market Brief</div>
    <div class="hdr-date">{date_str} &middot; NSE / BSE</div>
  </div>

  <div class="outlook">{outlook_icon} Nifty: {outlook} &middot; {analysis.get("nifty_reasoning", "")}</div>

  <div class="sec">
    <div class="sec-lbl">Macro Setup</div>
    <div class="macro">{analysis.get("morning_macro", "")}</div>
  </div>

  <div class="sec">
    <div class="sec-lbl">Stories</div>
    {stories_html}
  </div>

  <div class="sec">
    <div class="sec-lbl">Watchlist Snapshot</div>
    <table class="wl-tbl">
      <thead><tr><th>Stock</th><th>Today</th><th>Trigger</th></tr></thead>
      <tbody>{wl_rows}</tbody>
    </table>
  </div>

  {company_news_section}

  <div class="ftr">Generated at 7:30 AM IST &middot; Powered by Claude &middot; Sources: Moneycontrol, Economic Times, Google News</div>
</div>
</body>
</html>"""
