"""Hierarchical-summarization prompts for long opinions.

Used by: versions/hier_summary/recursive_summarize.py
"""

SYSTEM_MESSAGE = "This is a segment of a opinion text of a court case about contract disputes. Augment the summary by adding sections, subsections or points, or create a summary if there is no previous summary based on the segment, with the focus of identifying disputes that are either implicitly or directly dependent on the interpretation of certain phrases or words within a contract (there may be none). Specifically, either add to or create sections within the summary in the form: Section: A. key contention 1, (i) sub-contention 1, (a) details relevant to sub-contention 1, (ii) details relevant to A key contention 1, B. key contention 2, etc.; Make sure to include specific excerpts of the text that include details relevant to the different interpretations, if there are any."

INITIAL_SUMMARY = "None; This section is the first section of the opinion text."


def recursive_user_message(accumulated_summaries, subpart_name, segment):
    """Prompt for augmenting an existing summary with the next segment."""
    return (
        f"Summary to augment:\n\n{accumulated_summaries}\n\n"
        f"Current Segment's title/role within the Opinion Text: {subpart_name} \n\n"
        f"Current Segment to reference/use to augment the Summary:\n\n{segment}"
    )
