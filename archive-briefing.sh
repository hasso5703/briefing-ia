#!/usr/bin/env bash
set -e
# Archive le contenu et le HTML du briefing dans le repo (persistant)
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
ARCHIVE_DIR="$REPO_DIR/archives"
DATE=$(date +%Y-%m-%d)
DEST="$ARCHIVE_DIR/$DATE"
mkdir -p "$DEST"
cp /tmp/content.json "$DEST/"
cp /tmp/newsletter.html "$DEST/"
cd "$REPO_DIR"
git add -A
git diff --cached --quiet || git commit -m "Archive: $DATE" >/dev/null 2>&1 || true
echo "Archive: $DEST"
