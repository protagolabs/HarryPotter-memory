import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import copy
import re
from eventPrompt import Episodic_Memory_Template, Valid_JSON_Template
import json

def run_openai(messages, client):
    
    # Send the prompt to OpenAI's GPT-4
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stop=None,
        temperature=0.7
    )

    answer = response.choices[0].message.content
    
    return answer

def generate_templates(Prompt_Template, input_text):
    """
    Generates template with substituted texts.
    
    """

    # Deep copy the original template to avoid modifying it
    updated_template = copy.deepcopy(Prompt_Template)
        
    # Substitute the placeholder in the user document
    for entry in updated_template:
        if entry["role"] == "user":
            entry["content"] = entry["content"].format(input_text=input_text)
    
    return updated_template


if __name__ == "__main__":
    # Load the environment variables from the .env file
    load_dotenv()

    # Initialize OpenAI client
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

    input_folder = "jsonl"
    output_file = "episodic_events.jsonl"
    processed_chapters_file = 'processed_chapters.json'

    # Load the already processed chapters from a file, if it exists
    processed_chapters = set()
    if os.path.exists(processed_chapters_file):
        with open(processed_chapters_file, 'r') as f:
            processed_chapters = set(json.load(f))

    # Initialize a counter for the unique event key
    event_counter = 1

    # Get already processed event counter
    if os.path.exists(output_file):
        with open(output_file, 'r') as existing_file:
            for line in existing_file:
                event_data = json.loads(line.strip())
                # Update the event counter to reflect the last processed event
                last_event_key = list(event_data.keys())[-1]
                event_counter = max(event_counter, int(last_event_key.replace('event', '')) + 1)


    # Open the output file to write events
    with open(output_file, 'w') as outfile:
        
        # Iterate through each JSONL file in the folder
        for filename in sorted(os.listdir(input_folder)):
            filepath = os.path.join(input_folder, filename)
            
            # Process each line (each chapter) in the JSONL file
            with open(filepath, 'r') as infile:
                for line in infile:
                    chapter_data = json.loads(line.strip())  # Load the chapter (JSON object)

                    chapter_id = list(chapter_data.keys())[0]  

                    # Skip chapters that have already been processed
                    if chapter_id in processed_chapters:
                        print(f"Skipping {chapter_id}, already processed.")
                        continue  # Skip to the next chapter
                    
                    # Generate Episodic Memory using your templates and OpenAI
                    Episodic_Memory = generate_templates(Episodic_Memory_Template, chapter_data)
                    events = run_openai(Episodic_Memory, client)

                    # Strip the markdown delimiters (the ```json part)
                    cleaned_events = events.strip('```json').strip()

                    try:
                        # Parse the cleaned JSON string
                        cleaned_events = json.loads(cleaned_events)
                    except:
                        Valid_JSON = generate_templates(Valid_JSON_Template, events)
                        events = run_openai(Valid_JSON, client)
                        cleaned_events = events.strip('```json').strip()
                        cleaned_events = json.loads(cleaned_events)
                    
                    # Iterate through the generated events
                    for event_key, event_data in cleaned_events.items():
                        # Create a unique event key
                        unique_event_key = f"event{event_counter}"
                        event_counter += 1
                        
                        # Create a new dictionary with the unique event key and event data
                        event_dict = {unique_event_key: event_data}
                        
                        # Write this event to the output JSONL file
                        outfile.write(json.dumps(event_dict) + '\n')
                    
                    # Add the processed chapter to the set and save it
                    processed_chapters.add(chapter_id)
                    with open(processed_chapters_file, 'w') as f:
                        json.dump(list(processed_chapters), f)

    print(f"All events have been saved to {output_file}.")
