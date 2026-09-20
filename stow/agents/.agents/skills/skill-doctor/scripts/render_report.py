#!/usr/bin/env python3
"""Render a skill-doctor report.json into one shareable HTML report.

Output (next to report.json):
  report.html - scorecard, findings, and suggested skill edits in a single
                self-contained page, with a "share as png" button that draws
                a 1200x675 share image client-side and downloads it.

Python 3.9+, stdlib only. Uses system fonts so the page and the exported PNG
render the same everywhere.
"""

import argparse
import base64
import html
import json
import re
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

GRADES = [
    (0.97, "A+"), (0.93, "A"), (0.90, "A-"),
    (0.87, "B+"), (0.83, "B"), (0.80, "B-"),
    (0.77, "C+"), (0.73, "C"), (0.70, "C-"),
    (0.60, "D"), (0.0, "F"),
]

DIFFS_BUNDLE_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "pierre-diffs.js"
)

# Collapsed height of a diff before the "show more" toggle takes over.
DIFF_CLAMP_PX = 320


def grade_for(score: float) -> str:
    for threshold, letter in GRADES:
        if score >= threshold:
            return letter
    return "F"


def pct(score) -> int:
    return round(float(score) * 100)


def format_generated_at(value) -> str:
    if not value:
        return ""
    raw = str(value)
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    if re.search(r"[+-]\d{2}$", normalized):
        normalized += ":00"
    try:
        generated_at = datetime.fromisoformat(normalized)
    except ValueError:
        return raw
    suffix = ""
    if generated_at.tzinfo is not None:
        generated_at = generated_at.astimezone(timezone.utc)
        suffix = " UTC"
    time = generated_at.strftime("%I:%M %p").lstrip("0")
    return (
        f"{generated_at.strftime('%B')} {generated_at.day}, "
        f"{generated_at.year} at {time}{suffix}"
    )


def open_report(report_path: Path) -> bool:
    try:
        return bool(webbrowser.open(report_path.absolute().as_uri(), new=2))
    except (OSError, webbrowser.Error):
        return False


def esc(v) -> str:
    value = v if v is not None else ""
    return html.escape(str(value))


def render_diff(diff_text: str, proposed_path: str = "") -> str:
    if not diff_text:
        return ""
    encoded = base64.b64encode(diff_text.encode("utf-8")).decode("ascii")
    filename = Path(proposed_path).name if proposed_path else "SKILL.md"
    return (
        '<div class="diff-wrap" data-collapsed="true">'
        f'<div class="diff-view" data-pierre-diff data-diff="{encoded}" '
        f'data-filename="{esc(filename)}">'
        f'<pre class="diff-fallback">{esc(diff_text)}</pre></div>'
        '<button class="diff-toggle" type="button" hidden>show more</button>'
        "</div>"
    )


def embedded_diffs_script() -> str:
    if not DIFFS_BUNDLE_PATH.exists():
        raise RuntimeError(
            f"@pierre/diffs bundle missing: {DIFFS_BUNDLE_PATH}; "
            "restore it from warpdotdev/skill-doctor, which builds the bundle "
            "with `pnpm build:diffs`"
        )
    bundle = DIFFS_BUNDLE_PATH.read_text()
    return re.sub(r"</script", r"<\\/script", bundle, flags=re.IGNORECASE)


# Simple mark for the report and share image. No product logo.
MARK_VIEWBOX = (32, 32)
MARK_SVG = (
    '<svg class="mark" viewBox="0 0 32 32" fill="none" '
    'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="3" y="3" width="26" height="26" stroke="currentColor" stroke-width="2"/>'
    '<path d="M9 21V11h5.2c2.4 0 3.8 1.3 3.8 3.2 0 1.9-1.4 3.2-3.8 3.2H11.6V21H9zm2.6-6.4h2.2c1 0 1.6-.5 1.6-1.4s-.6-1.4-1.6-1.4h-2.2v2.8z" fill="currentColor"/>'
    "</svg>"
)

