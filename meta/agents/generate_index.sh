#!/usr/bin/env bash

# Load ignore patterns
IGNORE_FILE="/home/robb/projects/maf-local/meta/agents/.agentignore"
IGNORE_PATTERNS=()
if [[ -f "$IGNORE_FILE" ]]; then
  while IFS= read -r line; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" == \#* ]] && continue
    IGNORE_PATTERNS+=("$line")
  done < "$IGNORE_FILE"
fi

# Function to check if a path matches any ignore pattern
function is_ignored() {
  local path="$1"
  for pat in "${IGNORE_PATTERNS[@]}"; do
    # Convert simple glob to regex for bash [[ ]]
    if [[ "$path" == $pat ]]; then
      return 0
    fi
  done
  return 1
}

OUTPUT_FILE="/home/robb/projects/maf-local/meta/agents/The_Real_Index.md"
> "$OUTPUT_FILE"

# Find all files and filter
while IFS= read -r -d '' file; do
  rel_path="${file#/home/robb/projects/maf-local/}"
  if is_ignored "$rel_path"; then
    continue
  fi
  # Compute hash, size, modified time
  hash=$(sha256sum "$file" | awk '{print $1}')
  size=$(stat -c %s "$file")
  modified=$(stat -c %y "$file" | cut -d'.' -f1)
  echo "$rel_path | $hash | $size | $modified" >> "$OUTPUT_FILE"
done < <(find /home/robb/projects/maf-local -type f -print0)

# Trim to first 1000 lines if needed
line_count=$(wc -l < "$OUTPUT_FILE")
if (( line_count > 1000 )); then
  head -n 1000 "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
  mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
fi

echo "Generated $OUTPUT_FILE with $(wc -l < "$OUTPUT_FILE") entries."
