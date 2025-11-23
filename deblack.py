import os
import argparse
from PIL import Image

SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".bmp")


def process_image(path: str, tolerance: int, replacement: int):
    """Convert black pixels to near-black and save as new file."""
    img = Image.open(path).convert("RGB")
    pixels = img.load()

    width, height = img.size
    modified = False

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            if r <= tolerance and g <= tolerance and b <= tolerance:
                pixels[x, y] = (replacement, replacement, replacement)
                modified = True

    if modified:
        base, ext = os.path.splitext(path)
        new_path = f"{base}_processed{ext}"
        img.save(new_path)
        print(f"✔ Processed: {os.path.basename(path)} → {os.path.basename(new_path)}")
    else:
        print(f"⚪ Skipped (no black pixels found): {os.path.basename(path)}")


def main():
    parser = argparse.ArgumentParser(description="Convert black pixels to near-black for printing without black ink.")
    parser.add_argument("--tolerance", type=int, default=25,
                        help="RGB threshold for what counts as black (default: 25)")
    parser.add_argument("--replacement", type=int, default=50,
                        help="Replacement RGB value for near-black (default: 50)")
    args = parser.parse_args()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    images = [f for f in os.listdir(current_dir)
              if os.path.splitext(f)[1].lower() in SUPPORTED_FORMATS]

    if not images:
        print("⚠️ No supported image files found in this directory.")
        return

    print(f"🖨 Found {len(images)} image(s). Starting conversion...\n")

    for filename in images:
        process_image(os.path.join(current_dir, filename), args.tolerance, args.replacement)

    print("\n✅ Done! Processed images saved with '_processed' suffix.")


if __name__ == "__main__":
    main()
