---
name: text-transformer
description: Use when performing high-precision, style-sensitive rewriting or translation of long-form documents. Enforces the "Perfect Combination" workflow (Chunking + Polish + Advisory) to ensure zero data loss and maximum stylistic fidelity.
---

# Text Transformer Skill: The Sovereign Scribe Protocol

## Overview
This skill implements the **TextualAgent** orchestration logic: a multi-pass, high-fidelity pipeline that respects external stylistic rules ("Style Matrix") and ensures the structural and semantic integrity of complex documents.

## Core Mandates

### 1. The High-Resolution Mandate
**Summarization is a Failure Mode.** The goal is **Atomic Fidelity**. Every technical sub-point, illustrative nuance, and parenthetical reference is "Data Truth" that must be preserved. Any significant word-count reduction without a corresponding instruction to "summarize" is a procedural failure.

### 2. The Zero-Persona Mandate
Maintain semantic neutrality. Avoid AI-marketing metaphors, "helpful assistant" phrasing, or robotic scaffolding. Lead with the data and end with the [END] tag.

## The Perfect Combination (Workflow)

For all complex transformations, the model MUST execute the following 2-pass protocol:

### Phase 1: Structured Chunking (Semantic Preservation)
- **Segmentation:** Divide the source text into logical segments (1,000 – 1,200 words).
- **Transformation:** Apply the primary Agent Identity (e.g., `Rewrite.txt`) and Style Matrix.
- **Goal:** Ensure all logical nodes and technical nuances are stabilized in the target register without argument pruning.

### Phase 2: Mandate-Only Polish (Linguistic Elevation)
- **Verification:** Review the assembled output from Phase 1.
- **Refinement:** Perform a surgical "polish" pass to elevate the linguistic flow, correct grammatical inconsistencies, and enforce strict Matrix compliance (e.g., lexical swaps, pronoun enforcement).
- **Constraint:** Do not alter the logical structure or core arguments during this pass.

### Phase 3: Supplementary Advisory (Parallel Metadata)
- **Separation of Concerns:** Keep technical metadata, structural suggestions, and suggested sources in a separate `ADVISORY_LOG.md`.
- **Purpose:** Provide high-signal commentary (e.g., lexical distinctions, conceptual anchors) without compromising the "Sovereign" status of the primary text.

## Data Integrity (The Footnote Valve)
- **Immutable Data:** Treat text inside `[[FN]]...[[/FN]]` (footnotes), `[[TEXT]]` (containers), and bibliographic references as **Sacred Data**.
- **The Floor Rule:** Footnotes may grow (to accommodate nuance) but must never shrink (data loss).

## Style Derivation (The Matrix Physics)
The model acts as a "Deterministic Orchestrator." It does not guess style; it **derives** it from the provided matrix. 
- **Lexical Sovereignty:** Audit text for vague nouns and replace them with technical bifurcations defined in the Matrix or Context Files.
- **Grounding Spikes:** Balance abstract logic with concrete examples (as defined by Rule `U6` or `U13`) to ensure the text remains "anchored."
