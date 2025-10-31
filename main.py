import streamlink
import sys
import os
import json
import traceback

def info_to_text(stream_info, url):
    text = '#EXT-X-STREAM-INF:'
    if getattr(stream_info, "program_id", None):
        text += f'PROGRAM-ID={stream_info.program_id},'
    if getattr(stream_info, "bandwidth", None):
        text += f'BANDWIDTH={stream_info.bandwidth},'
    if getattr(stream_info, "codecs", None):
        text += 'CODECS="' + ",".join(stream_info.codecs) + '",'
    if getattr(stream_info, "resolution", None) and getattr(stream_info.resolution, "width", None):
        text += f'RESOLUTION={stream_info.resolution.width}x{stream_info.resolution.height}'
    text += f"\n{url}\n"
    return text

def main():
    print("=== Starting stream processing ===")

    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    print(f"Loading config from: {config_file}")

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ ERROR loading config file: {e}")
        sys.exit(1)

    folder_name = config["output"]["folder"]
    best_folder_name = config["output"]["bestFolder"]
    master_folder_name = config["output"]["masterFolder"]
    root_folder = os.path.join(os.getcwd(), folder_name)
    best_folder = os.path.join(root_folder, best_folder_name)
    master_folder = os.path.join(root_folder, master_folder_name)

    print(f"Creating folders:\n  Root: {root_folder}\n  Best: {best_folder}\n  Master: {master_folder}")
    os.makedirs(best_folder, exist_ok=True)
    os.makedirs(master_folder, exist_ok=True)

    channels = config.get("channels", [])
    print(f"\n=== Processing {len(channels)} channels ===\n")

    success_count = 0
    fail_count = 0

    for idx, channel in enumerate(channels, 1):
        slug = channel.get("slug", f"channel_{idx}")
        url = channel.get("url", "")
        print(f"[{idx}/{len(channels)}] Processing: {slug}\n  URL: {url}")

        try:
            streams = streamlink.streams(url)
            if not streams or 'best' not in streams:
                print(f"  ⚠️  No valid 'best' stream found for {slug}")
                fail_count += 1
                continue

            stream_obj = streams['best']
            if not hasattr(stream_obj, "multivariant") or not stream_obj.multivariant:
                print(f"  ⚠️  No multivariant playlist found for {slug}")
                fail_count += 1
                continue

            playlists = stream_obj.multivariant.playlists
            previous_res_height = 0
            master_text = ''
            best_text = ''

            http_flag = url.startswith("http://")
            plugin_name = None
            if http_flag:
                try:
                    plugin_name, _, _ = streamlink.session.Streamlink().resolve_url(url)
                except Exception:
                    plugin_name = None

            for playlist in playlists:
                info = playlist.stream_info
                if getattr(info, "video", None) != "audio_only":
                    sub_text = info_to_text(info, playlist.uri)
                    if getattr(info.resolution, "height", 0) > previous_res_height:
                        master_text = sub_text + master_text
                        best_text = sub_text
                        previous_res_height = info.resolution.height
                    else:
                        master_text += sub_text

            if master_text:
                version = getattr(stream_obj.multivariant, "version", None)
                if version:
                    header = f"#EXT-X-VERSION:{version}\n"
                    master_text = header + master_text
                    best_text = header + best_text
                master_text = "#EXTM3U\n" + master_text
                best_text = "#EXTM3U\n" + best_text

                if http_flag and plugin_name == "cinergroup":
                    master_text = master_text.replace("https://", "http://")
                    best_text = best_text.replace("https://", "http://")

                master_path = os.path.join(master_folder, f"{slug}.m3u8")
                best_path = os.path.join(best_folder, f"{slug}.m3u8")

                with open(master_path, "w", encoding="utf-8") as f:
                    f.write(master_text)
                with open(best_path, "w", encoding="utf-8") as f:
                    f.write(best_text)

                print(f"  ✅ Success - Files created")
                success_count += 1
            else:
                print(f"  ⚠️  No content generated for {slug}")
                fail_count += 1

        except Exception as e:
            print(f"  ❌ ERROR processing {slug}: {e}")
            print(traceback.format_exc())
            fail_count += 1

    print(f"\n=== Summary ===\n✅ Successful: {success_count}\n❌ Failed: {fail_count}\nTotal: {len(channels)}")

if __name__ == "__main__":
    main()
