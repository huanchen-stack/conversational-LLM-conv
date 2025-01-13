import requests
from bs4 import BeautifulSoup
import re
import json
import time


PROXIES = None

def get_conversation(url):
    try:
        response = requests.get(url, proxies=PROXIES, timeout=10)

        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('body')
        scripts = body.find_all('script')

        scripts = [(len(script.text), script) for script in scripts]
        scripts.sort(reverse=True)
        json_obj_match = re.search(r'window\.__remixContext\s*=\s*(\{.*?\});', scripts[0][1].text, re.DOTALL)
        json_obj_str = json_obj_match.group(1)
        json_obj = json.loads(json_obj_str)

        title = json_obj['state']['loaderData']['routes/share.$shareId.($action)']['serverResponse']['data']['title']
        conversation = json_obj['state']['loaderData']['routes/share.$shareId.($action)']['serverResponse']['data']['linear_conversation']
        conversation_distilled = []
        for message in conversation:
            role = message.get('message', {}).get('author', {}).get('role', '')
            message_content = message.get('message', {}).get('content', {}).get('parts', [])
            if role:
                conversation_distilled.append({
                    'role': role,
                    'message': message_content
                })
    except Exception as e:
        return

    return response.text, {
        'url': url,
        'title': title,
        'conversation': conversation_distilled
    }

with open('bing_search_results/chatgpt_share_urls_2k_sample.json', 'r') as f:
    urls = json.load(f)

for url, url_detail in urls.items():
    print(url, flush=True)

    conv_html, conv_distilled = get_conversation(url)
    fname = url.split('/')[-1]
    with open(f'conversations/{fname}.html', 'w') as f:
        f.write(conv_html)
    with open(f'conversations/{fname}.json', 'w') as f:
        json.dump(conv_distilled, f)

    time.sleep(60)
    # break