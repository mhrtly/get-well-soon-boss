#!/usr/bin/env python3
"""Add one entry to videos.json (and fetch a thumbnail when a YouTube link is given).

Example:
  python3 add_video.py --title "Live at the Main Point" --year 1975 --kind concert \
    --link "YouTube|https://www.youtube.com/watch?v=XXXXXXXXXXX|Free" \
    --era "Born to Run era" --tag "Full concert" --runtime "2 h 10 min" \
    --note "Two or three sentences on why it matters." --caveat ""
"""
import argparse, io, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "videos.json")

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]

def yt_id(url):
    m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})", url or "")
    return m and m.group(1)

def fetch_thumb(vid, dest):
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed; leaving thumb empty (the page will use YouTube's thumbnail URL).")
        return False
    for name in ("maxresdefault", "hqdefault"):
        try:
            data = urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/{name}.jpg", timeout=20).read()
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if im.width < 200:
                continue
            if name == "hqdefault":  # 4:3 with letterbox bars -> crop to 16:9
                h = round(im.width * 9 / 16); top = (im.height - h) // 2
                im = im.crop((0, top, im.width, top + h))
            im = im.resize((480, round(im.height * 480 / im.width)), Image.LANCZOS)
            im.save(dest, "JPEG", quality=74, optimize=True, progressive=True)
            return True
        except Exception:
            continue
    return False

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--title", required=True)
    ap.add_argument("--year", required=True, type=int)
    ap.add_argument("--kind", choices=["concert", "film"], default="concert")
    ap.add_argument("--link", action="append", default=[], help='"Label|URL|Access" (Access: Free, Subscription, Rent / buy). Repeatable.')
    ap.add_argument("--also", action="append", default=[], help="Plain-text availability line, e.g. 'Rent or buy on Amazon'. Repeatable.")
    ap.add_argument("--era", default="")
    ap.add_argument("--tag", action="append", default=[], help="Format tag, e.g. 'Full concert'. Repeatable.")
    ap.add_argument("--runtime", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--caveat", default="")
    ap.add_argument("--id", default="")
    ap.add_argument("--thumb", default="", help="Existing image path relative to the site folder (skips auto-fetch).")
    a = ap.parse_args()

    links = []
    for raw in a.link:
        parts = [p.strip() for p in raw.split("|")]
        if len(parts) != 3:
            sys.exit(f"Bad --link {raw!r}; use 'Label|URL|Access'")
        links.append(dict(label=parts[0], url=parts[1], access=parts[2]))

    items = json.load(open(DATA, encoding="utf-8"))
    vid_id = a.id or slug(a.title)
    if any(i["id"] == vid_id for i in items):
        sys.exit(f"An entry with id {vid_id!r} already exists.")

    thumb = a.thumb
    if not thumb:
        yid = next((yt_id(l["url"]) for l in links if yt_id(l["url"])), None)
        if yid:
            os.makedirs(os.path.join(HERE, "thumbs"), exist_ok=True)
            rel = f"thumbs/{vid_id}.jpg"
            if fetch_thumb(yid, os.path.join(HERE, rel)):
                thumb = rel
                print("Saved thumbnail", rel)

    items.append(dict(id=vid_id, title=a.title, year=a.year, kind=a.kind, runtime=a.runtime, era=a.era,
                      tags=a.tag, note=a.note, caveat=a.caveat, links=links, also=a.also, thumb=thumb))
    items.sort(key=lambda i: (i["year"], i["title"]))
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Added {vid_id!r} ({len(items)} entries).")

if __name__ == "__main__":
    main()
