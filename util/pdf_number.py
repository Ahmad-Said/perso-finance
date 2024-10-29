from const.const_gl import ConstGl
import fitz  # PyMuPDF


def add_page_numbers(input_pdf_path, output_pdf_path):
    # Open the original PDF
    doc = fitz.open(input_pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Define where the page number will be added
        text = f"Page {page_num + 1}"
        x, y = page.rect.width / 2, page.rect.height - 75  # Adjust to place text at bottom-right

        # Add the text as an overlay
        page.insert_text((x, y),
                         text,
                         fontname="helv",
                         fontsize=12,
                         rotate=0,
                         color=(0, 86 / 255, 179 / 255), )

    # Save the output with original bookmarks
    doc.save(output_pdf_path)


if __name__ == "__main__":
    # Example usage
    input_file = ConstGl.TEMP_DIR + "/input.pdf"
    output_file = ConstGl.TEMP_DIR + "/output_with_numbers.pdf"
    add_page_numbers(input_file, output_file)
