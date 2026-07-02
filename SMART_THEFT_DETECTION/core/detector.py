import torch
from ultralytics import YOLO
import sys
import os

# Add parent directory to path to allow importing from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import CONFIDENCE_THRESHOLD, ALLOWED_CLASSES, INFERENCE_SIZE, HALF_PRECISION, IOU_THRESHOLD

class ObjectDetector:
    """
    Class responsible for detecting objects in a frame using YOLOv11.
    Focused purely on optimized AI inference.
    """
    def __init__(self, model_path="yolo11n.pt"):
        """
        Initializes the object detector and loads the YOLO model.
        Automatically falls back to CPU if GPU is not available.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Detector] Initializing model on device: {self.device}")
        
        # Load YOLOv11 model (will download automatically if missing)
        self.model = YOLO(model_path)
        
        # Expose class names for the UI to use
        self.class_names = self.model.names
        
        # Determine allowed class IDs based on config/settings.py
        self.allowed_class_ids = []
        if ALLOWED_CLASSES:
            allowed_lower = {c.lower() for c in ALLOWED_CLASSES}
            for cls_id, cls_name in self.class_names.items():
                if cls_name.lower() in allowed_lower:
                    self.allowed_class_ids.append(cls_id)
        
        if not self.allowed_class_ids and ALLOWED_CLASSES:
            print("[Warning] None of the specified ALLOWED_CLASSES were found in the model's vocabulary.")

    def detect(self, frame):
        """
        Runs highly optimized object detection on the provided frame.
        
        Args:
            frame: The input image/frame (BGR from OpenCV).
            
        Returns:
            list: A list of detections, each is a tuple: (box_xyxy, confidence, class_id)
        """
        filter_classes = self.allowed_class_ids if self.allowed_class_ids else None
        
        # Apply Half Precision (FP16) safely only if CUDA is being used
        use_half = HALF_PRECISION and self.device == "cuda"
        
        # Run inference (YOLO natively ignores detections below conf threshold)
        results = self.model(frame, 
                             device=self.device, 
                             verbose=False, 
                             conf=CONFIDENCE_THRESHOLD, 
                             iou=IOU_THRESHOLD, 
                             imgsz=INFERENCE_SIZE, 
                             half=use_half,
                             classes=filter_classes)[0]
        
        detections = []
        for box in results.boxes:
            # Extract coordinates, confidence, and class ID
            xyxy = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())
            
            detections.append((xyxy, conf, cls_id))
            
        return detections
