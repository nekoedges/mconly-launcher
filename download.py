import argparse
import requests
import enum
import hashlib
import os
from dataclasses import dataclass
from zipfile import ZipFile

from tqdm import tqdm

import api

updateHost = "http://update.mconly.net"
updateHost_file = lambda modpack, file: f"{updateHost}/serverauth/updates/{modpack}/{file}"

def parse_args():
    parser = argparse.ArgumentParser(description="MinecraftOnly instance downloader")

    parser.add_argument("-m", "--modpack",  required = True)
    parser.add_argument("--chunk-size", type=int, default = 128 * 1024, help="I/O & Downloader chunk size(in bytes)")

    return parser.parse_args()


def download(args, url, output, size = None):
    if size == None:
        head = requests.head(url)
        size = int(head.headers.get('Content-Length', 0))

    bar = tqdm(total = size, desc = f"Downloading {os.path.basename(output)}",
               unit="B", unit_scale=True, leave=False)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with requests.get(url, stream=True) as r:
        with open(output, "wb") as f:
            for iter_ in r.iter_content(args.chunk_size):
                f.write(iter_)
                bar.update(len(iter_))
            return output

def get_file_md5(args, path):
    context = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(args.chunk_size)
            context.update(chunk)
            if len(chunk) < args.chunk_size:
                break
    return context.hexdigest()


def main(args):
    base_path = os.path.abspath(args.modpack + "_instance")

    updates = api.get_updates(args.modpack)

    full_download_list = [i for i in updates if i.type != api.UpdateType.Optional]
    download_list = []

    for entry in full_download_list:
        fullpath = os.path.join(base_path, entry.path)
        try:
            open(fullpath).close()
        except FileNotFoundError:
            download_list.append(entry)
            continue

        if entry.type == api.UpdateType.VerifyHash and get_file_md5(fullpath) != entry.md5:
            download_list.append(entry)

    for entry in tqdm(download_list, desc = f"Updating modpack \"{args.modpack}\""):
        fullpath = os.path.join(base_path, entry.path)
        download(args, updateHost_file(args.modpack, entry.path), fullpath)

        if entry.path in ["resources.zip", "configs.zip"]:
            with ZipFile(fullpath) as zf:
                zf.extractall(base_path)

    # TODO: add code to create a "servers.dat" file

if __name__ == "__main__":
    args = parse_args()
    main(args)
