"""
PDF Generator for Kobon Triangle Paper
Uses Playwright to render HTML with MathJax and export to PDF
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def generate_pdf():
    project_root = Path(__file__).parent.parent
    html_path = project_root / "paper.html"
    pdf_path = project_root / "paper.pdf"
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Open the HTML file
        page.goto(f"file:///{html_path.as_posix()}")
        
        # Wait for MathJax to render all equations
        # MathJax adds a 'typeset' attribute when done
        page.wait_for_timeout(3000)  # Give MathJax time to load and render
        
        # Additional wait for any pending typesetting
        try:
            page.evaluate("""
                () => {
                    if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                        return MathJax.typesetPromise();
                    }
                }
            """)
        except:
            pass  # MathJax might not expose this method
        
        page.wait_for_timeout(2000)  # Extra time for rendering
        
        # Generate PDF with print settings
        page.pdf(
            path=str(pdf_path),
            format="A4",
            margin={
                "top": "2.5cm",
                "bottom": "2.5cm",
                "left": "2cm",
                "right": "2cm"
            },
            print_background=True,
            scale=0.9
        )
        
        browser.close()
        
    print(f"✓ PDF generated successfully: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_pdf()
