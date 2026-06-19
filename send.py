#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envoi de la newsletter Briefing IA via Resend.

Aucun secret en dur ici (ce fichier est public) : la clé et les destinataires
viennent de l'environnement, fournis par le message de la routine.

Usage :
    RESEND_API_KEY=re_xxx RESEND_TO=a@b.com[,c@d.com] python3 send.py

Variables :
    RESEND_API_KEY   (requis)  clé API Resend
    RESEND_TO        (requis)  destinataire(s), séparés par des virgules
    RESEND_FROM      (option)  défaut: "Briefing IA <onboarding@resend.dev>"
    RESEND_SUBJECT   (option)  défaut: "📰 Briefing IA · <YYYY-MM-DD>"
    NEWSLETTER_HTML  (option)  défaut: /tmp/newsletter.html
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

key = os.environ.get("RESEND_API_KEY", "").strip()
to = [x.strip() for x in os.environ.get("RESEND_TO", "").split(",") if x.strip()]
sender = os.environ.get("RESEND_FROM", "Briefing IA <onboarding@resend.dev>").strip()
path = os.environ.get("NEWSLETTER_HTML", "/tmp/newsletter.html")

if not key or not to:
    print("ERREUR: RESEND_API_KEY et RESEND_TO sont requis.", file=sys.stderr)
    sys.exit(2)

date = subprocess.check_output(["date", "+%Y-%m-%d"]).decode().strip()
hour = int(subprocess.check_output(["date", "-u", "+%H"]).decode().strip())
slot = "matin" if hour < 8 else ("midi" if hour < 15 else "soir")
subject = os.environ.get("RESEND_SUBJECT", "📰 Briefing IA · %s · %s" % (slot, date))

with open(path, encoding="utf-8") as f:
    html = f.read()

if not html.strip():
    print("ERREUR: %s est vide." % path, file=sys.stderr)
    sys.exit(2)

payload = json.dumps({
    "from": sender,
    "to": to,
    "subject": subject,
    "html": html,
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.resend.com/emails",
    data=payload,
    headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) BriefingIA/1.0",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req) as r:
        body = r.read().decode()
        mid = json.loads(body).get("id", "?")
        print("OK %s | Newsletter envoyée à : %s (id %s)" % (r.status, ", ".join(to), mid))
except urllib.error.HTTPError as e:
    print("ERREUR HTTP %s : %s" % (e.code, e.read().decode()), file=sys.stderr)
    sys.exit(1)
