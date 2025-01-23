import json

with open('bing_search_results/chatgpt_share_urls.json', 'r') as f:
    bing_results1 = json.load(f)

with open('bing_search_results/chatgpt_share_urls2.json', 'r') as f:
    bing_results2 = json.load(f)

with open('bing_search_results/chatgpt_share_urls3.json', 'r') as f:
    bing_results3 = json.load(f)


print(len(bing_results1))
print(len(bing_results2))
print(len(bing_results3))
bing_results1.update(bing_results2)
bing_results1.update(bing_results3)
print(len(bing_results1))
bing_results1 = {k: bing_results1[k] for k in list(bing_results1)[:2000]}
print(len(bing_results1))

with open('bing_search_results/chatgpt_share_urls_2k_sample.json', 'w') as f:
    json.dump(bing_results1, f)