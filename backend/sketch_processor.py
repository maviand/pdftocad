import cv2
import numpy as np
from dxf_generator import generate_dxf_from_contours

def process_sketch(image_path: str, output_dxf_path: str):
    """
    Parses a raster image sketch, extracts line contours, and generates a DXF.
    """
    # 1. Load image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")
        
    # 2. Preprocess: Gaussian Blur to reduce paper noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    # 3. Thresholding: Adaptive thresholding works well for uneven lighting on paper
    # Inverse threshold so that the drawn lines become white (255) and background black (0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Optional: Morphological operations to close small gaps in lines
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # 4. Find Contours
    # RETR_LIST gets all contours without hierarchy
    # CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # 5. Approximate and filter contours
    processed_contours = []
    
    # Use image height to flip Y axis for CAD coordinates
    height = img.shape[0]
    
    for cnt in contours:
        # Filter out tiny noise contours
        if cv2.contourArea(cnt) < 10: 
            continue
            
        # Approximate to reduce point density and create more "CAD-like" lines
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        # Flatten and invert Y axis
        points = []
        for point in approx:
            x, y = point[0]
            points.append((x, -y)) # Invert Y for CAD
            
        if len(points) > 1:
            processed_contours.append(points)
            
    # Generate the DXF
    generate_dxf_from_contours(processed_contours, output_dxf_path)
