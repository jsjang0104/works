import json
import argparse
import re
from pathlib import Path


def split_sentences(text):
    """
    문장 단위 쪼개기
    """
    if not text:
        return []

    # Regex for splitting: matches sentence ending marks followed by space or newline
    # Also handles the end of the string
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    # Filter out empty or very short strings
    return [s.strip() for s in sentences if s.strip()]


def perform_ocr(image_path, reader):
    """
    OCR 수행
    """
    # Using paragraph=True to combine nearby text boxes into paragraphs
    results = reader.readtext(str(image_path), paragraph=True, detail=0)

    if not results:
        return []

    full_text = " ".join(results)
    sentences = split_sentences(full_text)
    return sentences


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from JPEG images in a directory using OCR, saving at the sentence level."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="source-images",
        help="Directory containing images (default: source-images)",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="ocr_results.json",
        help="Output JSON file name (default: ocr_results.json)",
    )
    parser.add_argument(
        "--langs",
        nargs="+",
        default=["ko", "en"],
        help="Languages to use for OCR (default: ko en)",
    )

    args = parser.parse_args()

    # Try finding input_dir relative to current working directory
    input_path = Path(args.input_dir)
    if not input_path.exists():
        # Try finding input_dir relative to the script's directory
        script_dir = Path(__file__).resolve().parent
        input_path = script_dir / args.input_dir

    if not input_path.exists():
        print(
            f"Error: Input directory '{args.input_dir}' not found in CWD or script directory ({script_dir / args.input_dir})."
        )
        return

    # Check for EasyOCR installation
    try:
        import easyocr
    except ImportError:
        print(
            "EasyOCR is not installed. Please install it using 'pip install easyocr'."
        )
        return

    print(f"Initializing EasyOCR reader for {args.langs}...")
    reader = easyocr.Reader(args.langs)

    # Supported extensions
    image_extensions = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]
    image_files = [
        f for f in input_path.iterdir() if f.is_file() and f.suffix in image_extensions
    ]

    if not image_files:
        print(f"No supported image files found in '{input_path}'.")
        return

    # Natural sort for files like output-1.jpg, output-2.jpg, ..., output-10.jpg
    def natural_sort_key(s):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split("([0-9]+)", str(s))
        ]

    image_files.sort(key=natural_sort_key)

    print(f"Found {len(image_files)} image(s). Starting OCR...")

    results_list = []
    current_id = 1

    for i, img_file in enumerate(image_files):
        print(f"[{i+1}/{len(image_files)}] Processing {img_file.name}...")
        sentences = perform_ocr(img_file, reader)

        for sentence in sentences:
            # Format: {id, extracted text, original image file}
            result = {
                "id": current_id,
                "extracted_text": sentence,
                "original_image_file": img_file.name,
            }
            results_list.append(result)
            current_id += 1

    # Save to JSON
    output_path = Path(args.output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_list, f, ensure_ascii=False, indent=4)

    print(
        f"\nOCR extraction completed! Total {len(results_list)} sentences saved to '{args.output_file}'."
    )


if __name__ == "__main__":
    main()
