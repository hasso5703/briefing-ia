#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Briefing IA — builder déterministe.

Le shell HTML, le CSS et la structure sont FIGÉS dans ce fichier.
L'agent ne fournit QUE des données (content.json) : il ne produit jamais de HTML.
Cela garantit un template identique à chaque exécution (zéro drift).

Usage:
    python3 render.py content.json > newsletter.html

Schéma de content.json :
{
  "date_long": "Jeudi 18 juin 2026",
  "edition":   "Édition du soir",
  "intro":     "Une à deux phrases de chapô.",
  "sections": [
    {
      "rank": "01", "kicker": "impact maximal",
      "title": "Coupure de service & régulation",
      "items": [
        {
          "title": "...",
          "status": "ok" | "warn" | "no",
          "dateline": "Événement : 12 juin · point au 18 juin",
          "body": "2 à 4 phrases factuelles.",
          "sources": [ {"name": "CNBC", "url": "https://..."} ]
        }
      ]
    }
  ],
  "signaux": [ {"title": "...", "status": "warn", "body": "..."} ],
  "enbref":  [ {"lead": "IPO record.", "text": "..."} ]
}

Règles :
- status : ok=✅ RECOUPÉ, warn=⚠️ À CONFIRMER, no=❌ NON VÉRIFIÉ.
- AUCUN em-dash (—) ni en-dash (–) : le builder les neutralise en filet de sécurité,
  mais le contenu ne doit pas en contenir (utiliser virgules, parenthèses, deux-points).
