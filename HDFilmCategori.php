<?php
$headers = [
    'Accept: */*',
    'Accept-Encoding: gzip',
    'Accept-Language: tr-TR,tr;q=0.9',
    'Connection: keep-alive',
    'User-Agent: okhttp/4.12.0'
];

function getData($url, $headers) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_HTTPHEADER => $headers
    ]);
    $res = curl_exec($ch);
    curl_close($ch);
    return $res;
}

function resolveImageUrl($block) {
    if (preg_match('/data-srcset=["\']([^"\']+)["\']/i', $block, $m)) {
        $parts = explode(',', $m[1]);
        $first = trim($parts[0]);
        $first = preg_replace('/\s+\d+x$/i', '', $first);
        if ($first !== '') return $first;
    }
    if (preg_match('/<img[^>]+data-src=["\']([^"\']+)["\']/i', $block, $m)) {
        $url = trim($m[1]);
        if ($url !== '') return $url;
    }
    if (preg_match('/<img[^>]+src=["\']([^"\']+)["\']/i', $block, $m)) {
        $url = trim($m[1]);
        if (!preg_match('/^data:image/i', $url)) return $url;
    }
    if (preg_match('/background-image:\s*url\(([^)]+)\)/i', $block, $m)) {
        $url = trim($m[1], "\"' ");
        if (!preg_match('/^data:image/i', $url)) return $url;
    }
    return '';
}

ob_start();
echo "#EXTM3U\n";

for ($page = 801; $page <= 925; $page++) {
    $url = "https://www.fullhdfilmizlesene.tv/filmizle/turkce-dublaj-filmler-hd-izle/$page";
    $site = getData($url, $headers);

    preg_match_all('#<li\s+class="film"(.*?)</li>#si', $site, $blocks);

    foreach ($blocks[1] as $block) {
        if (!preg_match('/<a\s+class=["\']tt["\']\s+href=["\']https?:\/\/www\.fullhdfilmizlesene\.tv\/film\/([^"\']+)["\']\s*>(.*?)<\/a>/is', $block, $m)) {
            continue;
        }

        $Link = trim($m[1]);
        $NameRaw = strip_tags(trim($m[2]));

        $OrgName = '';
        if (preg_match('/<span\s+class=["\']film-title["\']>(.*?)<\/span>/is', $block, $m2)) {
            $OrgName = strip_tags(trim($m2[1]));
        }

        $Year = '';
        if (preg_match('/<span\s+class=["\']film-yil["\']>(.*?)<\/span>/is', $block, $m3)) {
            $Year = trim($m3[1]);
        }

        $Group = '';
        if (preg_match('/<span\s+class=["\']ktt["\']>(.*?)<\/span>/is', $block, $m4)) {
            $Group = strip_tags(trim($m4[1]));
        }

        $Logo = resolveImageUrl($block);
        if ($Logo !== '' && !preg_match('#^https?://#i', $Logo)) {
            if (strpos($Logo, '//') === 0) {
                $Logo = 'https:' . $Logo;
            } else {
                $Logo = 'https://www.fullhdfilmizlesene.tv' . (substr($Logo, 0, 1) === '/' ? '' : '/') . $Logo;
            }
        }

        $removeList = [' izle', ' İzle', 'izle', 'İzle', '- izle', '-izle'];
        $Name = trim(str_replace($removeList, '', $NameRaw));
        $OrgName = trim(str_replace($removeList, '', $OrgName));

        echo '#EXTINF:-1 tvg-logo="' . $Logo . '" tvg-year="' . $Year . '" group-title="' . $Group . '",' . $Name . " - " . $OrgName . "\n";
        echo "http://movies.hdfilm.workers.dev/?ID=$Link\n";
    }
}

- name: Commit ve push playlist
  run: |
    git config --global user.name "github-actions[bot]"
    git config --global user.email "github-actions[bot]@users.noreply.github.com"
    git add streams/playlist.m3u
    git commit -m "Auto-update playlist" || echo "No changes to commit"
    git push https://x-access-token:${{ secrets.GITHUB_TOKEN }} HEAD:main

$playlist = ob_get_clean();
file_put_contents(__DIR__ . "/streams/playlist.m3u", $playlist);
?>
