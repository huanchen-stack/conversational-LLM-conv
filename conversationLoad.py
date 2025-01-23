from bs4 import BeautifulSoup
import re
import json
import os
from tqdm import tqdm


fname_list = os.listdir('conversations')
# fname_list = fname_list[0:1]

for fname in tqdm(fname_list):
    if fname.endswith('.json'):
        continue

    with open(f'conversations/{fname}', 'r') as f:
        html_text = f.read()

    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        body = soup.find('body')
        scripts = body.find_all('script')

        scripts = [(len(script.text), script) for script in scripts]
        scripts.sort(reverse=True)
        json_obj_match = re.search(r'window\.__remixContext\s*=\s*(\{.*?\});__remixContext', scripts[0][1].text, re.DOTALL)
        json_obj_str = json_obj_match.group(1)
        json_obj = json.loads(json_obj_str)

        title = json_obj['state']['loaderData']['routes/share.$shareId.($action)']['serverResponse']['data']['title']
        conversation = json_obj['state']['loaderData']['routes/share.$shareId.($action)']['serverResponse']['data']['linear_conversation']
        conversation_distilled = []
        for message in conversation:
            role = message.get('message', {}).get('author', {}).get('role', '')
            message_content = message.get('message', {}).get('content', {}).get('parts', [])
            text = message.get('message', {}).get('content', {}).get('text', '')
            if role:
                conversation_distilled.append({
                    'role': role,
                    'message': message_content,
                    'text': text
                })

        fid = fname.rstrip('.html')
        # print(conversation_distilled)
        with open(f'conversations/{fid}.json', 'w') as f:
            json.dump({
                'title': title,
                'conversation': conversation_distilled
            }, f)
    
    except Exception as e:
        pass