"""

import sys
import json
import html


def norm(s):
    """Filet anti-tirets-longs : aucun — ou – dans le rendu final."""
    if s is None:
        return ""
    s = str(s)
    s = s.replace(" — ", ", ").replace(" – ", ", ")
    s = s.replace("—", ", ").replace("–", "-").replace("--", ", ")
    return s


def esc(s):
    return html.escape(norm(s), quote=False)


def esc_up(s):
    return html.escape(norm(s).upper(), quote=False)


STATUS = {
    "ok":   ("b-ok",   "✅ RECOUPÉ",      "✅"),
    "warn": ("b-warn", "⚠️ À CONFIRMER",  "⚠️"),
    "no":   ("b-no",   "❌ NON VÉRIFIÉ",  "❌"),
}


def status(s):
    return STATUS.get((s or "ok").lower(), STATUS["ok"])


HEAD = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light only">
<title>Briefing IA</title>
<style>
  * { box-sizing:border-box; }
  body { margin:0; padding:0; background:#EFEDE7; -webkit-text-size-adjust:100%; }
  a { color:#17150F; text-decoration:none; border-bottom:1px solid #C9C4B7; }
  .frame { background:#EFEDE7; }
  .frame-pad { padding:30px 14px; }
  .paper { width:100%; max-width:600px; background:#FAF9F7; }

  .rule-top { height:5px; background:#17150F; font-size:0; line-height:0; }
  .masthead { padding:36px 38px 0 38px; }
  .kicker { font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; font-size:10.5px; letter-spacing:0.26em; text-transform:uppercase; color:#8A8678; margin:0 0 16px 0; }
  .wordmark { font-family:Georgia,"Times New Roman",serif; font-weight:700; font-size:44px; line-height:0.98; letter-spacing:-0.015em; color:#17150F; margin:0; }
  .dateline { font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; font-size:12px; letter-spacing:0.05em; color:#6E6A5E; margin:16px 0 0 0; }
  .rule-double { border-top:2px solid #17150F; border-bottom:1px solid #17150F; height:3px; margin:18px 38px 0 38px; font-size:0; line-height:0; }

  .standfirst { font-family:Georgia,serif; font-style:italic; font-size:17px; line-height:1.52; color:#2A2820; padding:24px 38px 0 38px; margin:0; }

  .legend { padding:20px 38px 0 38px; }
  .legend span.badge { margin:0 10px 0 0; }
  .legend small { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:10px; color:#8A8678; letter-spacing:0.04em; }

  .section { padding:34px 38px 0 38px; }
  .eyebrow { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:11px; letter-spacing:0.2em; text-transform:uppercase; color:#8A8678; margin:0 0 6px 0; }
  .eyebrow b { color:#17150F; font-weight:700; }
  .sec-title { font-family:Georgia,serif; font-weight:700; font-size:13px; letter-spacing:0.14em; text-transform:uppercase; color:#17150F; margin:0; padding-bottom:11px; border-bottom:1.5px solid #17150F; }

  .item { padding-top:22px; }
  .item-title { font-family:Georgia,serif; font-weight:700; font-size:20px; line-height:1.27; color:#17150F; margin:0 0 11px 0; }
  .badge { display:inline-block; font-family:ui-monospace,Menlo,Consolas,monospace; font-size:10.5px; font-weight:700; letter-spacing:0.05em; padding:3px 8px; border-radius:3px; white-space:nowrap; }
  .b-ok   { color:#2E7D4F; background:#E7F0EA; }
  .b-warn { color:#9C6B16; background:#F5EAD2; }
  .b-no   { color:#B23A33; background:#F6E3E1; }
  .meta { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:11px; letter-spacing:0.02em; color:#6E6A5E; margin:0 0 11px 0; }
  .meta .badge { margin-right:10px; }
  .body { font-family:-apple-system,"Helvetica Neue",Arial,sans-serif; font-size:15px; line-height:1.62; color:#2C2A22; margin:0 0 11px 0; }
  .sources { font-family:-apple-system,Arial,sans-serif; font-size:12px; line-height:1.55; color:#6E6A5E; margin:0; }
  .sources .lbl { font-family:ui-monospace,Menlo,Consolas,monospace; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; font-size:9.5px; color:#17150F; margin-right:6px; }
  .item-div { border-top:1px solid #E3DFD6; margin-top:24px; font-size:0; line-height:0; }

  .weak { margin:38px 0 0 0; background:#F1EFE7; border-top:1.5px solid #17150F; border-bottom:1.5px solid #17150F; padding-bottom:28px; }
  .weak .section { padding-top:26px; }
  .weak-item { padding:16px 38px 0 38px; }
  .weak-item .wt { font-family:Georgia,serif; font-weight:700; font-size:15px; color:#17150F; }
  .weak-item .wbadge { margin-left:6px; }
  .weak-item .wb { font-family:-apple-system,Arial,sans-serif; font-size:13.5px; line-height:1.56; color:#3A382F; margin:6px 0 0 0; }

  .brief { padding-top:6px; }
  .brief-li { padding:13px 38px 0 38px; }
  .brief-li .mk { font-family:ui-monospace,Menlo,Consolas,monospace; color:#17150F; font-size:13px; font-weight:700; padding-right:13px; vertical-align:top; line-height:1.55; }
  .brief-li .tx { font-family:-apple-system,Arial,sans-serif; font-size:13.5px; line-height:1.56; color:#2C2A22; }
  .brief-li .tx b { color:#17150F; }

  .footer { padding:32px 38px 38px 38px; margin-top:36px; border-top:5px solid #17150F; }
  .footer p { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:10px; line-height:1.75; letter-spacing:0.02em; color:#9A9587; margin:0 0 9px 0; }
  .footer .sig { color:#6E6A5E; font-size:11px; letter-spacing:0.16em; text-transform:uppercase; }

  @media only screen and (max-width:480px) {
    .masthead, .standfirst, .legend, .section, .weak-item, .brief-li, .footer { padding-left:22px !important; padding-right:22px !important; }
    .rule-double { margin-left:22px !important; margin-right:22px !important; }
    .wordmark { font-size:34px !important; }
    .item-title { font-size:18px !important; }
  }
</style>
</head>
<body>
<table role="presentation" class="frame" width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td class="frame-pad" align="center">
<table role="presentation" class="paper" align="center" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:0;">
    <div class="rule-top">&nbsp;</div>
"""

FOOTER = """    <div class="footer">
      <p class="sig">Briefing IA</p>
      <p>Généré automatiquement. Sources vérifiées et recoupées, hiérarchisées par impact. Les dates sont celles des événements, pas des publications.</p>
      <p>Les tags ⚠️ et ❌ signalent une information non confirmée par une source primaire : ne pas les traiter comme des faits établis. Les montants financiers restent prudents tant qu'ils ne sont pas confirmés par un dépôt officiel.</p>
    </div>"""

TAIL = """
</td></tr></table>
</td></tr></table>
</body>
</html>
"""


