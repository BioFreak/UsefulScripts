import os
import sys
import zipfile
import hashlib
import shutil

MAX_BYTES = 200
MAX_EXTENSION_BYTES = 20


def truncate_utf8(text, max_bytes):
    """Truncate string to at most max_bytes without breaking UTF-8."""
    encoded = text.encode("utf-8")

    if len(encoded) <= max_bytes:
        return text

    encoded = encoded[:max_bytes]

    # The cut may occur in the middle of a UTF-8 character.
    return encoded.decode("utf-8", errors="ignore")


def shorten(name):
    encoded = name.encode("utf-8")

    if len(encoded) <= MAX_BYTES:
        return name

    digest = hashlib.sha1(encoded).hexdigest()[:8]
    suffix = "_" + digest

    base, ext = os.path.splitext(name)

    # Preserve only reasonable extensions such as .pdf/.docx/.txt.
    # A gigantic ".extension" is treated as part of the filename.
    if (
        not ext
        or len(ext.encode("utf-8")) > MAX_EXTENSION_BYTES
        or "/" in ext
    ):
        base = name
        ext = ""

    reserved_bytes = len((suffix + ext).encode("utf-8"))
    available_bytes = MAX_BYTES - reserved_bytes

    if available_bytes <= 0:
        # Extremely pathological extension: discard it.
        ext = ""
        available_bytes = MAX_BYTES - len(suffix.encode("utf-8"))

    base = truncate_utf8(base, available_bytes)

    return base + suffix + ext


if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} archive.zip [output_directory]")
    sys.exit(1)

zip_path = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted"

with zipfile.ZipFile(zip_path) as archive:
    items = archive.infolist()
    total = len(items)

    for number, item in enumerate(items, 1):
        parts = item.filename.split("/")
        parts = [shorten(part) for part in parts if part]

        if not parts:
            continue

        target = os.path.join(output_dir, *parts)

        print(
            f"[{number}/{total}] {item.filename[:100]}",
            flush=True
        )

        if item.is_dir():
            os.makedirs(target, exist_ok=True)
            continue

        os.makedirs(os.path.dirname(target), exist_ok=True)

        with archive.open(item) as src, open(target, "wb") as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)

print(f"\nExtracted to: {output_dir}")
