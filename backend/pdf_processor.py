import fitz
from dxf_generator import generate_dxf

def process_pdf(pdf_path: str, output_dxf_path: str):
    """
    Parses a vector PDF and generates a DXF file.
    Extracts paths (lines/curves), text, and highlights.
    """
    doc = fitz.open(pdf_path)
    
    # Data to pass to DXF generator
    extracted_data = {
        "paths": [],
        "text_blocks": [],
        "highlights": []
    }
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 1. Extract vector paths
        paths = page.get_drawings()
        for p in paths:
            extracted_data["paths"].append(p)
            
        # 2. Extract text blocks
        text_blocks = page.get_text("blocks")
        # Text blocks are usually (x0, y0, x1, y1, "text", block_no, block_type)
        for b in text_blocks:
            if b[6] == 0:  # Block type 0 is text
                extracted_data["text_blocks"].append(b)
                
        # 3. Extract annotations (specifically Highlights)
        for annot in page.annots():
            if annot.type[0] == fitz.PDF_ANNOT_HIGHLIGHT:
                rect = annot.rect
                # Try to extract the highlighted text underneath
                highlighted_text = page.get_text("text", clip=rect).strip()
                extracted_data["highlights"].append({
                    "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
                    "text": highlighted_text,
                    "color": annot.colors.get('stroke', [1, 0, 0])  # Default to red if missing
                })
                
    doc.close()
    
    # Generate DXF
    generate_dxf(extracted_data, output_dxf_path)
