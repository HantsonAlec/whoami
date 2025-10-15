import sys
from pathlib import Path
import PyPDF2


def pdf_to_text(pdf_path: Path, output_path: Path = None):
    """Convert PDF to text file."""
    if not output_path:
        output_path = pdf_path.with_suffix(".txt")

    text = ""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Converted {pdf_path.name} -> {output_path.name}")
        print(f"Total characters: {len(text)}")

    except Exception as e:
        print(f"Error converting {pdf_path.name}: {e}")


def main():
    script_dir = Path(__file__).parent
    input_path = script_dir.parent / "data" / "pdfs"
    output_path = script_dir.parent / "data" / "texts"

    output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_path.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_path}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF file(s)\n")
    for pdf_file in pdf_files:
        output_file = output_path / pdf_file.with_suffix(".txt").name
        pdf_to_text(pdf_file, output_file)
        print()
    print("Conversion complete!")


if __name__ == "__main__":
    main()
