import requests
import json
from datetime import datetime
import random


gemma12_model = "google/gemma-3-12b-it:free"
gemma4_model = "google/gemma-3-4b-it:free"
llama3_model = "meta-llama/llama-3.2-3b-instruct:free"
KEY = <YOUR_KEY> #Correct your key here 

from utils import PLACES
from utils import ACTIVITIES
from utils import RACES
from utils import GENDERS


def generate_prompt(place, activity, race, gender):
    """Generate a prompt with the given parameters"""
    # Handle article (a/an)
    article = "an" if race[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    
    prompt = f"""
Generate 20 detailed video descriptions of {article} {race} {gender} {activity} in a {place}. 

CRITICAL REQUIREMENTS:
- Every single description MUST include the exact words "{race} {gender}"
- Do NOT use pronouns like "she", "he", "they" or "the person" - always use "{race} {gender}"
- Do NOT substitute with other terms - use exactly "{race} {gender}" in each description

Each description should be unique and capture different aspects like mood, 
camera angles, lighting, setting details, or the person's appearance and actions.

Format your response exactly as follows:

===VIDEO_DESC_1===
{article.capitalize()} {race} {gender} [rest of description here - must contain "{race} {gender}" at least once]

===VIDEO_DESC_2===
[Second description here - must contain "{race} {gender}" at least once]

===VIDEO_DESC_3===
[Third description here - must contain "{race} {gender}" at least once]

Continue this pattern through ===VIDEO_DESC_20===

EXAMPLE GOOD DESCRIPTION:
{article.capitalize()} {race} {gender} sits by the window in a cozy {place}, where the {race} {gender} is deeply absorbed in {activity}.

EXAMPLE BAD DESCRIPTION (DO NOT DO THIS):
A person sits by the window reading. She looks peaceful. (WRONG - does not use "{race} {gender}")

Make each description 1-2 sentences long and suitable for video generation AI. 
Include visual details about the environment, the {race} {gender}, the atmosphere, and any notable actions or moments.
"""
    return prompt

def call_ai_agent(prompt, model=gemma4_model):
    """Call the AI agent with the given prompt"""
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ]
                }
            ]
        })
    )
    return response

def parse_descriptions(response_text):
    """Parse the AI response and extract descriptions"""
    import re
    
    descriptions = re.findall(
        r'===VIDEO_DESC_\d+===\s*\n(.*?)(?=\n===VIDEO_DESC_|\Z)', 
        response_text, 
        re.DOTALL
    )
    descriptions = [d.strip() for d in descriptions]
    return descriptions

# Main execution
if __name__ == "__main__":
    # Random sampling
    place = random.choice(PLACES)
    activity = random.choice(ACTIVITIES)
    race = random.choice(RACES)
    gender = random.choice(GENDERS)
    
    print(f"Generating descriptions for: {race} {gender} {activity} in a {place}")
    print("-" * 80)
    
    # Generate prompt
    prompt = generate_prompt(place, activity, race, gender)
    
    # Call AI agent
    response = call_ai_agent(prompt, model=gemma4_model)
    
    # Get response content
    response_data = response.json()
    # import code; code.interact(local=dict(globals(), **locals()))
    print(response_data)
    content = response_data['choices'][0]['message']['content']
    
    print("Raw response:")
    print(content)
    print("-" * 80)
    
    # Parse descriptions
    descriptions = parse_descriptions(content)
    
    print(f"\nExtracted {len(descriptions)} descriptions:")
    for i, desc in enumerate(descriptions, 1):
        print(f"\n{i}. {desc}")
    
    # Save to file
    today = datetime.now().strftime("%y-%m-%d")
    output_filename = f"prompts_{today}_{race}_{gender}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        for i, desc in enumerate(descriptions, 1):
            f.write(f"\n{desc}\n\n")
    
    print(f"\nSaved to: {output_filename}")