# Sticky report footer. Local-only. No product CTA.
STAMP_NAME = "Local agent skill report"
STAMP_SUB = "transcripts stayed on this machine"

# Attribution shown only in the exported share image.
SHARE_STAMP_NAME = "Get your report with /skill-doctor"
SHARE_STAMP_SUB = "local only"

# Neutral scorecard tokens: white ground with a dot grid, monospace,
# indigo accent, hairline rules, square corners, lowercase labels.
PAGE_CSS = """
* { box-sizing: border-box; }
body {
  --mono-font: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --fg: #1a1522; --muted: #5d5966; --muted-2: #918d9a; --accent: #2a1eff;
  --line: rgba(13, 10, 61, 0.16); --line-soft: rgba(13, 10, 61, 0.07);
  --page-bg: #fff; --surface: #fff; --bg-panel: #f6f5fb; --yellow: #eef17c;
  --button-fg: #1a1522;
  --footer-shadow: rgba(13, 10, 61, 0.12);
  font-family: var(--mono-font);
  background: radial-gradient(circle at 1px 1px, var(--line-soft) 1px, transparent 0) 0 0 / 22px 22px, var(--page-bg);
  color: var(--fg); max-width: 900px; margin: 0 auto; padding: 48px 24px;
  line-height: 1.65; font-size: 13px; color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  body {
    --fg: #f4f1f8; --muted: #bbb5c2; --muted-2: #928b9b; --accent: #9188ff;
    --line: rgba(239, 235, 255, 0.2); --line-soft: rgba(239, 235, 255, 0.08);
    --page-bg: #0f0d14; --surface: #17141d; --bg-panel: #211d29;
    --footer-shadow: rgba(0, 0, 0, 0.45);
    color-scheme: dark;
  }
}
::selection { background: var(--accent); color: #fff; }
h1 { font-weight: 500; letter-spacing: -2px; font-size: 34px; margin: 4px 0 0; }
h2 { font-weight: 500; letter-spacing: -1px; font-size: 20px; margin: 40px 0 8px; }
p { color: var(--muted); font-weight: 500; }
a { color: var(--accent); }
code { background: var(--bg-panel); border: 1px solid var(--line-soft); padding: 1px 5px; }
li { margin-bottom: 10px; }
.tag { font-size: 11px; color: var(--accent); text-transform: lowercase; }
.tag::before { content: "# "; }
.muted { color: var(--muted-2); font-size: 12px; }
.stamp { display: flex; align-items: center; gap: 11px; }
.stamp .mark { width: 27px; height: 26px; flex: none; display: block; }
.stamp-name { font-size: 15px; font-weight: 600; letter-spacing: -0.03em; }
.stamp-sub { font-size: 11px; color: var(--muted-2); text-transform: lowercase; letter-spacing: 0.02em; }
.stamp-row { border: 1px solid var(--line); background: var(--surface); padding: 12px 16px; }
.report-footer { position: sticky; bottom: 16px; z-index: 20; margin-top: 40px;
  box-shadow: 0 8px 24px var(--footer-shadow); }
.row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.title-row { margin-top: 4px; }
.title-row h1 { margin: 0; }
.cta-button { font-family: inherit; font-size: 13px; font-weight: 600; color: var(--button-fg);
  background: var(--yellow); border: 1px solid var(--button-fg); padding: 8px 14px;
  text-decoration: none; white-space: nowrap; flex: none; cursor: pointer; }
.cta-button:hover { background: #f4f79f; }
.cta-button[disabled] { cursor: default; opacity: 0.65; }
.scorecard { display: flex; align-items: center; gap: 48px; border: 1px solid var(--line);
  background: var(--surface); padding: 26px 28px; margin-top: 20px; }
.grade-col { text-align: center; flex: none; width: 170px; }
.grade { font-size: 96px; font-weight: 600; line-height: 1; letter-spacing: -5px; color: var(--accent); }
.grade-label { font-size: 11px; color: var(--muted-2); margin-top: 8px; text-transform: uppercase; letter-spacing: 0.14em; }
.bars { flex: 1; display: flex; flex-direction: column; gap: 20px; min-width: 0; }
.bar-head { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 7px; font-weight: 500; }
.bar-name { text-transform: lowercase; }
.bar-val { font-weight: 600; font-variant-numeric: tabular-nums; }
.bar-track { height: 8px; background: var(--line-soft); box-shadow: inset 0 0 0 1px var(--line); }
.bar-fill { height: 100%; background: var(--accent);
  animation: skill-doctor-fill 700ms cubic-bezier(0.22, 1, 0.36, 1) var(--metric-delay) both;
  transform-origin: left; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--line);
  border-top: none; background: var(--bg-panel); }
.stat { padding: 16px 24px 14px; border-left: 1px solid var(--line); }
.stat:first-child { border-left: none; }
.stat .num { font-size: 34px; font-weight: 600; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.stat .lbl { font-size: 12px; color: var(--muted); margin-top: 2px; text-transform: lowercase; }
.diff-wrap { margin: 10px 0 4px; }
.diff-view { display: grid; gap: 10px; max-width: 100%;
  --diffs-font-family: var(--mono-font); --diffs-header-font-family: var(--mono-font); }
.diff-view > * { min-width: 0; }
.diff-fallback { background: var(--bg-panel); border: 1px solid var(--line); padding: 13px 16px;
  color: var(--muted); font-size: 12px; line-height: 1.7; overflow-x: auto; margin: 0; white-space: pre; }
.diff-wrap[data-overflowing="true"][data-collapsed="true"] .diff-view {
  max-height: __CLAMP__px; overflow: hidden;
  -webkit-mask-image: linear-gradient(#000 calc(100% - 72px), transparent);
  mask-image: linear-gradient(#000 calc(100% - 72px), transparent);
}
.diff-toggle { font-family: inherit; font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--accent); background: var(--surface);
  border: 1px solid var(--line); padding: 5px 10px; margin-top: 6px; cursor: pointer; }
.diff-toggle:hover { border-color: var(--accent); }
@keyframes skill-doctor-fill {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
@media (prefers-reduced-motion: reduce) {
  .bar-fill { animation: none; }
}
"""


