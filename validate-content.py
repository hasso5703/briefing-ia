#!/usr/bin/env python3
"""Validation du schema content.json pour Briefing IA."""
import json
import sys

REQUIRED_KEYS = {"date_long", "edition", "intro", "sections"}
VALID_STATUSES = {"ok", "warn", "no"}

def validate(data, path=""):
    errors = []
    if not isinstance(data, dict):
        return [f"{path}: attendu un objet JSON"]
    for key in REQUIRED_KEYS:
        if key not in data:
            errors.append(f"{path}: clé manquante '{key}'")
    # sections
    sections = data.get("sections", [])
    if not isinstance(sections, list):
        errors.append(f"{path}.sections: attendu un tableau")
    else:
        for i, sec in enumerate(sections):
            if not isinstance(sec, dict):
                errors.append(f"{path}.sections[{i}]: attendu un objet")
                continue
            for k in ("rank", "kicker", "title", "items"):
                if k not in sec:
                    errors.append(f"{path}.sections[{i}]: clé manquante '{k}'")
            items = sec.get("items", [])
            if not isinstance(items, list):
                errors.append(f"{path}.sections[{i}].items: attendu un tableau")
            else:
                for j, item in enumerate(items):
                    if not isinstance(item, dict):
                        errors.append(f"{path}.sections[{i}].items[{j}]: attendu un objet")
                        continue
                    for k in ("title", "status", "dateline", "body"):
                        if k not in item:
                            errors.append(f"{path}.sections[{i}].items[{j}]: clé manquante '{k}'")
                    if item.get("status") not in VALID_STATUSES:
                        errors.append(f"{path}.sections[{i}].items[{j}].status: valeur invalide '{item.get('status')}'")
    # signaux
    for i, sig in enumerate(data.get("signaux", [])):
        if isinstance(sig, dict):
            if sig.get("status") not in VALID_STATUSES:
                errors.append(f"{path}.signaux[{i}].status: invalide")
    # enbref
    for i, b in enumerate(data.get("enbref", [])):
        if isinstance(b, dict):
            if "lead" not in b or "text" not in b:
                errors.append(f"{path}.enbref[{i}]: clés 'lead' et 'text' requises")
    return errors

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/content.json"
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERREUR JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERREUR: fichier non trouvé: {path}", file=sys.stderr)
        sys.exit(1)

    errs = validate(data)
    if errs:
        print("VALIDATION ÉCHOUÉ:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("VALIDATION OK")
    sys.exit(0)
