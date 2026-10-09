# Get Well Soon, Boss

A small static library of Bruce Springsteen concerts and films.

    index.html    page + script (renders everything from videos.json)
    videos.json   one object per title
    thumbs/       480px-wide JPEG thumbnails
    add_video.py  helper to add an entry

The page loads `videos.json` with `fetch`, so open it through a web server rather than as a
local file, e.g. `python3 -m http.server` in this folder, then http://localhost:8000.
Any static host works (GitHub Pages, Netlify, Cloudflare Pages).

## Entry schema (videos.json)

```json
{
  "id": "hammersmith",                 // unique slug; also used for #open=<id> deep links
  "title": "Hammersmith Odeon, London ’75",
  "year": 1975,                        // sort order is by year
  "kind": "concert",                   // "concert" or "film"
  "runtime": "2 h 10 min",             // free text, optional
  "era": "Born to Run era",            // one era label, optional; shown in the Era filter row
  "tags": ["Full concert"],            // format tags, shown in the Format filter row
  "note": "Two or three sentences of context.",
  "caveat": "Tubi is US-only, with ads.",   // optional practical note, shown in the detail view
  "links": [ { "label": "YouTube", "url": "https://…", "access": "Free" } ],  // access: Free | Subscription | Rent / buy
  "also": ["Rent or buy on Amazon"],   // optional plain-text availability lines (no link)
  "thumb": "thumbs/hammersmith.jpg"    // optional
}
```

Thumbnails: if `thumb` is empty, the page uses the YouTube thumbnail of the first YouTube link;
if there is none (or it fails to load), it shows a typographic placeholder tile.

Known format tags: Full concert, Full album, Solo acoustic, Concert film, Documentary,
Studio story, Fan film, Drama. New tags and eras appear in the filters automatically.

Per-era accents in the detail view: "Darkness era" (typewriter title), "River era" (teal italic),
"Born to Run era" (sepia image with overprinted title), "Jersey Shore" (postcard rule).
Mapped in `ERA_CLASS` in index.html.

## Adding a video

    python3 add_video.py --title "Some Show" --year 1984 --kind concert \
      --link "YouTube|https://www.youtube.com/watch?v=XXXXXXXXXXX|Free" \
      --era "Born in the U.S.A." --tag "Full concert" --runtime "2 h" \
      --note "Why it matters." --caveat ""

The script fetches the YouTube thumbnail into `thumbs/` (needs Pillow; otherwise it leaves `thumb`
empty and the page falls back to the YouTube image URL). Or simply add an object to
`videos.json` by hand.