def render_sources(srcs):
    out = []
    for s in (srcs or []):
        name = esc(s.get("name"))
        url = (s.get("url") or "").strip()
        if url and url != "#":
            out.append('<a href="%s">%s</a>' % (html.escape(url, quote=True), name))
        else:
            out.append(name)
    return ", ".join(out)


def render_item(it, last):
    cls, label, _ = status(it.get("status"))
    rows = [
        '      <div class="item">',
        '        <p class="item-title">%s</p>' % esc(it.get("title")),
        '        <p class="meta"><span class="badge %s">%s</span> %s</p>' % (cls, label, esc_up(it.get("dateline"))),
        '        <p class="body">%s</p>' % esc(it.get("body")),
        '        <p class="sources"><span class="lbl">Sources</span> %s</p>' % render_sources(it.get("sources")),
    ]
    if not last:
        rows.append('        <div class="item-div">&nbsp;</div>')
    rows.append('      </div>')
    return "\n".join(rows)


def render_section(sec):
    rows = [
        '    <div class="section">',
        '      <p class="eyebrow"><b>%s</b> · %s</p>' % (esc(sec.get("rank")), esc(sec.get("kicker"))),
        '      <p class="sec-title">%s</p>' % esc(sec.get("title")),
        '',
    ]
    items = sec.get("items") or []
    for i, it in enumerate(items):
        rows.append(render_item(it, i == len(items) - 1))
        rows.append('')
    rows.append('    </div>')
    return "\n".join(rows)


def render_weak(signaux):
    if not signaux:
        return ""
    rows = [
        '    <div class="weak">',
        '      <div class="section">',
        '        <p class="eyebrow"><b>🔍</b> · non officiel</p>',
        '        <p class="sec-title">Signaux faibles · à surveiller</p>',
        '      </div>',
    ]
    for s in signaux:
        cls, _, tag = status(s.get("status"))
        rows.append('      <div class="weak-item">')
        rows.append('        <span class="wt">%s</span><span class="badge %s wbadge">%s</span>' % (esc(s.get("title")), cls, tag))
        rows.append('        <p class="wb">%s</p>' % esc(s.get("body")))
        rows.append('      </div>')
    rows.append('    </div>')
    return "\n".join(rows)


def render_brief(items):
    if not items:
        return ""
    rows = [
        '    <div class="section brief">',
        '      <p class="eyebrow"><b>+</b> · le reste</p>',
        '      <p class="sec-title">En bref</p>',
    ]
    for b in items:
        lead = esc(b.get("lead"))
        text = esc(b.get("text"))
        lead_html = ('<b>%s</b> ' % lead) if lead else ''
        rows.append('      <div class="brief-li"><table role="presentation" cellpadding="0" cellspacing="0"><tr><td class="mk">→</td><td class="tx">%s%s</td></tr></table></div>' % (lead_html, text))
    rows.append('    </div>')
    return "\n".join(rows)


def render_top(data):
    dl = esc_up(data.get("date_long")) + " · " + esc_up(data.get("edition") or "Édition du soir")
    return "\n".join([
        '    <div class="masthead">',
        '      <p class="kicker">Veille IA · vérifiée · hiérarchisée par impact</p>',
        '      <p class="wordmark">Briefing IA</p>',
        '      <p class="dateline">%s</p>' % dl,
        '    </div>',
        '    <div class="rule-double">&nbsp;</div>',
        '',
        '    <p class="standfirst">%s</p>' % esc(data.get("intro")),
        '',
        '    <div class="legend">',
        '      <span class="badge b-ok">✅ RECOUPÉ</span><span class="badge b-warn">⚠️ À CONFIRMER</span><span class="badge b-no">❌ NON VÉRIFIÉ</span>',
        '      <br><br><small>✅ ≥3 sources ou primaire &nbsp;·&nbsp; ⚠️ source unique &nbsp;·&nbsp; ❌ non recoupé</small>',
        '    </div>',
    ])


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "content.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    out = [HEAD, render_top(data)]
    for sec in (data.get("sections") or []):
        out.append(render_section(sec))
    out.append(render_weak(data.get("signaux")))
    out.append(render_brief(data.get("enbref")))
    out.append(FOOTER)
    out.append(TAIL)

    html_doc = "\n".join(part for part in out if part)
    sys.stdout.write(html_doc)


if __name__ == "__main__":
    main()
