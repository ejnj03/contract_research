"""Versioned prompt library.

Every prompt sent to a model lives in this package; no code file contains an
inline prompt literal.

    v1_single_prompt      one long prompt, whole task in a single call
    v2_chained            four chained steps (canonical wording)
    v3_chained_variant    four chained steps, alternative wording + resume restatements
    v4_flat_chained       v2's steps flattened to one line each, for the Batch API
    gemini_qa             preamble + six fixed questions, Vertex AI chat session
    summarization         hierarchical summarization of long opinions

Import explicitly, e.g. ``from prompts.v2_chained import part_1``, so each
script records which prompt version it ran.
"""

VERSIONS = ("v1_single_prompt", "v2_chained", "v3_chained_variant", "v4_flat_chained")
