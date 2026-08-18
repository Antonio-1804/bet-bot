import urllib.request

urls = [
    "https://iptv-org.github.io/iptv/regions/eur.m3u",
    "https://iptv-org.github.io/iptv/countries/it.m3u"
]

combined = "#EXTM3U\n"

for url in urls:
    try:
        # Lade die Playlist herunter
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            text = response.read().decode('utf-8')
            # Entferne den Kopf, um Fehler beim Zusammenfügen zu vermeiden
            text = text.replace("#EXTM3U\n", "")
            combined += text + "\n"
    except Exception as e:
        print(f"Fehler bei {url}: {e}")

# Speichere die gebündelte Datei
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined)

print("playlist.m3u erfolgreich erstellt.")
