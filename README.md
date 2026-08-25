# Contract Interpretation Research

LLM pipelines for extracting **contract-interpretation arguments** from U.S. federal court
opinions. Given an opinion, the models identify the disputed contractual language (a *Locus*),
who argued about it (plaintiff / defendant / court), and what *type* of interpretive argument
was made (categories A–E), emitting structured JSON.

## Repository layout

```
data/                        # Raw court opinions, one .txt per citation (e.g. "331 F.Supp.3d 263.txt")
gpt_unbatched.py             # Main single-prompt pipeline: opinion -> argument JSON
utils/                       # Reusable helpers and API plumbing
  gpt_batch_format.py        #   Build a .jsonl request file for the OpenAI Batch API
  gpt_batch_process.py       #   Upload, poll, and download a batch job
  o1_structured_input_ref.py #   Multi-step o1 run with a reference archive of prior steps
  assistants.py              #   Assistants API + shelve-backed thread persistence
  gemini_vertex.py           #   Vertex AI / Gemini variant of the same task
  check.py                   #   Scratch client for one-off API checks
versions/                    # Prompt + pipeline variants kept for comparison
  script_text.py             #   Prompt parts 1-4 (Motions -> Issues -> Loci -> Arguments)
  script_text_variant.py     #   Alternative wording of the same four parts
  o1_structured_input.py     #   4-step chained pipeline on o1-preview
  step_4.py                  #   Re-runs only the final step
  gpt-4-turbo_unbatched.py   #   Same chain on gpt-4-turbo
  structured_input_variant.py#   Variant chain with CSV-based resume/caching
  storage_init.py            #   Initialize the CSV cache
  revise_csv.py              #   Ad-hoc CSV cleanup
  hier_summary/              # Hierarchical-summarization approach for long opinions
    chunk_inputs.py          #   Split opinions on section headings
    recursive_summarize.py   #   Summarize chunks, then summarize the summaries
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then fill in your key
export OPENAI_API_KEY=...
```

All scripts read the key from `OPENAI_API_KEY`; none contain credentials.

## Data

`data/` holds the opinion texts. Scripts also expect a `labels.csv` in the working directory
with columns `citation`, `text`, `corrected_labels`. When an opinion's `text` cell is truncated
(<= 100 chars), the loader falls back to `data/<citation>.txt`. CSV/JSONL files are
gitignored, so they are not distributed with the repo.

## Running

Scripts use relative imports and relative paths, so run each from its own directory:

```bash
# Single-prompt extraction
python gpt_unbatched.py

# 4-step chained pipeline
cd versions && python o1_structured_input.py

# Batch API: format requests, then submit and collect
cd utils && python gpt_batch_format.py && python gpt_batch_process.py

# Long-opinion hierarchical summarization
cd versions/hier_summary && python recursive_summarize.py
```

Model names and output filenames are set in each script's `__main__` block.

## Approach

Two families of pipelines share the same task:

1. **Single prompt** (`gpt_unbatched.py`) — one long instruction defining Contract, Locus, and
   argument categories A–E; the model returns the full JSON array in one call.
2. **Chained steps** (`versions/o1_structured_input.py` and friends) — four prompts run in
   sequence, each consuming the previous output: extract motions, derive the issues per motion,
   locate the disputed loci, then classify the arguments. Intermediate steps are written to a
   separate `*_steps.jsonl` so a run can be inspected or resumed.

`versions/hier_summary/` handles opinions that exceed the context window by chunking on
numbered section headings and summarizing recursively before extraction.
