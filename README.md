# TextualAgent: The Sovereign Scribe Protocol

A high-precision research engine for Gemini CLI designed to process academic, theological, and technical texts with zero data loss and strict stylistic adherence.

## 🚀 Quick Start

1.  **Link the Extension:**
    `gemini extensions link ~/.gemini/extensions/textual-agent`
2.  **Navigate to a Domain Workspace:**
    Open your terminal in a folder containing your `StyleMatrix.json`.
3.  **Perform a Perfect Rewrite:**
    `gemini "/process chapter_1.docx"`

---

## 🛠️ Commands

### `/process <file>`
The **Master Command** for the flagship "Perfect Rewrite" workflow.
*   **What it does:** Automates the sequential 3-pass protocol: **Chunking** (via Rewrite Agent) → **Polish** (Linguistic Elevation) → **Advisory** (Metadata Insights).

### `/orchestrate <file> <agent>`
The general-purpose, headless pipeline.
*   **Use when:** You need a single-pass run for **Sanitize**, **Translate**, or **Summarize**.
*   **Agents:** `rewrite`, `sanitize`, `summarize`, `translate`.

### `/batch <file> <agent>`
A hardened, deterministic version of orchestration.
*   **Use when:** You need high-integrity processing with automatic retries if footnote counts or word-retention ratios fail the "Sovereign Audit."

---

## 💎 The Flagship Workflow (Perfect Rewrite)

For critical rewrites, the `/process` command automates this 3-tier protocol:

1.  **Phase 1: Structured Chunking**
    Every technical nuance is preserved and stabilized using the `Rewrite` agent identity.
2.  **Phase 2: Mandate-Only Polish** 
    Elevates the linguistic flow and enforces strict Matrix compliance (authorial singular, lexical swaps) without structural interference.
3.  **Phase 3: Advisory Insights**
    Captures metadata, suggested sources, and structural critiques in the `ADVISORY_LOG.md`.

---

## 📝 Key Features

*   **Zero-Macro Footnotes:** Autonomous logic injection into Word via AppleScript (macOS) or COM (Windows).
*   **Style Matrix Physics:** Style is derived deterministically from your `StyleMatrix.json`.
*   **The Floor Rule:** Footnotes can grow to store nuance, but they can never shrink.

---

## 📁 Best Practices

*   **Domain Workspaces:** Run from folders containing project-specific `StyleMatrix.json` and `STM.md`.
*   **Drag & Drop:** Drag files directly into the terminal and prefix with `@`.
