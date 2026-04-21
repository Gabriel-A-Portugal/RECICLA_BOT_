import json
import os
import re
import uuid
import glob as glob_module

def generate_uuid():
    return str(uuid.uuid4())

def read_training_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    intents = {}
    current_intent = None
    current_phrases = []
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('INTENT:'):
            if current_intent:
                intents[current_intent] = current_phrases
            current_intent = line.replace('INTENT:', '').strip()
            current_phrases = []
        elif line and line[0].isdigit():
            phrase = re.sub(r'^\d+\.\s*', '', line)
            if phrase:
                current_phrases.append(phrase)
    
    if current_intent:
        intents[current_intent] = current_phrases
    
    return intents

def create_user_says_entry(phrases):
    entries = []
    for phrase in phrases:
        if phrase and len(phrase) > 1:
            entry = {
                "id": generate_uuid(),
                "data": [
                    {
                        "text": phrase,
                        "userDefined": False
                    }
                ],
                "isTemplate": False,
                "count": 0,
                "lang": "pt-br",
                "updated": 0
            }
            entries.append(entry)
    
    return entries

def update_intent_file(intent_name, new_phrases, intents_dir):
    pattern1 = os.path.join(intents_dir, f"{intent_name}_usersays_pt-br.json")
    pattern2 = os.path.join(intents_dir, f"{intent_name}.json")
    
    filepath = None
    if os.path.exists(pattern1):
        filepath = pattern1
    elif os.path.exists(pattern2):
        filepath = pattern2
    
    if not filepath:
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    new_entries = create_user_says_entry(new_phrases)
    existing_data.extend(new_entries)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    base = os.path.dirname(__file__) or '.'
    training_file = os.path.join(base, 'RECICLA_BOT', 'treinamento_frases.txt')
    intents_dir = os.path.join(base, 'RECICLA_BOT', 'intents')
    
    print(f"Training file: {training_file}")
    print(f"Exists: {os.path.exists(training_file)}")
    
    intents_phrases = read_training_file(training_file)
    print(f"Intents found: {len(intents_phrases)}")
    
    updated_count = 0
    for intent_name, phrases in intents_phrases.items():
        if update_intent_file(intent_name, phrases, intents_dir):
            updated_count += 1
            print(f"Updated: {intent_name} ({len(phrases)} phrases)")
    
    print(f"\nTotal: {updated_count} intents updated")

if __name__ == "__main__":
    print("Starting script...")
    main()
    print("Done.")