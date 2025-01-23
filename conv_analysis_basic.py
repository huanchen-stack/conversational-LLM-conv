import os
import json
from langdetect import detect, detect_langs
import re
from tqdm import tqdm


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

def count_search(conversation):
    match_search = {}
    k = None
    for take in conversation['conversation']:
        if take['role'] == 'user':
            k = take.get('message', [''])
            k = k[0]
        if k and take['role'] != 'user':
            message = take.get('message', [])
            text = take.get('text', '')
            if k not in match_search:
                match_search[k] = []
            if message:
                match_search[k].append(message[0])
            if text:
                match_search[k].append(text)

    search_agg = {}
    for k, v in match_search.items():
        search_agg[k] = []
        for text in v:
            if "search(" in text and "search(" == text[:min(len('search('), len(text))]:
                search_agg[k].append(text)
        if not search_agg[k]:
            del search_agg[k]
    return search_agg

all_results = []
for fname in tqdm(conversation_fnames):
    conversation = get_conversation(fname)
    backNforth = count_backNforth(conversation)
    # langs = detect_lang(conversation)
    charcount_user, charcount_assistant = count_characters(conversation)
    # code_blocks = count_code(conversation)
    search_agg = count_search(conversation)

    result = {
        'conversation': fname,
        'backNforth': backNforth,
        # 'langs': langs,
        'charcount_user': charcount_user,
        'charcount_assistant': charcount_assistant,
        # 'code_blocks': code_blocks,
        'search_agg': search_agg,
    }
    # print(json.dumps(result), flush=True)
    all_results.append(result)

with open('conversation_analysis.json', 'w') as f:
    json.dump(all_results, f)

print("total #conv", len(all_results))
print("#conv w search()", sum([1 for res in all_results if len(res['search_agg'])>0]))
print("#search()", sum([len(res['search_agg']) for res in all_results]))
all_search = [res['search_agg'] for res in all_results if len(res['search_agg'])>0]
all_search_en = []
for search_conv in all_search:
    if detect(list(search_conv)[0]) == 'en':
        all_search_en.append(search_conv)
with open('conversation_all_search.json', 'w') as f:
    json.dump(all_search, f)
with open('conversation_all_search_en.json', 'w') as f:
    json.dump(all_search_en, f)