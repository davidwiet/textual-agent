# TextualAgent: The Sovereign Scribe Protocol

A high-precision research engine for Gemini CLI designed to process academic, theological, and technical texts with zero data loss and strict stylistic adherence.

## 🚀 Quick Start

1.  **Link the Extension:**
    `gemini extensions link ~/.gemini/extensions/textual-agent`
2.  **Navigate to a Domain Workspace:**
    Open your terminal in a folder containing your `StyleMatrix.json`.
3.  **Process a File:**
    `gemini "/orchestrate my_dissertation.docx rewrite"`

---

## 🛠️ Commands

### `/orchestrate <file> <intent>`
The headless, end-to-end pipeline. 
*   **What it does:** Automatically handles Word footnote flattening, segments the text into 1,000-word blocks, processes them via the selected Agent, and restores the footnotes in the final output.
*   **Intents:** `rewrite`, `sanitize`, `summarize`, `translate`.

### `/batch <file> <agent>`
A hardened, deterministic version of orchestration.
*   **Use when:** You need high-integrity processing with automatic retries if footnote counts or word-retention ratios fail the "Sovereign Audit."

### `/advise <file>`
The Architect's structural pass.
*   **Use when:** You want suggestions for moving paragraphs to improve logical flow without actually changing the text. Output is saved to `ADVISORY_LOG.md`.

### `/close-reading <file> <context_file>`
Perform a deep analysis through a specific lens (e.g., Maimonides, Kant).
*   **Use when:** You need to identify logical friction or thematic alignment based on an external "Viewpoint" file.

### `/relate <file>`
Tags the logical topology of a raw transcript.
*   **Use when:** You need to map "Late-Additions" (Oh, by the way moments) to their original thematic blocks.

---

## 💎 The "Perfect Combination" Workflow

For maximum quality, follow this 3-tier protocol:

1.  **Phase 1: Structured Chunking** (via `/orchestrate` or `/batch`)
    Ensures every technical nuance is preserved and stabilized in the new register.
2.  **Phase 2: Mandate-Only Polish** 
    Run a second pass asking the agent to "polish" the result. This fixes grammatical inconsistencies and elevates the registry without altering the arguments.
3.  **Phase 3: Advisory Insights**
    Capture metadata, suggested sources, and structural critiques in the `ADVISORY_LOG.md`.

---

## 📝 Key Features

*   **Zero-Macro Footnotes:** No setup required. The engine injects logic directly into Word via AppleScript (macOS) or COM (Windows).
*   **Style Matrix Physics:** Style is derived deterministically from your `StyleMatrix.json`. It is not a suggestion; it is the law of the text.
*   **The Floor Rule:** Footnotes may grow to store more nuance, but they can never shrink. Data loss is a procedural failure.

---

## 📁 Best Practices

*   **Domain Workspaces:** Always run from a folder containing your specific `StyleMatrix.json` and `STM.md`. This ensures the agent "remembers" your project-specific behavior.
*   **Drag & Drop:** You can drag files directly into the terminal—just remember to prefix the path with `@` so the CLI can read it.
