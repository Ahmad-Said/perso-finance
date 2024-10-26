import os
from PyPDF2 import PdfReader, PdfWriter

def merge_pdfs_with_bookmarks(pdf_files: list[str], output_filename: str):
    """
    Merge multiple PDF files into a single PDF with bookmarks for each file.
    Example:
    >>> pdf_files = ['file1.pdf', 'file2.pdf']
    >>> merge_pdfs_with_bookmarks(pdf_files, 'merged_file.pdf')

    :return: Path to the merged PDF file
    """
    pdf_writer = PdfWriter()
    current_page = 0

    for pdf_file in pdf_files:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        # Add pages and keep track of page count
        for page_num in range(num_pages):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        # Add a bookmark with the filename as the title
        bookmark_title = os.path.splitext(os.path.basename(pdf_file))[0]
        pdf_writer.add_outline_item(bookmark_title, current_page)
        current_page += num_pages

    # create parent dir
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    # Write the output PDF
    with open(output_filename, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    output_filename = os.path.abspath(output_filename)
    print(f"PDFs merged into: {output_filename}")

    return output_filename
