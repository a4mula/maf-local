import re
import pathlib
import yaml
from typing import List, Dict, Any

SESSION_HANDOFF_PATH = pathlib.Path(__file__).parents[2] / "docs" / ".ai" / "Documentor" / "SESSION_HANDOFF.md"

# Simple parser for the handoff markdown sections
SECTION_REGEX = re.compile(r"^##\s+(.*)$", re.MULTILINE)

def read_handoff() -> str:
    """Read the SESSION_HANDOFF.md file as a string."""
    return SESSION_HANDOFF_PATH.read_text(encoding="utf-8")

def split_sections(content: str) -> Dict[str, str]:
    """Split the handoff into a dict of section title -> body text."""
    sections: Dict[str, str] = {}
    matches = list(SECTION_REGEX.finditer(content))
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections[title] = content[start:end].strip()
    return sections

def update_architecture_diagram(diagram_md: str) -> None:
    """Replace the Mermaid diagram in docs/architecture/CURRENT.md with the one from the handoff."""
    arch_path = pathlib.Path(__file__).parents[2] / "docs" / "architecture" / "CURRENT.md"
    arch_content = arch_path.read_text(encoding="utf-8")
    # Replace the first ```mermaid block we find
    new_content = re.sub(r"```mermaid[\s\S]*?```", f"```mermaid\n{diagram_md}\n```", arch_content, count=1)
    arch_path.write_text(new_content, encoding="utf-8")
    print(f"[Documentor] Updated architecture diagram in {arch_path}")

def update_file_section(section_body: str, target_path: pathlib.Path) -> None:
    """Append or replace a specific section in a markdown file.
    The handoff uses a markdown table for new/modified files; we simply append the table.
    """
    if not target_path.exists():
        target_path.write_text(section_body + "\n", encoding="utf-8")
        print(f"[Documentor] Created new doc {target_path}")
    else:
        # Simple strategy: ensure the section header exists, then replace its body.
        content = target_path.read_text(encoding="utf-8")
        header_match = re.search(r"^##\s+.*$", content, re.MULTILINE)
        if header_match:
            # Replace everything after the first header
            new_content = f"{content[:header_match.end()]}\n\n{section_body}\n"
        else:
            new_content = f"## Updated Section\n\n{section_body}\n"
        target_path.write_text(new_content, encoding="utf-8")
        print(f"[Documentor] Updated {target_path}")

def main() -> None:
    handoff = read_handoff()
    sections = split_sections(handoff)
    # 1. Architecture diagram
    if "Architecture & Relationships" in sections:
        diagram_md = sections["Architecture & Relationships"].split("```mermaid", 1)[-1].split("```", 1)[0].strip()
        update_architecture_diagram(diagram_md)
    # 2. New / Modified Files tables
    for title, body in sections.items():
        if title.startswith("New Directories & Files") or title.startswith("Modified Files"):
            # Determine target doc based on title
            target = pathlib.Path(__file__).parents[2] / "docs" / "architecture" / "CURRENT.md"
            update_file_section(body, target)
    # Additional custom handling can be added here (e.g., updating planning docs)

if __name__ == "__main__":
    main()
