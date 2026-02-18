# Paper Chunking Protocol for PRP Phase 2

## Purpose
This document defines the standard procedure for chunking academic papers into marked-up markdown files with citation IDs. Use this protocol to ensure consistent quality across all papers in the corpus.

## Explanation of Chunking Methodology
I used Claude Opus 4.6 to complete chunking according to the proctocol outlined here. Prior testing with script-based PDF extraction methods and OCR proved undesirable. Testing with Claude was very successful. I prepared this document to share with Claude after interviewing it about how it processed the PDF text extraction and chunking process in testing. Since processing 20 documents was likely to occur over multiple conversations, it was important to have a standardized process that Claude could refer to and follow in later iterations.

---

## Output Format Specification

### File naming
```
{source_id}_chunked.md
```
Example: `uriot2022_chunked.md`

### Document structure
```markdown
# {source_id} -- {title}

**Authors:** {author list}
**Venue:** {venue} ({year})
**DOI:** {doi or url}

---

## sec0 -- Abstract

[sec0_p1] Abstract text paragraph 1...

[sec0_p2] Abstract text paragraph 2 (if applicable)...

---

## sec1 -- Introduction

[sec1_p1] First paragraph of introduction...

[sec1_p2] Second paragraph...

### sec1.1 -- Subsection Title

[sec1.1_p1] First paragraph of subsection...

---

## sec2 -- Next Section
...
```

### Chunk ID format
- Main sections: `[secN_pM]` where N = section number, M = paragraph number
- Subsections: `[secN.X_pM]` (e.g., `[sec4.2_p3]`)
- Sub-subsections: `[secN.X.Y_pM]` (e.g., `[sec5.3.1_p2]`)
- Split paragraphs: `[secN_pM_K]` where K = split part (e.g., `[sec3_p2_1]`, `[sec3_p2_2]`)
- Paragraph numbering resets within each section/subsection

### Section numbering convention

**Core principle:** Number sections sequentially based on document order, not semantic meaning. Match the document's actual structure.

| Position in document | Chunk prefix | Notes |
|---------------------|--------------|-------|
| First substantive section | sec0 | Usually "Abstract" but could be "Summary", "Executive Summary", "Scope", etc. |
| Second substantive section | sec1 | Usually "Introduction" but could be "Overview", "Background", etc. |
| Subsequent sections | sec2, sec3, ... | Number in document order. |
| Final section | secN | Usually "Conclusions" but use actual title. |
| References | Omit | Do not chunk |
| Appendices | secA, secB or continue numbering | Include if substantive. |

**Handling non-standard documents:**

| Scenario | What to do |
|----------|------------|
| No abstract | sec0 = whatever comes first |
| No introduction | sec1 = second section, whatever it's called |
| Different naming (e.g., "Overview") | Use actual title: `## sec1 -- Overview` |
| Document starts with content, no headers | Use `## sec0 -- [Untitled Opening]` |
| Standards document with "Scope" first | `## sec0 -- Scope` |

---

## Step-by-Step Chunking Process

### Step 1: Extract text

### PDF file format in this environment

When PDF files are uploaded to Claude, they are converted to ZIP archives containing per-page text and image files. Standard PDF extraction tools (pymupdf, pdfplumber, pdfminer) will fail. Use the following procedure:
```bash
# 1. Confirm file format
file /mnt/project/{source_id}.pdf
# Expected output: "Zip archive data, ..."

# 2. Extract to working directory
cp /mnt/project/{source_id}.pdf /home/claude/{source_id}.zip
unzip -o /home/claude/{source_id}.zip -d /home/claude/{source_id}_pages

# 3. Read extracted text (pages are numbered 1.txt, 2.txt, ...)
for f in /home/claude/{source_id}_pages/*.txt; do
    echo "=== $(basename $f) ==="; cat "$f"; echo
done
```

The extracted `.txt` files are the raw source text for chunking. Page images (`.jpeg`) can be consulted if text extraction appears garbled or incomplete. Do not attempt to install or use PDF libraries. If you encounter a file that is in standard PDF format, follow the steps below.

### PDF file in native PDF format.
- Read all pages from the PDF.
- Concatenate into single text stream.
- Note any extraction issues (tables, figures, equations).

### Step 2: Identify document structure
- Find all section headers (numbered or unnumbered).
- Map the hierarchy (main sections vs. subsections).
- Create section outline before chunking.

### Step 3: Assign section IDs
- sec0 = Abstract (true for most sources)
- sec1 = Introduction (true for most sources)
- Number subsequent sections in document order.
- Use dot notation for subsections (sec2.1, sec2.2).

