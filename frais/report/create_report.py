import os.path
from datetime import datetime

import pandas as pd
from jinja2 import Template
import pdfkit

from const.const_gl import ConstGl


def create_summary_pdf(df: pd.DataFrame, freshness_date: str) -> str:
    """
    Create a PDF report from a DataFrame with enhanced styling and dynamic title
    Example:
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> create_summary_pdf(df, '2024-08-06')
    'data/temp/summary_table.pdf'
    :return: Path to the generated PDF file
    """
    # Define HTML template with enhanced styling and dynamic title
    html_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Thierry Lastname - Frais jusqu'à {{ freshness_date }}</title>
<style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; color: #333; }
    h2 { color: #0056b3; }
    .container { max-width: 800px; margin: auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
    th { background-color: #0056b3; color: white; }
</style>
</head>
<body>
    <div class="container">
        <h2>{{ person_fullname | safe }}</h2>
        <p><strong>Frais jusqu'à:</strong> {{ freshness_date }}</p>
        {{ data | safe }}
    </div>
</body>
</html>
""")

    # Generate HTML from DataFrame with dynamic freshness date
    html_output = html_template.render(
        person_fullname=ConstGl.PERSON_FULL_NAME,
        data=df.to_html(index=False),
        freshness_date=freshness_date
    )

    # Convert HTML to PDF
    temp_dir = ConstGl.TEMP_DIR
    html_file = f"{temp_dir}/frais_summary_table.html"
    pdf_file = f"{temp_dir}/frais_summary_table.pdf"
    os.makedirs(temp_dir, exist_ok=True)
    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_output)

    # download from https://wkhtmltopdf.org/downloads.html
    path_wkhtmltopdf = ConstGl.PATH_TO_WK_HTML_TO_PDF

    if not os.path.exists(path_wkhtmltopdf):
        print("wkhtmltopdf could not be found at {}".format(path_wkhtmltopdf))
        print("Let pdfkit find it automatically")
        pdfkit.from_file(html_file, pdf_file)
    else:
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdfkit.from_file(html_file, pdf_file, configuration=config)

    return pdf_file
