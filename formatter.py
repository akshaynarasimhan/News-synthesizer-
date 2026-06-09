from typing import Dict

_SENTIMENT_COLOR = {
    "BULLISH": "#16a34a",
    "BEARISH": "#dc2626",
    "NEUTRAL": "#d97706",
    "NOT IMPACTED": "#6b7280",
}

_OUTLOOK_ICON = {"BULLISH": "▲", "BEARISH": "▼", "NEUTRAL": "◆"}


def format_email(analysis: Dict, date_str: str) -> str:
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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Morning Market Brief</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background:#f1f5f9;color:#1e293b}}
.wrap{{max-width:660px;margin:0 auto;background:#fff}}
.hdr{{background:#0f172a;color:#fff;padding:22px 26px}}
.hdr-title{{font-size:20px;font-weight:700;letter-spacing:-.3px}}
.hdr-date{{color:#94a3b8;font-size:12px;margin-top:4px}}
.outlook{{background:{outlook_color};color:#fff;padding:11px 26px;font-size:14px;font-weight:600}}
.sec{{padding:18px 26px}}
.sec-lbl{{font-size:10px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:#94a3b8;margin-bottom:10px}}
.macro{{background:#f8fafc;border-left:3px solid #0f172a;padding:13px 15px;font-size:13.5px;line-height:1.65;color:#334155;border-radius:0 6px 6px 0}}
.card{{border:1px solid #e2e8f0;border-radius:8px;padding:15px;margin-bottom:12px}}
.card-src{{font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#64748b;margin-bottom:5px}}
.card-headline{{font-size:15px;font-weight:700;line-height:1.3;margin-bottom:9px;color:#0f172a}}
.card-impact{{font-size:13px;line-height:1.6;color:#475569;margin-bottom:10px}}
.pc-row{{display:flex;gap:12px;margin-bottom:9px}}
.pc-block{{flex:1;background:#f8fafc;border-radius:5px;padding:9px 11px}}
.pc-label{{font-size:11px;font-weight:700;margin-bottom:5px}}
.pc-block ul{{padding-left:16px;font-size:12px;color:#475569;line-height:1.5}}
.chips-row{{display:flex;flex-wrap:wrap;align-items:center;gap:5px;font-size:12px}}
.chips-label{{font-size:11px;font-weight:600;color:#475569;margin-right:3px}}
.chip{{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:4px;padding:3px 8px;font-size:11px;font-weight:500}}
.wl-tbl{{width:100%;border-collapse:collapse;font-size:13px}}
.wl-tbl th{{text-align:left;padding:8px 10px;background:#f8fafc;font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#94a3b8;border-bottom:2px solid #e2e8f0}}
.wl-sym{{padding:9px 10px;font-weight:700;color:#0f172a}}
.wl-trigger{{padding:9px 10px;color:#475569;font-size:12.5px}}
.badge{{display:inline-block;padding:2px 8px;border-radius:20px;color:#fff;font-size:10px;font-weight:700;letter-spacing:.3px}}
.ftr{{background:#f8fafc;padding:14px 26px;font-size:11px;color:#94a3b8;text-align:center;border-top:1px solid #e2e8f0}}
@media(max-width:480px){{.pc-row{{flex-direction:column}}}}
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
    <div class="sec-lbl">Top Stories</div>
    {stories_html}
  </div>

  <div class="sec">
    <div class="sec-lbl">Watchlist Snapshot</div>
    <table class="wl-tbl">
      <thead><tr><th>Stock</th><th>Today</th><th>Trigger</th></tr></thead>
      <tbody>{wl_rows}</tbody>
    </table>
  </div>

  <div class="ftr">Generated at 7:30 AM IST &middot; Powered by Claude &middot; Sources: Moneycontrol, Economic Times</div>
</div>
</body>
</html>"""
