#!/bin/bash
FILE=$(cat /dev/stdin | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null)

if [[ -z "$FILE" || ! -f "$FILE" ]]; then exit 0; fi

# Python files
if [[ "$FILE" == *.py ]]; then
  command -v ruff &>/dev/null && ruff format "$FILE" --quiet 2>/dev/null || true
fi

# TypeScript / JavaScript files
if [[ "$FILE" == *.ts || "$FILE" == *.tsx || "$FILE" == *.js || "$FILE" == *.jsx ]]; then
  command -v prettier &>/dev/null && prettier --write "$FILE" --quiet 2>/dev/null || true
fi

# JSON files
if [[ "$FILE" == *.json ]]; then
  command -v prettier &>/dev/null && prettier --write "$FILE" --quiet 2>/dev/null || true
fi

exit 0
