import os
import re
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_ROOT = os.path.join(SCRIPT_DIR, "photography")
SOURCE_DIR = os.path.join(PHOTO_ROOT, "photos")
THUMB_DIR = os.path.join(SOURCE_DIR, "thumb")
HTML_FILE = os.path.join(PHOTO_ROOT, "photography.html")

MAX_BYTES = 10 * 1024  # 10KB target
SOURCE_EXTS = (".jpg", ".jpeg", ".png", ".JPG", ".PNG", ".JPEG")
INITIAL_WIDTH = 700
MIN_WIDTH = 100
WIDTH_STEP = 100


def ensure_thumb_dir():
    os.makedirs(THUMB_DIR, exist_ok=True)


def existing_html_entries(html):
    """Return set of image filenames (basenames) already referenced in the grid."""
    pattern = re.compile(r'<img\s+src="photos/([^"]+)"', re.IGNORECASE)
    return {os.path.basename(p) for p in pattern.findall(html)}


def source_images():
    """Return sorted dict: basename -> full source path for photos folder images."""
    images = {}
    for f in os.listdir(SOURCE_DIR):
        full = os.path.join(SOURCE_DIR, f)
        if os.path.isfile(full) and os.path.splitext(f)[1] in SOURCE_EXTS:
            images[f] = full
    return images


def compress_to_webp(src_path, dst_path):
    """Compress src_path into a webp of <=MAX_BYTES. Returns True on success."""
    with Image.open(src_path) as pil:
        pil = pil.convert("RGB")
        orig_w, orig_h = pil.size

    width = INITIAL_WIDTH
    while width >= MIN_WIDTH:
        w = min(width, orig_w)
        nh = max(1, round((w / orig_w) * orig_h))
        with Image.open(src_path) as pil:
            pil = pil.convert("RGB").resize((w, nh), Image.LANCZOS)
            for quality in range(90, 19, -5):
                pil.save(dst_path, "WEBP", quality=quality, method=6)
                if os.path.getsize(dst_path) <= MAX_BYTES:
                    return True
        width -= WIDTH_STEP

    # Fallback: smallest size, lowest quality (may exceed the cap for tiny images)
    with Image.open(src_path) as pil:
        pil = pil.convert("RGB").resize((MIN_WIDTH, max(1, round((MIN_WIDTH / orig_w) * orig_h))), Image.LANCZOS)
        pil.save(dst_path, "WEBP", quality=20, method=6)
    return True


def max_alt_number(html):
    numbers = [
        int(m) for m in re.findall(r'alt="photo\s+(\d+)"', html)
    ]
    return max(numbers) if numbers else 0


def remove_deleted(html, sources):
    """Remove from HTML (and thumb folder) any image no longer in the photos folder."""
    existing = existing_html_entries(html)
    deleted = sorted(existing - set(sources))
    if not deleted:
        return html, 0

    for name in deleted:
        base = os.path.splitext(name)[0]
        thumb = os.path.join(THUMB_DIR, f"{base}.webp")
        if os.path.exists(thumb):
            os.remove(thumb)
            print(f"  Deleted thumb {base}.webp")

    # Remove matching <img> tags (allow surrounding whitespace)
    tags = []
    for name in deleted:
        pattern = re.compile(
            r'<img\s+src="' + re.escape(f"photos/{name}") + r'"[^>]*>\s*',
            re.IGNORECASE,
        )
        html, count = pattern.subn("", html)
        if count:
            tags.append(name)

    return html, len(tags)


def main():
    ensure_thumb_dir()

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    sources = source_images()

    html, removed = remove_deleted(html, sources)
    if removed:
        print(f"Removed {removed} deleted image(s) from the grid.")

    existing = existing_html_entries(html)

    new_images = [
        name for name in sorted(sources)
        if name not in existing
    ]

    if new_images:
        print(f"Found {len(new_images)} new image(s).")
        start_number = max_alt_number(html)

        new_tags = []
        for i, name in enumerate(new_images, start=1):
            base = os.path.splitext(name)[0]
            thumb = os.path.join(THUMB_DIR, f"{base}.webp")

            if not os.path.exists(thumb) or os.path.getsize(thumb) > MAX_BYTES:
                if compress_to_webp(sources[name], thumb):
                    size = os.path.getsize(thumb)
                    print(f"  Created thumb {base}.webp ({size} bytes)")
                else:
                    print(f"  WARNING: failed to compress {name}")
            else:
                print(f"  Reusing existing thumb {base}.webp")

            alt = start_number + i
            new_tags.append(
                f'    <img src="photos/{name}" alt="photo {alt}" '
                f'class="zoomable" loading="lazy" decoding="async" />'
            )

        block = "\n".join(new_tags)

        marker = '<main class="gallery-grid">'
        if marker not in html:
            print("ERROR: gallery-grid marker not found.")
            return

        html = html.replace(
            marker,
            marker + "\n" + block,
            1,
        )

        print(f"\nAdded {len(new_images)} image(s) to the top of the gallery grid.")

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    if not removed and not new_images:
        print("Nothing to do.")


if __name__ == "__main__":
    main()
