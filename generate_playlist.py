import os
import re
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.nowtv.com.tr/canli-yayin"
OUTPUT_DIR = "streams"
OUTPUT_FILE = "playlist.m3u8"

def extract_m3u8_url(html):
    # Yayın linki genellikle bir player içinde geçer
    m3u8_matches = re.findall(r'(https?://[^\s"\']+\.m3u8)', html)
    return m3u8_matches[0] if m3u8_matches else None

def fetch_live_stream_url(source_url):
    try:
        response = requests.get(source_url, timeout=10)
        response.raise_for_status()
        return extract_m3u8_url(response.text)
    except requests.RequestException as e:
        print(f"[!] Hata: {e}")
        return None

def write_to_m3u8(stream_url, output_dir, output_file):
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, output_file)
    with open(full_path, "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1, NOW TV\n")
        f.write(f"{stream_url}\n")
    print(f"[✓] Playlist yazıldı: {full_path}")

if __name__ == "__main__":
    stream_url = fetch_live_stream_url(SOURCE_URL)
    if stream_url:
        write_to_m3u8(stream_url, OUTPUT_DIR, OUTPUT_FILE)
    else:
        print("[!] Yayın linki bulunamadı.")
