#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except:
    print('')
" 2>/dev/null)

# Block direct pushes to protected branches
if echo "$COMMAND" | grep -qE "git push.*(main|master|production)(\s|$)"; then
  echo "BLOCKED: Direct push to protected branch. Push to claude/startup-improvement-plan-WOC5X and open a PR." >&2
  exit 2
fi

# Block destructive git commands
if echo "$COMMAND" | grep -qE "git (reset --hard|clean -fd|push --force)"; then
  echo "BLOCKED: Destructive git command. Confirm explicitly with the user before running this." >&2
  exit 2
fi

# Block accidental secret commits
if echo "$COMMAND" | grep -qE "git add.*(\.env|secrets|credentials)"; then
  echo "BLOCKED: Attempting to stage sensitive file. Check .gitignore." >&2
  exit 2
fi

exit 0
