### deblack.py — Replace black pixels with near-black to bypass dead black cartridge.

Usage:
    `python deblack.py [--tolerance 10] [--replacement 16]`

Description:
    - Processes all images in the script's directory (*.png, *.jpg, *.jpeg, *.bmp).
    - Detects pixels where R, G, B <= tolerance.
    - Replaces them with (replacement, replacement, replacement).
    - Saves result as filename_processed.ext
