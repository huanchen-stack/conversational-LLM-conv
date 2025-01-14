import os
import json
from langdetect import detect, detect_langs
import re


conversation_fnames = os.listdir('conversations')
conversation_fnames = [fname for fname in conversation_fnames if '.json' in fname]

def get_conversation(fname):
    conversation_example = fname
    with open(f'conversations/{conversation_example}', 'r') as f:
        conversation = json.load(f)
    return conversation

def count_backNforth(conversation):
    roles = ['user', 'assistant']
    backNforth = 0
    prev_role = 'user'
    for take in conversation['conversation']:
        if take['role'] == 'user':
            prev_role = 'user'
        elif take['role'] == 'assistant' and prev_role == 'user':
            prev_role = 'assistant'
            backNforth += 1
    return backNforth

def detect_lang(conversation):
    queries = [take['message'] for take in conversation['conversation']if take['role']=='user']
    if len(queries) > 0:
        if len(queries[0]) > 0 and queries[0][0] == 'Original custom instructions no longer available':
            queries.pop(0)
    langset = set()
    for i in range(min(len(queries), 5)):
        try:
            lang = detect(queries[i][0])
            langset.add(lang)
        except:
            pass
    return list(langset)

def count_characters(conversation):
    user_messages = [take['message'] for take in conversation['conversation']if take['role']=='user']
    if len(user_messages) > 0:
        if len(user_messages[0]) > 0 and user_messages[0][0] == 'Original custom instructions no longer available':
            user_messages.pop(0)
    assistant_messages = [take['message'] for take in conversation['conversation']if take['role']=='assistant']
    charcount_user = sum([len(take[0]) for take in user_messages if len(take)!=0])
    charcount_assistant = sum([len(take[0]) for take in assistant_messages if len(take)!=0])
    return charcount_user, charcount_assistant

def count_code(conversation):
    assistant_messages = [take['message'] for take in conversation['conversation']if take['role']=='assistant']
    texts = []
    for take in assistant_messages:
        texts += take

    all_code = []
    for text in texts:
        code_blocks = re.findall(r"```(.*?)```", text, re.DOTALL)
        # Print extracted code blocks
        all_code.append([{
            'type': code_block.split('\n')[0].strip(),
            'length': len('\n'.join(code_block.split('\n')[1:]))
        } for code_block in code_blocks])
    return all_code

all_results = []
for fname in conversation_fnames:
    conversation = get_conversation(fname)
    backNforth = count_backNforth(conversation)
    langs = detect_lang(conversation)
    charcount_user, charcount_assistant = count_characters(conversation)
    code_blocks = count_code(conversation)

    result = {
        'conversation': fname,
        'backNforth': backNforth,
        'langs': langs,
        'charcount_user': charcount_user,
        'charcount_assistant': charcount_assistant,
        'code_blocks': code_blocks
    }
    print(json.dumps(result), flush=True)

    all_results.append(result)

with open('conversation_analysis.json', 'w') as f:
    json.dump(all_results, f)
