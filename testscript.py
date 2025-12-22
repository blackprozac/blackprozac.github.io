import os
from PIL import Image

# ---------- ABSOLUTE PATH FIX ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCE_DIR = os.path.join(SCRIPT_DIR, "photography", "photos")
THUMB_DIR = os.path.join(SOURCE_DIR, "thumb")
HTML_FILE = os.path.join(SCRIPT_DIR, "photography", "photography.html")
# -------------------------------------

THUMB_WIDTH = 600
WEBP_QUALITY = 60
SOURCE_EXTS = (".jpg", ".jpeg", ".png", ".JPG", ".PNG")


def debug_paths():
    print("SCRIPT_DIR :", SCRIPT_DIR)
    print("SOURCE_DIR :", SOURCE_DIR)
    print("THUMB_DIR  :", THUMB_DIR)
    print("HTML_FILE  :", HTML_FILE)
    print("-" * 40)


def ensure_thumb_dir():
    os.makedirs(THUMB_DIR, exist_ok=True)


def get_source_images():
    images = {}
    files = os.listdir(SOURCE_DIR)
    print("SOURCE FILES:", files)

    for f in files:
        if f.endswith(SOURCE_EXTS):
            base = os.path.splitext(f)[0]
            images[base] = f
    return images


def get_existing_thumbs():
    if not os.path.exists(THUMB_DIR):
        return set()

    thumbs = os.listdir(THUMB_DIR)
    print("THUMB FILES :", thumbs)

    return {
        os.path.splitext(f)[0]
        for f in thumbs
        if f.endswith(".webp")
    }


def create_missing_thumbs(source_images, existing_thumbs):
    new_images = []

    print("SOURCE BASES:", set(source_images.keys()))
    print("THUMB BASES :", existing_thumbs)

    missing = set(source_images.keys()) - existing_thumbs
    print("MISSING    :", missing)

    for base in missing:
        filename = source_images[base]

        src = os.path.join(SOURCE_DIR, filename)
        dst = os.path.join(THUMB_DIR, f"{base}.webp")

        try:
            with Image.open(src) as img:
                img = img.convert("RGB")
                w, h = img.size
                nh = int((THUMB_WIDTH / w) * h)
                img = img.resize((THUMB_WIDTH, nh), Image.LANCZOS)
                img.save(dst, "WEBP", quality=WEBP_QUALITY)

            new_images.append(filename)
            print(f"✔ CREATED: {base}.webp")

        except Exception as e:
            print(f"✖ ERROR: {filename} → {e}")

    return new_images


def inject_into_html(new_images):
    if not new_images:
        print("⚠ NOTHING TO INJECT")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    insert = "</main>"

    tags = "\n".join(
        f'<img src="photos/thumb/{os.path.splitext(img)[0]}.webp" '
        f'data-full="photos/{img}" class="zoomable" loading="lazy" />'
        for img in new_images
    )

    html = html.replace(insert, f"\n{tags}\n\n{insert}")

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✔ INJECTED {len(new_images)} IMAGE(S)")


def main():
    debug_paths()
    ensure_thumb_dir()

    source_images = get_source_images()
    existing_thumbs = get_existing_thumbs()

    new_images = create_missing_thumbs(source_images, existing_thumbs)
    inject_into_html(new_images)


if __name__ == "__main__":
    main()
