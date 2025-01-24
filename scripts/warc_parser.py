import sys
import gzip
import json
import re
import subprocess
from warcio.archiveiterator import ArchiveIterator

download_dir = "/home/huanchen/conversational-LLM-conv/common_crawl/warcs/"
# target_host_regex = r'https://chatgpt.com[^\s)\]\}\>,]+'
target_host_regex = r'https://chatgpt\.com(?:/[a-zA-Z0-9\-._~:/?#[\]@!$&\'()*+,;=]*)?'
links_dir = "/home/huanchen/conversational-LLM-conv/common_crawl/links/"

def parse(warc_fname, target_host_regex=target_host_regex, download_dir=download_dir):
    warc_file_path = f"{download_dir}{warc_fname}"
    extracted_links = []
    total_htmls = 0
    with gzip.open(warc_file_path, 'rb') as f:
        for record in ArchiveIterator(f):
            if record.rec_type == 'response' and record.http_headers:
                url = record.rec_headers.get_header('WARC-Target-URI')
                html = record.content_stream().read().decode('utf-8', errors='ignore')                
                url_pattern = re.compile(target_host_regex)
                # url_pattern = re.compile(r'https://www.[^\s)\]\}\>,]+')
                links = re.findall(url_pattern, html)
                links = [link.rstrip('/') for link in list(set(links))]
                if links: 
                    extracted_links.append({'url': url, 'links': links})
                total_htmls += 1

    with open(f'{links_dir}{warc_fname.split('.')[0]}.json', 'w') as f:
        json.dump({
            'total_htmls': total_htmls,
            'external_links': extracted_links
        }, f)
    subprocess.run(["rm", warc_file_path], check=True)

if __name__ == "__main__":
    warc_fname = sys.argv[1]
    parse(warc_fname)