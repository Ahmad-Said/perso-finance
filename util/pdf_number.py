from const.const_gl import ConstGl

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def add_page_numbers(input_pdf_path, output_pdf_path):
    # Open the original PDF
    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    for i in range(len(pdf_reader.pages)):
        # Create an overlay PDF with the page number
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        # Add page number text at the bottom-right corner
        can.drawString(500, 10, f"Page {i + 1}")
        can.save()

        # Move the overlay PDF to start for merging
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        overlay_page = overlay_pdf.pages[0]

        # Merge the overlay with the original PDF page
        original_page = pdf_reader.pages[i]
        original_page.merge_page(overlay_page)
        pdf_writer.add_page(original_page)

    # Write out the new PDF
    with open(output_pdf_path, "wb") as output_pdf_file:
        pdf_writer.write(output_pdf_file)

if __name__ == "__main__":
    # Example usage
    input_file = ConstGl.TEMP_DIR + "/input.pdf"
    output_file = ConstGl.TEMP_DIR + "/output_with_numbers.pdf"
    add_page_numbers(input_file, output_file)

