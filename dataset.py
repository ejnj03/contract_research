"""Dataset index for the opinion corpus.

`labels.csv` is the manifest every pipeline starts from, with three columns:

    citation           case identifier, e.g. "331 F.Supp.3d 263"; also the
                       stem of the opinion file in data/
    text               the opinion text; may be blank or truncated, in which
                       case data/<citation>.txt is used instead
    corrected_labels   human ground-truth label, if one has been assigned

Build it from the corpus with::

    python -m dataset            # writes labels.csv from data/

Read it with :func:`load_samples`, which returns one dict per case:
``{"citation": str, "text": str, "label": Any}``.
"""

import argparse
import os

import pandas as pd

DATA_DIR = "data"
LABELS_CSV = "labels.csv"

# A cell shorter than this is treated as missing and read from data/ instead.
MIN_TEXT_LENGTH = 100


def opinion_path(citation, data_dir=DATA_DIR):
    """Path of the opinion file backing a citation."""
    return os.path.join(data_dir, f"{citation}.txt")


def build_labels_csv(data_dir=DATA_DIR, labels_path=LABELS_CSV, overwrite=False):
    """Create labels.csv from the .txt files in data_dir.

    Citations are taken from the filenames. An existing labels.csv is not
    overwritten unless overwrite=True; instead its labels are carried over for
    citations it already covers, and any new opinions are appended with a blank
    label. Returns the DataFrame that was written.
    """
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"No data directory at {data_dir}")

    citations = sorted(
        name[: -len(".txt")] for name in os.listdir(data_dir) if name.endswith(".txt")
    )
    if not citations:
        raise FileNotFoundError(f"No .txt opinions found in {data_dir}")

    existing_labels = {}
    if os.path.exists(labels_path) and not overwrite:
        existing = pd.read_csv(labels_path)
        if "citation" in existing and "corrected_labels" in existing:
            existing_labels = dict(zip(existing["citation"], existing["corrected_labels"]))
        print(f"Carrying over {len(existing_labels)} label(s) from {labels_path}")

    rows = []
    for citation in citations:
        with open(opinion_path(citation, data_dir), "r") as f:
            text = f.read()
        rows.append(
            {
                "citation": citation,
                "text": text,
                "corrected_labels": existing_labels.get(citation, ""),
            }
        )

    frame = pd.DataFrame(rows, columns=["citation", "text", "corrected_labels"])
    frame.to_csv(labels_path, index=False)
    print(f"Wrote {len(frame)} row(s) to {labels_path} from {data_dir}")
    return frame


def load_samples(labels_path=LABELS_CSV, data_dir=DATA_DIR, skip_missing=True):
    """Load labels.csv into a list of {"citation", "text", "label"} dicts.

    Where the CSV's text cell is blank or truncated (<= MIN_TEXT_LENGTH chars),
    the opinion is read from data/<citation>.txt. Cases whose text cannot be
    resolved either way are reported and, unless skip_missing=False, dropped so
    they are never sent to a model as an empty opinion.
    """
    labels_df = pd.read_csv(labels_path)

    missing_columns = {"citation", "text"} - set(labels_df.columns)
    if missing_columns:
        raise ValueError(
            f"{labels_path} is missing required column(s): {sorted(missing_columns)}"
        )
    if "corrected_labels" not in labels_df.columns:
        labels_df["corrected_labels"] = ""

    samples = [
        {"citation": citation, "text": "" if pd.isna(text) else str(text), "label": label}
        for citation, text, label in zip(
            labels_df["citation"], labels_df["text"], labels_df["corrected_labels"]
        )
    ]

    resolved = []
    for sample in samples:
        if len(sample["text"]) <= MIN_TEXT_LENGTH:
            path = opinion_path(sample["citation"], data_dir)
            if os.path.exists(path):
                with open(path, "r") as f:
                    sample["text"] = f.read()

        if len(sample["text"]) <= MIN_TEXT_LENGTH:
            print(
                f"Missing text for citation: {sample['citation']} "
                f"(no usable text in {labels_path}, and no {opinion_path(sample['citation'], data_dir)})"
            )
            if skip_missing:
                continue
        resolved.append(sample)

    print(f"Loaded {len(resolved)} of {len(samples)} case(s) from {labels_path}")
    return resolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build labels.csv from the data/ corpus.")
    parser.add_argument("--data-dir", default=DATA_DIR)
    parser.add_argument("--labels-path", default=LABELS_CSV)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="discard existing labels instead of carrying them over",
    )
    arguments = parser.parse_args()
    build_labels_csv(arguments.data_dir, arguments.labels_path, arguments.overwrite)
