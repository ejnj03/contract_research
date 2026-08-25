import os
from openai import OpenAI
import json
import time

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def validate_jsonl_file(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                json.loads(line)  # Attempt to parse each line as JSON
                #print(line)
        print(f"{file_path} is a valid JSONL file.")
    except json.JSONDecodeError as e:
        print(f"Invalid JSONL format: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def start_batch_process(input_file, batch_file):
    validate_jsonl_file(input_file)

    # Upload the file to OpenAI
    batch_input_file = client.files.create(
        file=open(input_file, 'rb'),
        purpose="batch"
    )

    # Create the batch and retrieve the batch ID
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "contract interp results"}
    )

    batch_id = batch.id  # Retrieve the batch ID from the response
    print(batch_id)
    # Save the batch ID to the file
    with open(batch_file, "w") as f:
        f.write(batch_id)
    f.close()


def batch_process(input_file, response_destination_file, batch_file):
    try:
        with open(batch_file, "r") as f:
            batch_id = f.read().strip()  # Ensure no extraneous whitespace
            print(batch_id)
    except FileNotFoundError:
        batch_id = ''

    if not batch_id:
        print("Starting batch processing....")
        start_batch_process(input_file, batch_file)
    
    batch = client.batches.retrieve(batch_id)
    while(batch.status != 'completed' and batch.status != 'failed'):
        print("processing batch input..")
        time.sleep(30.0)
        batch = client.batches.retrieve(batch_id)
        
    if batch.status == 'completed':
        print(f"Batch processing completed. Writing output to {response_destination_file}")
            
        file_id = batch.output_file_id
        output = client.files.content(file_id)

        with open(response_destination_file, 'w') as f:
            f.write(output.text)
        f.close()
                    
    else:
        print(f"Batch processing at stage {repr(batch.status)}")
        if batch.status == 'failed':
            print(f"Error: {repr(batch.errors)}")

if __name__ == '__main__':
    batch_process(input_file='structured_4_turbo_other_input.jsonl', response_destination_file='structured_4_turbo_other_output.jsonl', batch_file = 'batch.txt')
