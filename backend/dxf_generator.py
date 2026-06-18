import ezdxf

def generate_dxf(extracted_data: dict, output_path: str):
    """
    Takes extracted vector paths, text, and highlights, and generates a DXF.
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Create specific layers
    doc.layers.add("Building_Lines", color=7)  # 7 is black/white
    doc.layers.add("Measurement_Lines", color=5) # 5 is blue
    doc.layers.add("Text", color=3)      # 3 is green
    doc.layers.add("Highlights", color=1) # 1 is red
    
    # Process vector paths
    for p in extracted_data["paths"]:
        # Determine if it's a measurement line or building line
        is_measurement = False
        width = p.get("width")
        dashes = p.get("dashes")
        
        if width is not None and width < 1.0:
            is_measurement = True
        if dashes and len(dashes) > 0: # Often dashed lines are annotations/measurements
            is_measurement = True
            
        layer_name = "Measurement_Lines" if is_measurement else "Building_Lines"
        
        for item in p["items"]:
            if item[0] == "l":  # Line
                p1, p2 = item[1], item[2]
                msp.add_line((p1.x, -p1.y), (p2.x, -p2.y), dxfattribs={"layer": layer_name})
            elif item[0] == "c":  # Cubic bezier (curve)
                p1, p2, p3, p4 = item[1], item[2], item[3], item[4]
                msp.add_spline(fit_points=[(p1.x, -p1.y), (p4.x, -p4.y)], dxfattribs={"layer": layer_name})
            elif item[0] == "re": # Rectangle
                rect = item[1]
                points = [
                    (rect.x0, -rect.y0),
                    (rect.x1, -rect.y0),
                    (rect.x1, -rect.y1),
                    (rect.x0, -rect.y1),
                    (rect.x0, -rect.y0)
                ]
                msp.add_lwpolyline(points, dxfattribs={"layer": layer_name})

    # Process text
    for b in extracted_data["text_blocks"]:
        x0, y0, x1, y1, text, block_no, block_type = b
        msp.add_text(
            text.replace('\n', ' '), 
            dxfattribs={
                "layer": "Text", 
                "height": 12 # Default height, could be derived from rect size
            }
        ).set_placement((x0, -y0))
        
    # Process highlights (Measurements)
    for h in extracted_data["highlights"]:
        rect = h["rect"]
        text = h["text"]
        x0, y0, x1, y1 = rect
        
        # Draw a bounding box for the highlight
        points = [
            (x0, -y0), (x1, -y0), (x1, -y1), (x0, -y1), (x0, -y0)
        ]
        msp.add_lwpolyline(points, dxfattribs={"layer": "Highlights"})
        
        # Add the highlighted text on the Highlights layer
        if text:
            msp.add_text(
                f"[MEASUREMENT]: {text}", 
                dxfattribs={
                    "layer": "Highlights",
                    "height": 14,
                    "color": 1 # Red
                }
            ).set_placement((x0, -y0))

    # Save the DXF
    doc.saveas(output_path)

def generate_dxf_from_contours(contours: list, output_path: str):
    """
    Takes processed contours from an image (sketch) and generates a DXF.
    """
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Create specific layer for sketch
    doc.layers.add("Sketch_Lines", color=7)
    
    for cnt in contours:
        # A contour is a list of (x, y) tuples
        if len(cnt) > 2:
            # We close the polyline if it represents a closed shape,
            # but since users might draw open lines, let's just draw them open
            msp.add_lwpolyline(cnt, dxfattribs={"layer": "Sketch_Lines"}, close=True)
            
    doc.saveas(output_path)
