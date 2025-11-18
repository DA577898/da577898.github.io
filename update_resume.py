
import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file and performs initial cleaning."""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    # Clean up some common extraction artifacts
    text = text.replace(' \n', '\n')  # remove trailing spaces on lines
    text = re.sub(r' +', ' ', text) # collapse multiple spaces
    return text

def format_resume_to_html(text):
    """Formats the raw resume text into structured HTML."""
    lines = text.strip().split('\n')

    html_parts = []
    in_list = False

    # Header section (first few lines are special)
    html_parts.append(f"<h1>{lines[0].strip()}</h1>")
    html_parts.append(f"<p class='contact-info'>{lines[1].strip()}</p>")

    # Find where the summary ends and education begins
    summary_end_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "EDUCATION":
            summary_end_index = i
            break

    summary = " ".join(lines[2:summary_end_index]).strip()
    html_parts.append(f"<p class='summary'>{summary}</p>")

    # Process from EDUCATION onwards
    content_lines = lines[summary_end_index:]

    section_headers = ["EDUCATION", "PROJECTS", "SKILLS", "CERTIFICATIONS", "WORK EXPERIENCE", "INVOLVEMENT"]

    for line in content_lines:
        line = line.strip()
        if not line:
            continue

        if line in section_headers:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append(f'<h2>{line.title()}</h2>')
        elif line.startswith('•'):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            list_item_content = line[1:].strip()
            html_parts.append(f'<li>{list_item_content}</li>')
        else:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            # These are sub-headings like job titles or university names
            html_parts.append(f"<div class='resume-item'><h3>{line}</h3></div>")

    if in_list:
        html_parts.append('</ul>')

    return "\n".join(html_parts)

def generate_resume_page(html_content, template_path, output_path):
    """Injects the generated HTML into a template file."""
    try:
        with open(template_path, 'r') as f:
            template = f.read()

        final_html = template.replace('{{RESUME_CONTENT}}', html_content)

        with open(output_path, 'w') as f:
            f.write(final_html)
        print(f"Successfully generated {output_path}")
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        print("Please create the template file first.")


if __name__ == "__main__":
    pdf_path = 'src/Daniel Hernandez Resume.pdf'
    template_path = 'resume/template.html'
    output_path = 'resume/index.html'

    print("Extracting text from PDF...")
    resume_text = extract_text_from_pdf(pdf_path)

    print("Formatting text to HTML...")
    resume_html = format_resume_to_html(resume_text)

    print("\n--- Generated HTML ---")
    print(resume_html)
    print("----------------------\n")

    # The following function will be used in a later step
    print(f"Generating final resume page using template '{template_path}'...")
    generate_resume_page(resume_html, template_path, output_path)