### Step 4: Chunk by paragraph
- Each paragraph gets one chunk ID.
- A "paragraph" = logical unit of thought (usually separated by blank lines).
- Keep paragraphs intact; do not split mid-paragraph.
- Exception: If a paragraph exceeds 2000 characters, split at sentence boundary.

**Paragraph split numbering:**

When splitting a long paragraph, use sub-numbering to preserve structure:

| Original paragraph | Split chunks |
|-------------------|--------------|
| Paragraph 2 (2500 chars) | `[sec3_p2_1]` first part, `[sec3_p2_2]` second part |

This ensures:
- Citation verification works (p2 maps to original paragraph 2).
- Semantic relationship is clear (parts belong together).
- Original paragraph numbering is preserved for subsequent paragraphs.

### Step 5: Clean text
- Remove page headers/footers.
- Remove page numbers.
- Fix hyphenation from line breaks (e.g., "ma-\nchine" → "machine").
- Preserve meaningful formatting (lists, equations where possible).
- Remove figure/table captions OR mark them clearly as [Figure N caption].

**Textual fidelity:** Chunks must reproduce the source text completely and verbatim after cleaning. Do not paraphrase, summarize, truncate, or rewrite the authors' language. The only permitted modifications are:

- Removing line-break hyphenation (e.g., "ma-\nchine" → "machine")
- Removing page headers/footers/page numbers
- Merging multi-column layout into reading order
- Replacing complex or garbled equations with labeled placeholders (described in the Equations section).
- Converting bullet lists from the original into inline prose (when needed for paragraph structure)

If text is unclear or extraction is uncertain, flag it with [unclear] rather than guessing at the intended meaning.

### Step 6: Quality check
Run through checklist before finalizing (see below).

---

## Quality Checklist

Before marking a paper as complete, verify:

### Structure
- [ ] All major sections are captured (Abstract through Conclusions)
- [ ] Section hierarchy matches original paper
- [ ] No sections are missing or duplicated
- [ ] References section is excluded

### Chunk IDs
- [ ] Every paragraph has exactly one chunk ID for each splt. (If not split, there is exactly one chunk ID.) 
- [ ] IDs follow `[secN_pM]` or `[secN.X_pM]` format.
- [ ] Split paragraphs use `[secN_pM_1]`, `[secN_pM_2]` format.
- [ ] Paragraph numbers reset in each section/subsection.
- [ ] No duplicate chunk IDs exist.

### Content
- [ ] No empty chunks
- [ ] No chunks with only headers/whitespace
- [ ] Text completely and faithfully reproduces the source (no paraphrasing or summarization).
- [ ] Text is readable (no major extraction artifacts).
- [ ] Equations/symbols are reasonably preserved or marked as [Equation N] with a descriptive label.
- [ ] Tables are linearized or omitted with semantic summary labels (no bare `[Table N omitted]` without description).

