import subprocess
import threading
import os
import time
import random


warc_path_path = "/home/huanchen/conversational-LLM-conv/common_crawl/warc.paths"
download_dir = "/home/huanchen/conversational-LLM-conv/common_crawl/warcs/"

download_task_l = []
parse_task_l = []
download_task_mtx = threading.Lock()
parse_task_mtx = threading.Lock()

def download(warc_download_path):
    print(f"Downloading {warc_download_path}", flush=True)
    download_url = f"https://data.commoncrawl.org/{warc_download_path}"
    if os.path.exists(f"{download_dir}{warc_download_path.split('/')[-1]}"):
        return
    subprocess.run(["wget", "--no-verbose", download_url, "-P", download_dir], check=True)

def parse(warc_fname):
    print(f"Parsing {warc_fname}", flush=True)
    subprocess.run(["python3", "warc_parser.py", warc_fname], check=True)

def downloader():
    while True:
        with download_task_mtx:
            if not download_task_l:
                break
            warc_download_path = download_task_l.pop(0)
        try:
            download(warc_download_path)
        except Exception as e:
            print(f"Error downloading {warc_download_path}: {e}")
            continue
        download_fname = warc_download_path.split('/')[-1]
        with parse_task_mtx:
            parse_task_l.append(download_fname)

def parser():
    while True:
        with parse_task_mtx:
            with download_task_mtx:
                if not parse_task_l and not download_task_l:
                    break
            if not parse_task_l:
                continue
            warc_fname = parse_task_l.pop(0)
        try:
            parse(warc_fname)
        except Exception as e:
            print(f"Error parsing {warc_fname}: {e}")
            continue


if __name__ == "__main__":
    with open(warc_path_path, 'r') as f:
        download_task_l += f.read().splitlines()

    print(f"Total {len(download_task_l)} warc files to download")
    download_task_l = random.sample(download_task_l, 400)
    print(f"Downloading {len(download_task_l)} warc files")

    download_threads = [threading.Thread(target=downloader) for _ in range(3)]
    parse_threads = [threading.Thread(target=parser) for _ in range(15)]

    for t in download_threads:
        t.start()
    for t in parse_threads:
        t.start()

    for t in download_threads:
        t.join()
    for t in parse_threads:
        t.join()