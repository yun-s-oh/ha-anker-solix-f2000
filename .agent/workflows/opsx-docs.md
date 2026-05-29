---
description: Update, review, and validate project and API documentation following OpenSpec standards
---

Update and validate repository documentation (including READMEs, Custom Component setup guides, BLE protocol matrix, and automated agent guidelines) to ensure it perfectly matches the system implementation.

**Input**: Optionally specify a documentation file or target area (e.g., `/opsx:docs README.md` or `/opsx:docs protocol`). If omitted, the agent will analyze the changes and codebase status to determine which documents require synchronization.

---

## Steps

### 1. Identify Outdated Documentation
Identify which files are out of sync with current code, specifications, or user features:
- Core Readme: `README.md`
- Change Proposal: `openspec/changes/<name>/proposal.md`
- Active Specifications: `openspec/changes/<name>/specs/**/*.md`
- Agent Guidelines: `openspec/changes/<name>/specs/agent-guidelines/spec.md`
- Protocol matrix: `openspec/changes/<name>/specs/ble-protocol/spec.md`

### 2. Pre-Update Verification
Before writing or modifying documentation, review the source code and specs:
- **Code Alignment**: Read the actual implementation (e.g. Python code, JSON schemas) to ensure telemetry byte offsets, parameter names, and configurations match the documentation.
- **Spec Consistency**: Check the active OpenSpec design and proposal files to ensure scope alignment.

### 3. Apply Markdown Standards
All documentation must maintain a highly premium visual aesthetic and structured readability:
- **Headers**: Maintain a clean hierarchical header structure (`#`, `##`, `###`, etc.). Never skip levels.
- **Alerts**: Use standard GitHub-style alerts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`) for highlighting important information.
- **Formatting**:
  - Keep sentences short, clear, and direct.
  - Wrap code examples in appropriate fenced code blocks with language identifiers.
  - Format telemetry matrices, byte offsets, and decoding registers in clean markdown tables.
  - Use visual diagrams (Mermaid or ASCII flowcharts) to illustrate complex architecture or BLE communication sequences.

### 4. Perform the Update
Create or edit the documentation files:
- Use precise file operations to update specific sections without disrupting unrelated documentation.
- Do not use placeholders or outdated assumptions.
- Reference other files using standard Markdown links (e.g. `[README](file:///Users/yunseokoh/Projects/ha-anker-solix-f2000/README.md)`).

### 5. Validate the Assets
Verify the updated documentation:
- **Links**: Ensure all relative and absolute links in the markdown files are valid.
- **Render Check**: Verify that there are no broken markdown syntax errors (e.g., incomplete code fences, unclosed brackets, or malformed tables).

### 6. Commit the Updates
Once validated, stage and commit the updated documentation using the `/opsx-commit` workflow:
```bash
git add docs/ README.md
git commit -m "docs: update BLE protocol documentation and setup guides"
```

---

## Output During Execution

```
## Initiating Documentation Update

### Step 1: Scanning Documentation Assets
Analyzing differences between codebase and documentation...
Out of sync detected:
- openspec/changes/anker-solix-ble-hacs/specs/ble-protocol/spec.md (needs telemetry byte offset updates)
- README.md (needs setup guide updates)

### Step 2: Updating Assets
✓ Updated: openspec/changes/anker-solix-ble-hacs/specs/ble-protocol/spec.md
✓ Updated: README.md

### Step 3: Validation Checks
✓ Verified all markdown tables and code fences
✓ Verified all internal document links

Documentation is now fully aligned with the codebase! Run `/opsx:commit` to secure your changes.
```

---

## Guardrails
- **No Stale Facts**: Never guess or speculate on API behavior or protocol formats; verify against actual code or verified telemetry captures.
- **Aesthetic Excellence**: Avoid simple unformatted text blocks. Use structured lists, tables, bold text, and code formatting to make documents extremely readable.
- **No Broken Links**: Double-check all file paths and references before concluding.