### Encoding
- [ ] File saved as UTF-8.
- [ ] Special characters display correctly (em-dashes, accents).
- [ ] No garbled character sequences (â€", Ã, etc.)

### Metadata
- [ ] Header includes source_id, title, authors, venue, year.
- [ ] DOI or URL included (see priority below).

**DOI/URL priority:**

| Situation | What to include |
|-----------|-----------------|
| DOI available | `**DOI:** https://doi.org/...` |
| No DOI, URL available | `**URL:** https://arxiv.org/...` or similar |
| Both available | DOI only (preferred identifier) |
| Neither available | `**Source:** [description of where obtained]` |

---

## Edge Cases and Decisions

### Figures
- Always omit figure images.
- Include caption as: `[Figure N: caption text]`.
- Do not assign chunk ID to figure captions.

### Tables
Tables in scientific papers often contain query-relevant content (hyperparameters, experimental results, dataset characteristics, comparison benchmarks) that the surrounding prose does not fully restate. Omitting tables without compensation creates retrieval blind spots: queries about specific values, configurations, or comparisons will not match any chunk.

**Decision framework:**

| Table type | Action | Rationale |
|------------|--------|-----------|
| Results / comparisons (e.g., model performance, benchmark scores) | Linearize | High query relevance; values rarely restated in prose |
| Configuration / parameters (e.g., hyperparameters, system specs, dataset splits) | Linearize | Directly answers "what settings were used" queries |
| Simple reference data (e.g., RCS values, orbit characteristics) | Linearize | Short, easy to convert, fills gaps left by prose references like "see Table 2" |
| Large comparison matrices (many rows × many columns) | Omit with semantic summary | Too complex to linearize cleanly; summary preserves retrievability |
| Formatting-only tables (e.g., notation glossaries, abbreviation lists) | Omit | Low retrieval value |

**Linearization:** Convert table rows into natural-language sentences within a chunked paragraph. Assign a chunk ID. Prefix the paragraph with a provenance marker in the format `[Table N: original caption text]` so that human reviewers can distinguish linearized tables from source prose. The marker parallels the existing `[Figure N: caption text]` convention. This makes content embeddable and retrievable while maintaining traceability to the source document.

**Process:**
1. When encountering a table, decide whether to linearize or omit using the decision framework above.
2. If linearizing, place the linearized paragraph at the location where the table appears in the document, using the section's chunk ID sequence.
3. If omitting, write a semantic summary label and do not assign a chunk ID to the placeholder.

**Table captions:** Unlike figures, table captions do not need a separate caption line. For linearized tables, incorporate the caption's descriptive content into the linearized paragraph. For omitted tables, the semantic summary label should begin with the original caption text, then extend with retrieval-relevant detail (key dimensions, value ranges, units) when the caption alone is too terse to match likely queries.

**Semantic labels for omitted tables:**

When a table is omitted rather than linearized, the placeholder must include a natural-language description of the table's content, following the same principle as equation placeholders: embedding models cannot retrieve from bare structural markers like `[Table N omitted]`, so the descriptive label provides the semantic content that allows nearby chunks to match relevant queries.

| Format | Example |
|--------|---------|
| Omitted with semantic summary | `[Table 5 omitted: Recall, precision, and F1-score of the End-to-End CNN with depth images — per-category results for 11 spacecraft types plus average (precision 0.69, recall 0.70, F1 0.69)]` |
| Omitted, low value | `[Table 1 omitted: notation and abbreviation definitions]` |

**Label guidelines for omitted tables:**
- Begin with the original caption text.
- Extend with retrieval-relevant detail when the caption alone is too terse: key dimensions (what rows and columns represent), value ranges, and units.
- Keep labels to one or two sentences.

**Linearization examples:**

Simple reference table:
```markdown
[sec4.1_p2] [Table 2: Radar cross-section as the diameter of the spherical object varies.] Radar cross-sections for spherical metallic objects vary with diameter as follows: 0.5 cm diameter corresponds to an RCS of 0.000078 m², 1 cm to 0.000314 m², 2 cm to 0.001256 m², 4 cm to 0.005026 m², and 8 cm to 0.020106 m². Values are obtained by Mie series approximation.
```

Configuration table:
```markdown
[sec4.2_p2] [Table 3: Summary of TIRA tracking mode parameters.] The TIRA tracking mode parameters used in simulation are: propagation at light speed, 100 integrated pulses (assumed), 5 kHz sample rate (assumed), maximum range of 3000 km, operating frequency of 1.33 GHz (L-band), peak power of 1.5 × 10⁶ (linear), antenna gain of 49.7 dB, pulse width of 1 millisecond with rectangular pulse shape, PRF of 25 Hz, and antenna frequency range of 1–2 GHz.
```

### Equations

- If extractable as text: keep inline.
- If complex or garbled: replace with a labeled placeholder (see format guidance below).

**Semantic labels for equation placeholders:**

Equation placeholders must include a brief natural-language description of what the equation represents. This is critical for RAG retrieval: embedding models cannot meaningfully encode mathematical notation, so the descriptive label provides the semantic content that allows a chunk to match relevant queries.

| Format | Example |
|--------|---------|
| Inline placeholder | `[Equation 1: Bayes' theorem, posterior as product of likelihood and prior divided by evidence]` |
| Equation block | `[Equation 3: HMM likelihood as recursive product of transition and emission probabilities over observation sequence]` |
| Grouped equations | `[Equations 5–8: HMM prior specifications — Dirichlet priors for initial state π and transition rows A, Truncated Normal priors for emission means μ, Inverse Gamma priors for emission standard deviations σ]` |

**Label guidelines:**
- Name the equation if it has a standard name (e.g., "Bayes' theorem", "Bellman equation").
- Describe what it computes or relates (e.g., "posterior as product of...", "collision probability as function of...").
- Include key variable names when they appear in surrounding prose.
- Keep labels to one sentence; Thedetail lives in the prose context, not the placeholder.

**Markdown safety:** Avoid bare tilde characters (`~`) in chunks, as these render as strikethrough in markdown. Replace distributional notation like `X~N(0,1)` with prose: `X distributed as N(0,1)`.

### Multi-column layouts
- Merge into single column, preserving reading order
- Watch for text that merged incorrectly (mid-sentence jumps)

### Headers/footers
- Remove all running headers (journal name, page numbers)
- Remove author affiliations from headers if repeated

### Acknowledgments
- Include as a section (secN -- Acknowledgments) if substantive
- Omit if just funding boilerplate

### Appendices
Label as secA, secB or continue numbering (secN+1, secN+2).

**Decision test:** Would this content help answer research questions in the domain?

| Include (substantive) | Exclude (boilerplate) |
|-----------------------|-----------------------|
| Extended methodology details | Funding acknowledgments |
| Additional experimental results | Author contribution statements |
| Mathematical proofs/derivations | Ethics approval boilerplate |
| Implementation details (architecture, hyperparameters) | Abbreviation lists |
| Case studies or worked examples | Supplementary figures duplicating main text |
| Ablation studies | Conference/journal submission metadata |
| Data preprocessing steps | |

**Process:**
1. Scan appendix title and first paragraph
2. Ask: "If I queried about methods, data, or limitations, would this be relevant?"
3. If yes → chunk it
4. If no → note `[Appendix X omitted: {reason}]` at end of document

### References
**Always exclude.** Do not chunk the references section.

**Rationale:**
- References are bibliographic metadata, not prose with claims/evidence
- Pollutes retrieval (queries would match paper titles, not content)
- Wrong unit of meaning for RAG (structured citations ≠ semantic paragraphs)

---

## Validation Commands

After creating a chunked file, run these checks:

```bash
# Count chunks and sections.
grep -c '\[sec[0-9]' {file}
grep -c '^## sec\|^### sec' {file}

# Check for encoding issues.
grep -c 'â€\|Ã\|Â' {file}

# Check for empty chunks. Fixed to stop flagging figure labels.
grep -cP '^\[sec[\d][\d.]*_p[\d_]+\]\s*$' {file}

# Check for split paragraphs (informational).
grep -c '_[0-9]\]' {file}

# Check chunk size distribution (handles inline citations).
grep -oP '\[sec[\d][\d.]*_p[\d_]+\].*?(?=\[sec[\d]|$)' {file} | awk '{print length}' | sort -n | head -5
grep -oP '\[sec[\d][\d.]*_p[\d_]+\].*?(?=\[sec[\d]|$)' {file} | awk '{print length}' | sort -rn | head -5
```

Expected results:
- Encoding issues: 0
- Empty chunks: 0
- Min chunk size: >50 chars
- Max chunk size: <2500 chars
- Split paragraphs: typically 0-5 (more suggests source has very long paragraphs)

---

## Example: Good vs. Bad Chunking

### Good
```markdown
## sec3 -- Methodology

[sec3_p1] We propose a novel approach based on recurrent neural networks for predicting collision probability. The model takes as input a sequence of Conjunction Data Messages (CDMs) and outputs a probability distribution over future risk values.

[sec3_p2] The architecture consists of three main components: an encoder that processes the CDM sequence, a latent representation layer, and a decoder that generates predictions with associated uncertainty estimates.

### sec3.1 -- Data Preprocessing

[sec3.1_p1] Raw CDMs were filtered to remove incomplete records. We retained only events with at least five CDMs in the sequence, resulting in 12,847 training examples.
```

### Bad
```markdown
## Methodology

We propose a novel approach based on recurrent neural networks for predicting collision probability. The model takes as input a sequence of Conjunction Data Messages (CDMs) and outputs a probability distribution over future risk values. The architecture consists of three main components: an encoder that processes the CDM sequence, a latent representation layer, and a decoder that generates predictions with associated uncertainty estimates.

[chunk_1] Raw CDMs were filtered to remove incomplete records.

[chunk_2] We retained only events with at least five CDMs in the sequence, resulting in 12,847 training examples.
```

Problems:
- First two paragraphs missing chunk IDs
- Section ID missing from header
- Generic "chunk_N" instead of section-aware IDs
- Paragraph unnecessarily split

---

## My Process

These are the steps I followed while working with Claude Opus to complete chunking for the corpus. The process was completed over multiple conversations, and maintaining consistency was important.

1. Added this protocol document and the assignment description to a Claude project.
2. Used this prompt: "I'm chunking papers for my Phase 2 RAG corpus. Please follow the protocol in CHUNKING_PROTOCOL.md. Here's the first paper: [upload PDF]".
3. After chunking, asked Claude to run the validation commands.
4. Reviewed output before downloading.
5. Requested corrections if needed.

---

## Corpus Tracking

| source_id | status | chunks | sections | issues |
|-----------|--------|--------|----------|--------|
| ... | pending | | | |

Updated this table as papers were processed.
