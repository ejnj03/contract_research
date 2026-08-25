"""The four-step chained pipeline.

Each opinion goes through four prompts in sequence, every step consuming the
previous reply:

    1. motions            the procedural actions the court rules on
    2. issues             what the court must decide for each motion
    3. argument trees     how each side supports or refutes each issue
    4. disputes           which of those turn on contract language

This one script covers every chained run: the prompt version, the model, and
where a run resumes from are all flags.

    python -m pipelines.chained --prompts v2 --model o1-preview
    python -m pipelines.chained --prompts v4 --model gpt-4-turbo
    python -m pipelines.chained --prompts v2 --only-step 4    # reuse cached 1-3

Steps are cached per (citation, model, step) in --steps, so an interrupted run
resumes where it stopped and never pays for a step twice. Delete the cache file
to force a clean run.

How a step's messages are built depends on the prompt version. v2 and v4
accumulate one growing conversation. v3 restarts the conversation at every step
from a condensed restatement of what came before (its REVISED_STEP_* prompts),
to keep the context small; the pipeline picks this up automatically from the
prompt module.
"""

import argparse
import json
import os

from openai import OpenAI

from dataset import load_samples
from prompts import v2_chained, v3_chained_variant, v4_flat_chained

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT_VERSIONS = {
    "v2": v2_chained,
    "v3": v3_chained_variant,
    "v4": v4_flat_chained,
}

STEPS = (1, 2, 3, 4)


def step_prompts(version):
    """The four step prompts, plus the condensed restatements if the version has them."""
    module = PROMPT_VERSIONS[version]
    parts = [getattr(module, f"part_{step}") for step in STEPS]
    revised = [getattr(module, f"REVISED_STEP_{step}", None) for step in STEPS[:3]]
    return parts, revised if any(revised) else None


class StepCache:
    """Per-(citation, model, step) cache of completed steps, one JSON object per line."""

    def __init__(self, path):
        self.path = path
        self.entries = {}
        if path and os.path.exists(path):
            with open(path, "r") as f:
                for line_number, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        self.entries[
                            (record["citation"], record["model"], record["step"])
                        ] = record["response"]
                    except (json.JSONDecodeError, KeyError) as error:
                        print(f"Skipping {path} line {line_number}: {error}")
            print(f"Loaded {len(self.entries)} cached step(s) from {path}")

    def get(self, citation, model, step):
        return self.entries.get((citation, model, step))

    def put(self, citation, model, step, response):
        self.entries[(citation, model, step)] = response
        if not self.path:
            return
        with open(self.path, "a") as f:
            f.write(json.dumps({
                "citation": citation,
                "model": model,
                "step": step,
                "response": response,
            }) + "\n")


def build_messages(step, parts, revised, opinion, history):
    """Messages for one step, given the responses to the steps before it.

    With `revised`, each step restarts from a condensed restatement of the
    previous step plus its answer. Without it, the whole conversation is
    replayed and grows by two turns per step.
    """
    if revised and step > 1:
        return [
            {"role": "user", "content": revised[step - 2] + opinion},
            {"role": "assistant", "content": history[step - 2]},
            {"role": "user", "content": parts[step - 1].strip()},
        ]

    messages = [{"role": "user", "content": parts[0].strip() + opinion}]
    for earlier in range(1, step):
        messages.append({"role": "assistant", "content": history[earlier - 1]})
        messages.append({"role": "user", "content": parts[earlier].strip()})
    return messages


def run(model, prompt_version, out_path, steps_path, only_step, limit):
    parts, revised = step_prompts(prompt_version)
    cache = StepCache(steps_path)
    samples = load_samples()
    if limit:
        samples = samples[:limit]

    with open(out_path, "a") as out:
        for input_sample in samples:
            citation = input_sample["citation"]
            opinion = "\nopinion_text = " + input_sample["text"].strip()

            if cache.get(citation, model, 4) and only_step != 4:
                print(f"{citation}: already complete, skipping")
                continue

            history = []
            for step in STEPS:
                cached = cache.get(citation, model, step)
                if cached is not None and not (step == only_step):
                    print(f"{citation}: step {step} from cache")
                    history.append(cached)
                    continue

                if only_step and step < only_step:
                    raise SystemExit(
                        f"{citation}: --only-step {only_step} needs a cached step {step} "
                        f"in {steps_path}; run the earlier steps first."
                    )

                print(f"{citation}: extracting step {step}...")
                messages = build_messages(step, parts, revised, opinion, history)
                response = client.chat.completions.create(model=model, messages=messages)
                content = response.choices[0].message.content
                print(f"[START_{step}] {content} [END_{step}]")
                history.append(content)
                cache.put(citation, model, step, content)

            out.write(json.dumps({
                "citation": citation,
                "model": model,
                "prompts": prompt_version,
                "output": history[-1],
            }) + "\n")
            out.flush()
            print(f"{citation}: wrote final output")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", default="o1-preview")
    parser.add_argument("--prompts", default="v2", choices=sorted(PROMPT_VERSIONS))
    parser.add_argument("--out", default=None, help="default: <prompts>_<model>_output.jsonl")
    parser.add_argument("--steps", default=None, help="step cache; default: <prompts>_<model>_steps.jsonl")
    parser.add_argument(
        "--only-step",
        type=int,
        choices=STEPS,
        help="re-run just this step, taking the earlier ones from the cache",
    )
    parser.add_argument("--limit", type=int, help="only process the first N cases")
    arguments = parser.parse_args()

    stem = f"{arguments.prompts}_{arguments.model.replace('.', '-')}"
    run(
        model=arguments.model,
        prompt_version=arguments.prompts,
        out_path=arguments.out or f"{stem}_output.jsonl",
        steps_path=arguments.steps or f"{stem}_steps.jsonl",
        only_step=arguments.only_step,
        limit=arguments.limit,
    )
