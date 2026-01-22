
import sys
from pypdf import PdfReader, PdfWriter, PageObject

def merge_pdfs(content_path, numbers_path, output_path):
    print(f"Merging {content_path} and {numbers_path}...")
    
    content_reader = PdfReader(content_path)
    numbers_reader = PdfReader(numbers_path)
    writer = PdfWriter()
    
    num_pages = len(content_reader.pages)
    print(f"Document has {num_pages} pages.")
    
    for i in range(num_pages):
        content_page = content_reader.pages[i]
        
        # Get corresponding number page (if available)
        if i < len(numbers_reader.pages):
            number_page = numbers_reader.pages[i]
            # Merge number page ON TOP of content page
            content_page.merge_page(number_page)
            
        writer.add_page(content_page)
        
    with open(output_path, "wb") as f_out:
        writer.write(f_out)
        
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    merge_pdfs("paper_clean.pdf", "paper_numbers.pdf", "paper.pdf")
