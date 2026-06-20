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
import time
import socket
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

# Retry avec backoff exponentiel (Resend rate limit / instabilité réseau)
max_retries = 3
for attempt in range(max_retries):
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read().decode()
            mid = json.loads(body).get("id", "?")
            print("OK %s | Newsletter envoyée à : %s (id %s)" % (r.status, ", ".join(to), mid))
            sys.exit(0)
    except urllib.error.HTTPError as e:
        code = e.code
        err_msg = e.read().decode()
        if code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
            wait = 2 ** attempt
            print("ERREUR HTTP %s (tentative %d/%d). Retry dans %ds..." % (code, attempt + 1, max_retries, wait), file=sys.stderr)
            time.sleep(wait)
        else:
            print("ERREUR HTTP %s : %s" % (code, err_msg), file=sys.stderr)
            sys.exit(1)
    except (urllib.error.URLError, socket.timeout, OSError) as e:
        if attempt < max_retries - 1:
            wait = 2 ** attempt
            print("ERREUR RESEAU (%s) (tentative %d/%d). Retry dans %ds..." % (e.reason, attempt + 1, max_retries, wait), file=sys.stderr)
            time.sleep(wait)
        else:
            print("ERREUR RESEAU (%s) après %d tentatives." % (e.reason, max_retries), file=sys.stderr)
            sys.exit(1)
