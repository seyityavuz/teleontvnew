import requests

SOURCE_URL = "https://www.nowtv.com.tr/canli-yayin"
PROXY_PREFIX = "http://tv.dsmart-go.workers.dev/?ID="

def generate_proxy_link(source_url):
    return f"{PROXY_PREFIX}{source_url}"

def write_to_m3u8(proxy_url, output_file="playlist.m3u8"):
    with open(output_file, "w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXTINF:-1, NOW TV\n")
        f.write(f"{proxy_url}\n")

if __name__ == "__main__":
    proxy_link = generate_proxy_link(SOURCE_URL)
    write_to_m3u8(proxy_link)
