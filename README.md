# Briefing IA

Builder déterministe (**données → HTML**) pour la newsletter quotidienne **Briefing IA**,
envoyée chaque soir par une routine Claude Code (agent cloud) via Resend.

Le but : **figer le template hors du prompt**. Le shell HTML, le CSS et la structure
vivent dans `render.py`. L'agent ne produit **que des données** (`content.json`) ;
il ne génère jamais de HTML. Résultat : un rendu identique à chaque exécution (zéro drift).

## Fichiers

- **`PROMPT.md`** : le protocole complet exécuté par l'agent cloud (recherche, contenu, rendu, envoi). La routine se contente de dire « lis PROMPT.md et exécute ».
- **`render.py`** : le builder figé (shell + CSS + structure). Données → HTML.
- **`send.py`** : envoi via Resend (clé et destinataires lus dans l'environnement, aucun secret en dur).
- **`sample-content.json`** : exemple de données complet.
- **`briefing-template.html`** : rendu de référence figé (design).

## Usage

```bash
python3 render.py content.json > newsletter.html
RESEND_API_KEY=re_xxx RESEND_TO=a@b.com python3 send.py
```

Aucune dépendance (stdlib uniquement). Testé avec `sample-content.json`.

## Schéma de `content.json`

```json
{
  "date_long": "Jeudi 18 juin 2026",
  "edition":   "Édition du soir",
  "intro":     "Une à deux phrases de chapô.",
  "sections": [
    {
      "rank": "01",
      "kicker": "impact maximal",
      "title": "Coupure de service & régulation",
      "items": [
        {
          "title": "Titre de la brève",
          "status": "ok | warn | no",
          "dateline": "Événement : 12 juin · point au 18 juin",
          "body": "2 à 4 phrases factuelles.",
          "sources": [ { "name": "CNBC", "url": "https://..." } ]
        }
      ]
    }
  ],
  "signaux": [ { "title": "...", "status": "warn", "body": "..." } ],
  "enbref":  [ { "lead": "IPO record.", "text": "..." } ]
}
```

## Conventions

- **Statut de fiabilité** (seule couleur de la page) :
  - `ok` → ✅ RECOUPÉ (≥3 sources ou source primaire)
  - `warn` → ⚠️ À CONFIRMER (source unique)
  - `no` → ❌ NON VÉRIFIÉ
- **Sections ordonnées par impact** (`rank` = rang d'impact, pas l'ordre d'apparition).
- **`signaux`** = rumeurs / fuites / non officiel, clairement taggés.
- **Aucun em-dash (—) ni en-dash (–)** dans le contenu (ça fait « généré par IA »).
  Le builder les neutralise en filet de sécurité, mais le contenu ne doit pas en produire.

## Aperçu du design

Identité « dispatch de renseignement vérifié » : encre sur papier, Georgia + monospace,
**la seule couleur est le statut de vérification**. Le fichier `briefing-template.html`
est un rendu de référence figé (pour éditer le design ou prévisualiser).

## Modifier le design

Éditer le shell / CSS dans `render.py` (constante `HEAD` et fonctions `render_*`),
puis re-tester avec `python3 render.py sample-content.json > out.html`.
La routine cloud reclone ce repo à chaque run : tout changement poussé ici est pris en compte au prochain envoi.
