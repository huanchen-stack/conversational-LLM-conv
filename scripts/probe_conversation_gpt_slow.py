import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os


PROXIES = None

def get_conversation(url):
    try:
        response = requests.get(url, proxies=PROXIES, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})
    except Exception as e:
        return '', {}
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
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
            if role:
                conversation_distilled.append({
                    'role': role,
                    'message': message_content
                })
    except Exception as e:
        return response.text, {}

    return response.text, {
        'url': url,
        'title': title,
        'conversation': conversation_distilled
    }

with open('bing_search_results/chatgpt_share_urls_2k_sample.json', 'r') as f:
    urls = json.load(f)

for url, url_detail in urls.items():
    print(url, flush=True)
    fname = url.split('/')[-1]
    if f'{fname}.json' in os.listdir('conversations'):
        continue

    try:
        conv_html, conv_distilled = get_conversation(url)
        if conv_html != '':
            with open(f'conversations/{fname}.html', 'w') as f:
                f.write(conv_html)
        if conv_distilled != {}:
            with open(f'conversations/{fname}.json', 'w') as f:
                json.dump(conv_distilled, f)
    except Exception as e:
        print(e)
        pass

    time.sleep(60)
        # break