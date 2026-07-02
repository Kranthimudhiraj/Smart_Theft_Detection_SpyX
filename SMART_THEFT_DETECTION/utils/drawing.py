import cv2

def get_color_for_class(cls_id):
    """
    Generates a unique, deterministic, and bright color for a given class ID.
    """
    b = (cls_id * 57) % 200 + 55
    g = (cls_id * 113) % 200 + 55
    r = (cls_id * 191) % 200 + 55
    return (int(b), int(g), int(r))

def draw_bounding_boxes(frame, detections, class_names):
    """
    Draws bounding boxes, labels, and center points on the provided frame.
    
    Args:
        frame: The image frame to annotate.
        detections: List of detections (box_xyxy, conf, class_id, [tracker_id]).
        class_names: Dictionary mapping class IDs to class names.
        
    Returns:
        Annotated frame.
    """
    for det in detections:
        box = det[0]
        conf = det[1]
        cls_id = det[2]
        track_id = det[3] if len(det) > 3 else None
        
        x1, y1, x2, y2 = map(int, box)
        class_name = class_names.get(cls_id, f"Unknown_{cls_id}").lower()
        
        # Determine label text (Customer logic vs general object logic)
        if track_id is not None and class_name == "person":
            label = f"Customer {track_id} {conf:.2f}"
        else:
            label = f"{class_name.capitalize()} {conf:.2f}"
        
        # Get deterministic unique color per class
        color = get_color_for_class(cls_id)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw Center Point for tracked people
        if track_id is not None and class_name == "person":
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            # Solid inner circle
            cv2.circle(frame, (cx, cy), 4, color, -1)
            # High-contrast white border to make it pop
            cv2.circle(frame, (cx, cy), 4, (255, 255, 255), 1)
        
        # Calculate text size to draw background rectangle
        (w, h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        
        # Ensure label background doesn't draw outside the top of the frame
        y_bg = max(y1, h + 5)
        
        # Draw label background
        cv2.rectangle(frame, (x1, y_bg - h - 5), (x1 + w + 4, y_bg + 4), color, -1)
        
        # Draw label text (white text for good contrast)
        cv2.putText(frame, label, (x1 + 2, y_bg), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
    return frame

def draw_ui(frame, fps, is_recording):
    """
    Draws UI overlays such as FPS, recording status, and instructions.
    """
    # Draw FPS with a dark semi-transparent background for readability
    fps_text = f"FPS: {fps:.1f}"
    (w, h), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    cv2.rectangle(frame, (5, 5), (15 + w, 15 + h + 10), (0, 0, 0), -1) 
    cv2.putText(frame, fps_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    
    # Draw recording indicator
    if is_recording:
        cv2.circle(frame, (20, 60), 8, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (35, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
        
    # Draw instructions at the bottom with a dark background
    instructions = "Q: Quit | S: Screenshot | R: Record"
    (w, h), _ = cv2.getTextSize(instructions, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    frame_h, frame_w = frame.shape[:2]
    cv2.rectangle(frame, (5, frame_h - h - 15), (15 + w, frame_h - 5), (0, 0, 0), -1)
    cv2.putText(frame, instructions, (10, frame_h - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                
    return frame
