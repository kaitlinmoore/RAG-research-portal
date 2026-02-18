# Chunking Playbook — Operational Guide for Claude

**Purpose:** Operational playbook for chunking papers. Format rules are in CHUNKING_PROTOCOL.md; this file tells you HOW to execute efficiently.

---

## Exact Execution Script

Follow this script literally. There are exactly 2 tool calls before you start writing.

**Tool call 1 of 2** — Read this playbook (you're doing that now). STOP HERE. Do NOT also read CHUNKING_PROTOCOL.md. Everything you need is in this file.

**Tool call 2 of 2** — Run the combined extraction command (see Text Extraction Steps below). This gives you the manifest metadata AND the full text in one call.

**Tool call 3** — `create_file` with Batch 1 content. You are now writing chunks.

**That's it. Three tool calls total before chunk content is being written.**

### What your conversational output should look like

Between tool calls, your text to the user should be **one sentence or less**. Here is the ideal:

```
[reads playbook]                          ← tool call 1
                                          ← NO conversational output needed
[runs combined extraction command]        ← tool call 2
                                          ← NO conversational output needed  
[create_file with Batch 1]                ← tool call 3 — you are now writing chunks
```

If you feel compelled to say something, the MAXIMUM is:

> "Extracting text."

...before tool call 2, and nothing else until all batches are done.

### What MUST NOT appear in your output before writing starts

Any of the following patterns mean you are wasting tokens and the paper WILL stall:

- ❌ Listing the sections you found ("The paper has these sections: 1. Abstract, 2. Introduction...")
- ❌ Describing your batch plan ("Batch 1 will cover..., Batch 2 will cover...")
- ❌ Deliberating about structure ("I'm reconsidering whether these should be subsections...")
- ❌ Reading CHUNKING_PROTOCOL.md (400+ lines you already have summarized below)
- ❌ Any paragraph longer than one sentence between tool calls

---

## Batching Strategy

Long papers (roughly 10+ pages) risk hitting the output token limit if the entire chunked file is generated in a single tool call. The solution is to break the work into batches.

### How to batch

1. **Batch 1 (create file):** Metadata header + sec0 (Abstract) through approximately sec3 or the first 3–4 major sections.
2. **Subsequent batches (append):** Use `cat >> /home/claude/{source_id}_chunked.md << 'BATCHN_END'` to append 2–4 sections per batch.
3. **Final batch:** Last sections + validation checks.

### Sizing guidance

Batch by **section count**, not page count. A 10-page paper with 14 sections needs just as many batches as a 20-page paper with 7 sections.

- **Few sections (< 6 major sections):** Usually safe in one or two file creation calls.
- **Many sections (6–10 major sections):** Two to three batches. ~3–4 sections per batch.
- **Very many sections (10+ major sections):** Three to four batches. Plan from the start — do not attempt to fit into fewer.
- **Papers with many subsections under one section:** Keep the parent section and its subsections together in one batch if possible, since context carries across subsections.

### What triggers a batch boundary

- Approaching ~3,000 words of output content in a single tool call.
- Natural section breaks (between major numbered sections, not mid-subsection).
- After completing a thematically self-contained block.

---

## Zero-Tolerance Token Waste List

If you catch yourself producing any of these, STOP and delete it:

1. **Reading CHUNKING_PROTOCOL.md** — You have the Format Cheat Sheet below. That's enough.
2. **Outputting a section list** — You can think about structure. You cannot write it out.
3. **Describing a batch plan** — Just execute the batches. The user doesn't need a preview.
4. **Explaining your approach** — The user wrote the playbook. They know the approach.
5. **Reconsidering decisions aloud** — Decide internally, commit, write.
6. **Any multi-sentence paragraph between tool calls** — One sentence max. Prefer zero.

---

## Format Cheat Sheet (So You Don't Need to Read the Full Protocol)

This covers the most common formatting rules. Only consult CHUNKING_PROTOCOL.md if you encounter an unusual case (appendices, non-standard document structure, edge cases with split paragraphs).

**File header:**
```
# {source_id} -- {title}

**Authors:** {from manifest}
**Venue:** {from manifest} ({year})
**DOI:** {from manifest}
```

**Section headers:** `## secN -- Title` for major sections, `### secN.X -- Title` for subsections, `#### secN.X.Y -- Title` for sub-subsections. Separate sections with `---`.

**Chunk IDs:** `[secN_pM]` at the start of every paragraph. Numbering resets per section. Split long paragraphs (>2000 chars) as `[secN_pM_1]`, `[secN_pM_2]`.

**sec0 = Abstract, sec1 = Introduction, then sequential. Skip References.**

**Figures:** Omit the image itself, but **always include the caption** as `[Figure N: caption text]` on its own line. Do NOT assign a chunk ID to figure captions. Captions contain retrieval-relevant context that the surrounding prose often references.

**Tables — most tables should be linearized, not skipped:**

| Table type | Action |
|------------|--------|
| Results / comparisons (model performance, benchmarks) | **Linearize** |
| Configuration / parameters (hyperparameters, specs, dataset splits) | **Linearize** |
| Simple reference data (values, characteristics) | **Linearize** |
| Large complex matrices (many rows × many columns) | Omit with semantic summary |
| Formatting-only (notation glossaries, abbreviation lists) | Omit |

Linearization format: Convert rows to natural-language sentences in a chunked paragraph. Prefix with `[Table N: caption text.]`. Example:
```
[sec4_p3] [Table 2: Database overview.] The database contains 15,321 events, of which 30 have risk >= 10^−4. There are 199,082 CDMs total, averaging 13 per event.
```

For omitted tables: `[Table N omitted: semantic description including key dimensions, value ranges, and what rows/columns represent]`. Never use bare `[Table N omitted]` — embedding models can't retrieve from that.

**Equations:** `[Equation N: natural-language description of what it computes]`. Never include raw LaTeX or garbled symbols.

**Text fidelity:** Verbatim after cleaning (fix hyphenation, remove headers/footers/page numbers, merge columns). Do NOT paraphrase or summarize.

---

## Text Extraction Steps

Run this **single combined command** to extract text and pull manifest metadata in one tool call:

```bash
# Combined extraction + manifest lookup
SRC="{source_id}"
echo "=== MANIFEST ===" && grep "$SRC" /mnt/project/data_manifest.csv && echo ""
cp /mnt/project/${SRC}.pdf /home/claude/${SRC}.zip
unzip -o /home/claude/${SRC}.zip -d /home/claude/${SRC}_pages 2>&1 | tail -3
echo "=== PAGE COUNT ===" && ls /home/claude/${SRC}_pages/*.txt | wc -l
echo "=== TEXT ===" 
for f in $(ls /home/claude/${SRC}_pages/*.txt | sort -V); do
    echo "=== $(basename $f) ==="; cat "$f"; echo
done
```

This gives you everything needed to start writing: metadata for the header, page count for batch planning, and full text for chunking. **Start writing Batch 1 immediately after this returns.**

**Do not** attempt pymupdf, pdfplumber, pdfminer, Tesseract, or any OCR tool. They do not work with the ZIP-based PDF format in this environment.

---

## Validation (Run After Every Paper)

Copy-paste this block, replacing `$FILE`:

```bash
FILE=/home/claude/{source_id}_chunked.md
echo "=== Chunk count ===" && grep -c '\[sec[0-9]' "$FILE"
echo "=== Section count ===" && grep -c '^## sec\|^### sec\|^#### sec' "$FILE"
echo "=== Encoding issues ===" && grep -c 'Ã¢â‚¬\|Ãƒ\|Ã‚' "$FILE"
echo "=== Empty chunks ===" && grep -cP '^\[sec[\d][\d.]*_p[\d_]+\]\s*$' "$FILE"
echo "=== Split paragraphs ===" && grep -c '_[0-9]\]' "$FILE"
echo "=== Shortest chunks ===" && grep -oP '\[sec[\d][\d.]*_p[\d_]+\].*?(?=\[sec[\d]|$)' "$FILE" | awk '{print length}' | sort -n | head -5
echo "=== Longest chunks ===" && grep -oP '\[sec[\d][\d.]*_p[\d_]+\].*?(?=\[sec[\d]|$)' "$FILE" | awk '{print length}' | sort -rn | head -5
```

Expected results: encoding issues = 0, empty chunks = 0, min chunk > 50 chars, max chunk < 2500 chars.

---

## Delivery

After validation passes:

```bash
cp /home/claude/{source_id}_chunked.md /mnt/user-data/outputs/{source_id}_chunked.md
```

Then use the `present_files` tool to share the file.

---

## Patching Existing Chunked Files (Figures/Tables Fix)

Use this procedure to add missing figure captions or fix table handling in already-chunked files without re-chunking from scratch.

### Prompt for patching

> "Patch {source_id}_chunked.md — add missing figure captions and linearize/summarize any skipped tables. Follow the patch protocol in CHUNKING_PLAYBOOK.md."

### Execution script (3 steps)

**Step 1 — Audit.** Run this single command to extract the PDF text and identify what's missing:

```bash
# Extract PDF text
SRC="{source_id}"
cp /mnt/project/${SRC}.pdf /home/claude/${SRC}.zip
unzip -o /home/claude/${SRC}.zip -d /home/claude/${SRC}_pages 2>&1 | tail -3

# Show all figure/table references in the PDF text
echo "=== FIGURES IN PDF ==="
for f in $(ls /home/claude/${SRC}_pages/*.txt | sort -V); do
    grep -inE '(fig\.|figure|table)\s*[0-9]' "$f" 2>/dev/null
done

# Show what's already in the chunked file
echo "=== FIGURES/TABLES IN CHUNKED FILE ==="
cp /mnt/project/${SRC}_chunked.md /home/claude/${SRC}_chunked.md
grep -inE '\[Figure|\[Table' /home/claude/${SRC}_chunked.md
```

This tells you what figures and tables exist in the source and which are already captured. The difference is your patch list.

**Step 2 — Patch.** For each missing item, use `str_replace` on `/home/claude/{source_id}_chunked.md`:

*Missing figure caption* — find the paragraph that references it and insert the caption line after that paragraph:

```
str_replace:
  old_str: "[sec3_p2] ...paragraph that says 'as shown in Fig. 4'..."
  new_str: "[sec3_p2] ...paragraph that says 'as shown in Fig. 4'...\n\n[Figure 4: caption text from the PDF]"
```

*Missing/skipped table that should be linearized* — find where the table appears in the section flow and insert a new chunked paragraph:

```
str_replace:
  old_str: "[sec5_p3] The paragraph right after where the table belongs..."
  new_str: "[sec5_p3] [Table 2: original caption.] Row 1 value is X, row 2 value is Y...\n\n[sec5_p4] The paragraph right after where the table belongs..."
```

Note: when inserting a new chunk paragraph for a table, renumber subsequent chunk IDs in that section (p3 becomes p4, etc.).

*Table that was omitted but needs a semantic summary* — insert a placeholder line (no chunk ID) at the table's location.

**Step 3 — Validate.** Run the standard validation block, then copy to outputs.

### Key principles

- **Use `str_replace`, not file rewrite.** Each edit is one surgical insertion. This uses minimal tokens.
- **Work from the PDF text, not the page images.** Grep the extracted `.txt` files for caption text.
- **Batch edits by section.** If a section has 3 missing figures, do all 3 in one `str_replace` call by replacing the section's last paragraph with itself plus all the inserted captions.
- **Don't touch existing chunk text.** The only changes are insertions (new caption lines, new linearized table paragraphs) and chunk ID renumbering when a table paragraph is inserted mid-section.
- **If a figure caption is unrecoverable from the text extraction** (garbled, image-only), read the page image `.jpeg` to get the caption text.

---

## Stall Recovery / Handoff Protocol

If a conversation stalls mid-paper (output token limit, context window full, or session ends):

### What the user should note for the next conversation

Provide a message like:

> "Chunking {source_id} stalled after batch N. Sections sec0–secX are complete in the attached partial file. Resume from secY. Follow CHUNKING_PLAYBOOK.md."

### What Claude should do in the new conversation

1. Read **this playbook only** (not CHUNKING_PROTOCOL.md — it's too long for a recovery scenario).
2. Read the partial file to confirm where it left off.
3. Extract the PDF text (the new conversation won't have it in context).
4. Resume appending from the next section using `cat >>`. **Do not narrate the plan — just start writing.**
5. Run validation on the complete file.

### Prevention

- Use the batching strategy above to avoid stalls in the first place.
- If a paper has 8+ major sections, plan for 3–4 batches from the start.
- **The most important prevention is token discipline** — keep pre-writing output to an absolute minimum. Every "let me plan..." sentence is a sentence of chunk content you won't have room for.

---

## Corpus-Specific Notes

### Papers already chunked (do not re-chunk)

Check `data_manifest.csv` — the `chunked` column indicates completion status. Corresponding `{source_id}_chunked.md` files exist in the project.

### Known extraction quirks

- **Multi-column layouts:** The ZIP text extraction sometimes merges columns incorrectly. Watch for mid-sentence jumps in meaning. Cross-reference with page images (`.jpeg` files in the extracted directory) if text seems garbled.
- **Equations:** Most equations in this corpus extract as garbled text. Use semantic placeholders per the protocol (e.g., `[Equation 1: description of what it computes]`).
- **Tables:** Linearize simple tables; provide semantic summaries for complex ones. See CHUNKING_PROTOCOL.md for examples.
- **Unicode issues:** Characters like em-dashes, smart quotes, and accented author names sometimes extract with encoding artifacts. Clean these during chunking.
- **Tilde characters:** Replace `~` (distributional notation like `X~N(0,1)`) with prose (`X distributed as N(0,1)`) to avoid markdown strikethrough rendering.

### Metadata source

Always pull author names, venue, year, and DOI from `data_manifest.csv` rather than re-deriving from the PDF text. The manifest has been verified and corrected.