def render_page(r) -> str:
    scores = r["scores"]
    stats = r.get("stats", {})
    grade = r.get("grade") or grade_for(scores["overall"])
    generated_at = format_generated_at(r.get("generated_at"))

    bars = "".join(
        f'<div class="bar-row"><div class="bar-head"><span class="bar-name">{esc(name)}</span>'
        f'<span class="bar-val">{pct(val)}</span></div>'
        f'<div class="bar-track"><div class="bar-fill" '
        f'style="width:{pct(val)}%;--metric-delay:{180 + index * 110}ms"></div></div></div>'
        for index, (name, val) in enumerate([
            ("Efficiency", scores.get("efficiency", 0)),
            ("Code Quality", scores.get("code_quality", 0)),
            ("Procedure Compliance", scores.get("procedure_compliance", 0)),
            ("Verbosity", scores.get("verbosity", 0)),
            ("Skill Coverage", scores.get("skill_coverage", 0)),
        ])
    )
    stat_cells = "".join(
        f'<div class="stat"><div class="num">{esc(value)}</div><div class="lbl">{esc(label)}</div></div>'
        for value, label in [
            (stats.get("sessions_analyzed", 0), "conversations scored"),
            (stats.get("skills_found", 0), "skills installed"),
            (stats.get("skills_used", 0), "skills used"),
        ]
    )
    findings = "".join(f"<li>{esc(finding)}</li>" for finding in r.get("top_findings", []))
    suggestions = "".join(
        f"""<li><b><code>{esc(s.get('skill'))}</code></b> — {esc(s.get('change'))}
        {('<div class="muted">Evidence: ' + esc(s['evidence']) + '</div>') if s.get('evidence') else ''}
        {render_diff(s.get('diff', ''), s.get('proposed_path', ''))}</li>"""
        for s in r.get("suggestions", [])
    ) or "<li>No skill change cleared the bar for this window.</li>"

    card_data = json.dumps({
        "title": r.get("title", "Agent Skill Report"),
        "eyebrow": "skill-doctor",
        "handle": r.get("handle") or "agent skill report",
        "harness": r.get("harness", "codex"),
        "grade": grade,
        "grade_label": f"overall {pct(scores['overall'])}",
        "bars": [
            ["Efficiency", pct(scores.get("efficiency", 0))],
            ["Code Quality", pct(scores.get("code_quality", 0))],
            ["Procedure Compliance", pct(scores.get("procedure_compliance", 0))],
            ["Verbosity", pct(scores.get("verbosity", 0))],
            ["Skill Coverage", pct(scores.get("skill_coverage", 0))],
        ],
        "meta": f"{stats.get('sessions_scanned', 0)} conversations found \u00b7 "
                f"last {stats.get('window_days', 45)} days",
        "stats": [
            [str(stats.get("sessions_analyzed", 0)), "conversations scored"],
            [str(stats.get("skills_found", 0)), "skills installed"],
            [str(stats.get("skills_used", 0)), "skills used"],
        ],
        "stamp": [SHARE_STAMP_NAME, SHARE_STAMP_SUB],
        "viewbox": list(MARK_VIEWBOX),
    })

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="color-scheme" content="light dark">
<title>{esc(r.get('title', 'Agent Skill Report'))}</title>
<style>{PAGE_CSS.replace('__CLAMP__', str(DIFF_CLAMP_PX))}</style></head><body>
<div class="tag">skill-doctor</div>
<div class="row title-row">
  <h1>{esc(r.get('title', 'Agent Skill Report'))}</h1>
  <button class="cta-button" id="share-png" type="button">Share</button>
