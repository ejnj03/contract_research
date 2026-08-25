"""Batch API pipeline: format the four flat prompts as requests, then submit them.

The Batch API has no reply to chain onto, so all four steps go out in a single
request per opinion, at the lower batch rate. Formatting and submission are one
command:

    python -m pipelines.batch

Use --format-only to write the request file without submitting it.
"""

import argparse
import json

from lib.batch_api import batch_process
from prompts.v4_flat_chained import part_1, part_2, part_3, part_4
from dataset import load_samples



def to_gpt_input(model, max_tokens, file_name):
    samples = load_samples()
    with open(file_name, 'w') as f:
        for number, input_sample in enumerate(samples):
            if input_sample["text"] != "nan":
                content = "\nopinion_text = " + input_sample["text"].strip()
                citation = input_sample["citation"]

                # The Batch API cannot chain: there is no reply to feed into the
                # next step, so all four steps go out as one request.
                messages = [
                    {"role": "user", "content": part.strip() + content}
                    for part in (part_1, part_2, part_3, part_4)
                ]
                
                # Construct the full JSON object
                chat_input = {
                    "custom_id": f"{citation}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens
                    }
                }
                
                # Write the JSON object as a string to the file
                f.write(json.dumps(chat_input))
                f.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", default="gpt-4-turbo")
    parser.add_argument("--max-tokens", type=int, default=3000)
    parser.add_argument("--input-file", default="batch_input.jsonl")
    parser.add_argument("--output-file", default="batch_output.jsonl")
    parser.add_argument("--batch-file", default="batch.txt", help="records the batch id")
    parser.add_argument("--format-only", action="store_true", help="write requests, do not submit")
    arguments = parser.parse_args()

    to_gpt_input(
        model=arguments.model,
        max_tokens=arguments.max_tokens,
        file_name=arguments.input_file,
    )
    if not arguments.format_only:
        batch_process(
            input_file=arguments.input_file,
            response_destination_file=arguments.output_file,
            batch_file=arguments.batch_file,
        )
