from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


root = Path(__file__).resolve().parents[3]
pages_dir = root / "tmp" / "pdfs" / "drawing_templates" / "pages"
output_dir = root / "output" / "pdf"
output_dir.mkdir(parents=True, exist_ok=True)
output = output_dir / "软件工程II八类画图模板.pdf"

page_w, page_h = landscape(A4)
c = canvas.Canvas(str(output), pagesize=(page_w, page_h), pageCompression=1)

for image_path in sorted(pages_dir.glob("*.png")):
    c.drawImage(str(image_path), 0, 0, width=page_w, height=page_h, preserveAspectRatio=False)
    c.showPage()

c.save()
print(output)