</div>
<p class="muted">Generated {esc(generated_at)} &middot; harness: {esc(r.get('harness', 'codex'))}</p>
<div class="scorecard">
  <div class="grade-col"><div class="grade">{esc(grade)}</div>
    <div class="grade-label">overall {pct(scores['overall'])}</div></div>
  <div class="bars">{bars}</div>
</div>
<div class="stats">{stat_cells}</div>
<h2>Findings</h2><ul>{findings}</ul>
<h2>Suggested skill changes</h2><ol>{suggestions}</ol>
<div class="stamp-row row report-footer">
  <div class="stamp">{MARK_SVG}<div>
    <div class="stamp-name">{esc(STAMP_NAME)}</div>
    <div class="stamp-sub">{esc(STAMP_SUB)}</div>
  </div></div>
</div>
<script>{embedded_diffs_script()}</script>
<script>{page_script(card_data)}</script>
</body></html>"""


def page_script(card_data: str) -> str:
    """Diff collapsing plus a canvas-drawn 1200x675 share image."""
    script = r"""
(function () {
  var CARD = __CARD__;
  var CLAMP = __CLAMP__;

  // --- collapsible diffs -------------------------------------------------
  // scrollHeight is the full content height whether or not the view is
  // currently clamped, so this measures the same either way. Only diffs that
  // actually overflow get clamped, so short ones never pick up the fade.
  function syncToggle(wrap, button) {
    var view = wrap.querySelector('.diff-view');
    if (!view) return;
    var overflowing = view.scrollHeight > CLAMP + 24;
    wrap.dataset.overflowing = overflowing ? 'true' : 'false';
    button.hidden = !overflowing;
  }

  document.querySelectorAll('.diff-wrap').forEach(function (wrap) {
    var button = wrap.querySelector('.diff-toggle');
    var view = wrap.querySelector('.diff-view');
    if (!button || !view) return;
    button.addEventListener('click', function () {
      var collapsed = wrap.dataset.collapsed === 'true';
      wrap.dataset.collapsed = collapsed ? 'false' : 'true';
      button.textContent = collapsed ? 'show less' : 'show more';
      if (!collapsed) wrap.scrollIntoView({ block: 'nearest' });
    });
    syncToggle(wrap, button);
    if (window.ResizeObserver) {
      new ResizeObserver(function () { syncToggle(wrap, button); }).observe(view);
    }
  });

  // --- share image -------------------------------------------------------
  var MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';
  var FG = '#1a1522', MUTED = '#5d5966', MUTED2 = '#918d9a', ACCENT = '#2a1eff';
  var LINE = 'rgba(13,10,61,0.16)', LINE_SOFT = 'rgba(13,10,61,0.07)';
  var PANEL = '#f6f5fb';
  var W = 1200, H = 675;

  function drawMark(c, x, y, size) {
    c.save();
    c.strokeStyle = FG;
    c.lineWidth = 2;
    c.strokeRect(x, y, size, size);
    c.fillStyle = FG;
    font('600', 16);
    text('sd', x + size / 2, y + size / 2, 'center');
    c.restore();
  }

  function drawCard(scale) {
    var canvas = document.createElement('canvas');
    canvas.width = W * scale;
    canvas.height = H * scale;
    var c = canvas.getContext('2d');
    c.scale(scale, scale);

    function font(weight, size) { c.font = weight + ' ' + size + 'px ' + MONO; }
    function track(value) { try { c.letterSpacing = value; } catch (e) {} }
    function rule(x, y, w, h) { c.fillStyle = LINE; c.fillRect(x, y, w, h); }
    function text(str, x, y, align) {
      c.textAlign = align || 'left';
      c.textBaseline = 'middle';
      c.fillText(str, x, y);
      c.textAlign = 'left';
    }
    function dots(x, y, w, h, step) {
      c.save();
      c.beginPath();
      c.rect(x, y, w, h);
      c.clip();
      c.fillStyle = LINE_SOFT;
      for (var i = x; i < x + w; i += step) {
        for (var j = y; j < y + h; j += step) {
          c.beginPath();
          c.arc(i + 1, j + 1, 1, 0, Math.PI * 2);
          c.fill();
        }
      }
      c.restore();
    }

    c.fillStyle = '#fff';
    c.fillRect(0, 0, W, H);
    dots(0, 0, W, H, 22);

    var fx = 48, fy = 40, fw = 1104, fh = 595;
    c.fillStyle = '#fff';
    c.fillRect(fx, fy, fw, fh);
    rule(fx, fy, fw, 1);
    rule(fx, fy + fh - 1, fw, 1);
    rule(fx, fy, 1, fh);
    rule(fx + fw - 1, fy, 1, fh);

    // meta bar
    var barBottom = fy + 38;
    rule(fx, barBottom, fw, 1);
    font('400', 11);
    track('1.1px');
    c.fillStyle = MUTED2;
    var handle = CARD.handle.toUpperCase();
    text(handle, fx + 16, fy + 19);
    var handleEnd = fx + 16 + c.measureText(handle).width + 14;
    var harness = CARD.harness.toUpperCase();
    var harnessW = c.measureText(harness).width + 12;
    var harnessX = fx + fw - 16 - harnessW;
    c.strokeStyle = LINE;
    c.lineWidth = 1;
    c.strokeRect(harnessX + 0.5, fy + 8.5, harnessW - 1, 21);
    text(harness, harnessX + 6, fy + 19);
    var meta = CARD.meta.toUpperCase();
    var metaX = harnessX - 14 - c.measureText(meta).width;
    text(meta, metaX, fy + 19);
    rule(handleEnd, fy + 19, Math.max(0, metaX - 14 - handleEnd), 1);
    track('normal');

    // body
    dots(fx + 1, barBottom + 1, fw - 2, 404, 26);
    font('400', 11);
    track('0.4px');
    c.fillStyle = ACCENT;
    text('# ' + CARD.eyebrow, fx + 36, barBottom + 18);
    font('500', 34);
    track('-2px');
    c.fillStyle = FG;
    text(CARD.title, fx + 36, barBottom + 52);
    track('normal');

    var mainMid = barBottom + 74 + (405 - 74) / 2;

    font('600', 170);
    track('-8px');
    c.fillStyle = ACCENT;
    text(CARD.grade, fx + 186, mainMid - 15, 'center');
    track('normal');
    font('400', 11);
    track('1.5px');
    c.fillStyle = MUTED2;
    text(CARD.grade_label.toUpperCase(), fx + 186, mainMid + 88, 'center');
    track('normal');

    var bx = fx + 392;
    var bw = fx + fw - 36 - bx;
    var rowH = 35, gap = CARD.bars.length > 3 ? 12 : 28;
    var top = mainMid - (CARD.bars.length * rowH + (CARD.bars.length - 1) * gap) / 2;
    CARD.bars.forEach(function (bar, index) {
      var y = top + index * (rowH + gap);
      font('500', 14);
      c.fillStyle = FG;
      text(bar[0].toLowerCase(), bx, y + 9);
      font('600', 14);
      text(String(bar[1]), bx + bw, y + 9, 'right');
      c.fillStyle = LINE_SOFT;
      c.fillRect(bx, y + 27, bw, 8);
      c.strokeStyle = LINE;
      c.strokeRect(bx + 0.5, y + 27.5, bw - 1, 7);
      c.fillStyle = ACCENT;
      c.fillRect(bx, y + 27, bw * Math.max(0, Math.min(100, bar[1])) / 100, 8);
    });

    // stats
    var sy = barBottom + 405;
    c.fillStyle = PANEL;
    c.fillRect(fx + 1, sy, fw - 2, 96);
    rule(fx, sy, fw, 1);
    var colW = (fw - 2) / 3;
    CARD.stats.forEach(function (stat, index) {
      var cx = fx + 1 + index * colW;
      if (index) rule(cx, sy, 1, 96);
      font('600', 40);
      c.fillStyle = FG;
      text(stat[0], cx + 24, sy + 40);
      font('400', 12);
      c.fillStyle = MUTED;
      text(stat[1], cx + 24, sy + 72);
    });

    // footer
    var gy = sy + 96;
    c.fillStyle = '#fff';
    c.fillRect(fx + 1, gy, fw - 2, fy + fh - gy - 1);
    rule(fx, gy, fw, 1);
    drawMark(c, fx + 16, gy + 15, 27);
    font('600', 15);
    track('-0.45px');
    c.fillStyle = FG;
    text(CARD.stamp[0], fx + 54, gy + 20);
    track('normal');
    font('400', 11);
    c.fillStyle = MUTED2;
    text(CARD.stamp[1], fx + 54, gy + 37);

    return canvas;
  }

  function slug(value) {
    return (value || '').toLowerCase().replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'agent';
  }

  var button = document.getElementById('share-png');
  button.addEventListener('click', function () {
    var label = button.textContent;
    button.disabled = true;
    var ready = (document.fonts && document.fonts.ready) || Promise.resolve();
    ready.then(function () {
      drawCard(2).toBlob(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = slug(CARD.handle) + '-skill-report.png';
        a.click();
        setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
        button.disabled = false;
        button.textContent = 'saved \u2713';
        setTimeout(function () { button.textContent = label; }, 2000);
      }, 'image/png');
    });
  });
})();
"""
    return script.replace("__CARD__", card_data.replace("</", "<\\/")).replace("__CLAMP__", str(DIFF_CLAMP_PX))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report_path",
        nargs="?",
        default="./skill-doctor-report/report.json",
        help="Path to the report.json file",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="Open the generated report in the default browser",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    report_path = Path(args.report_path).expanduser()
    if not report_path.exists():
        print(f"error: {report_path} not found", file=sys.stderr)
        sys.exit(1)
    r = json.loads(report_path.read_text())
    r.setdefault("grade", grade_for(r["scores"]["overall"]))

    out_path = report_path.parent / "report.html"
    out_path.write_text(render_page(r))
    print(f"report: {out_path.absolute().as_uri()}")
    if args.open_browser:
        if open_report(out_path):
            print("        opened in the default browser")
        else:
            print(
                "warning: could not open the report in the default browser",
                file=sys.stderr,
            )
    print('        use "share as png" for a 1200x675 share image')


if __name__ == "__main__":
    main()
