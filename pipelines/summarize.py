import os
from typing import Optional
from openai import OpenAI
from tqdm import tqdm
from lib.chunking import chunk_csv
from prompts.summarization import SYSTEM_MESSAGE, INITIAL_SUMMARY, recursive_user_message

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_chat_completion(messages, model='gpt-4-turbo'):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

def summarize(text_dict: str,
              model: str = 'gpt-4-turbo',
              additional_instructions: Optional[str] = None,
              summarize_recursively=True,
              verbose=False):
    """
    Summarizes a given text by splitting it into chunks, each of which is summarized individually. 
    The level of detail in the summary can be adjusted, and the process can optionally be made recursive.

    Parameters:
    - text (str): The text to be summarized.
    - detail (float, optional): A value between 0 and 1 indicating the desired level of detail in the summary.
      0 leads to a higher level summary, and 1 results in a more detailed summary. Defaults to 0.
    - model (str, optional): The model to use for generating summaries. Defaults to 'gpt-3.5-turbo'.
    - additional_instructions (Optional[str], optional): Additional instructions to provide to the model for customizing summaries.
    - minimum_chunk_size (Optional[int], optional): The minimum size for text chunks. Defaults to 500.
    - chunk_delimiter (str, optional): The delimiter used to split the text into chunks. Defaults to ".".
    - summarize_recursively (bool, optional): If True, summaries are generated recursively, using previous summaries for context.
    - verbose (bool, optional): If True, prints detailed information about the chunking process.

    Returns:
    - str: The final compiled summary of the text.

    The function first determines the number of chunks by interpolating between a minimum and a maximum chunk count based on the `detail` parameter. 
    It then splits the text into chunks and summarizes each chunk. If `summarize_recursively` is True, each summary is based on the previous summaries, 
    adding more context to the summarization process. The function returns a compiled summary of all chunks.
    """

    # set system message
    system_message_content = SYSTEM_MESSAGE
    if additional_instructions is not None:
        system_message_content += f"\n\n{additional_instructions}"

    accumulated_summaries = INITIAL_SUMMARY
    for part_name in tqdm(text_dict.keys()):
        ref_dict = {}
        if part_name == "DISCUSSION" or part_name == "ANALYSIS":
            ref_dict = ref_dict[part_name]
        else:
            ref_dict = {f"{part_name}": f"{ref_dict[part_name]}"}
        for subpart_name in ref_dict.keys():
            print(subpart_name)
            if summarize_recursively and accumulated_summaries:
                # Creating a structured prompt for recursive summarization
                accumulated_summaries_string = accumulated_summaries
                user_message_content = recursive_user_message(
                    accumulated_summaries_string, subpart_name, ref_dict[subpart_name]
                )
            else:
                # Directly passing the chunk for summarization without recursive context
                user_message_content = ref_dict[subpart_name]

            # Constructing messages based on whether recursive summarization is applied
            messages = [
                {"role": "system", "content": system_message_content},
                {"role": "user", "content": user_message_content}
            ]

            # Assuming this function gets the completion and works as expected
            response = get_chat_completion(messages, model=model)
            accumulated_summaries = response

    # Compile final summary from partial summaries
    final_summary = accumulated_summaries

    return final_summary

if __name__ == '__main__':
    samples = chunk_csv()
    for sample in samples:
        if sample["citation"] == "377 F.Supp.3d 633":
            summary = summarize(sample["text"])
            print(summary)