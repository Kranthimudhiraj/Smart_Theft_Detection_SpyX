import json
import os
from datetime import datetime

class DataLogger:
    """
    Communication Module.
    Handles structuring detection data and logging it to a JSON file.
    Designed to be read by other modules.
    """
    def __init__(self, file_path="data/detections.json", flush_interval=15):
        """
        Initializes the DataLogger.
        
        Args:
            file_path: Path to the JSON log file.
            flush_interval: Number of frames to buffer before writing to disk 
                            (to maintain high FPS).
        """
        self.file_path = file_path
        self.flush_interval = flush_interval
        self.buffer = []
        self.frame_count = 0
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Initialize an empty JSON array if starting fresh
        # (This avoids reading a massive legacy file on startup)
        with open(self.file_path, 'w') as f:
            json.dump([], f)

    def log_detections(self, detections, class_names):
        """
        Structures and buffers current frame detections.
        
        Args:
            detections: List of (box_xyxy, conf, cls_id, track_id)
            class_names: Dictionary mapping class IDs to names
        """
        if not detections:
            return
            
        timestamp = datetime.now().isoformat()
        
        for det in detections:
            box = det[0]
            conf = float(det[1])
            cls_id = int(det[2])
            track_id = int(det[3]) if len(det) > 3 and det[3] is not None else -1
            
            # Convert xyxy to x, y, w, h
            x1, y1, x2, y2 = map(int, box)
            w = x2 - x1
            h = y2 - y1
            
            # Format object name
            obj_name = class_names.get(cls_id, f"Unknown_{cls_id}").capitalize()
            
            # Create structured log entry
            log_entry = {
                "timestamp": timestamp,
                "customer_id": track_id,
                "object": obj_name,
                "confidence": round(conf, 2),
                "location": [x1, y1, w, h]
            }
            self.buffer.append(log_entry)
            
        self.frame_count += 1
        
        # Flush to disk periodically to avoid locking up the main loop
        if self.frame_count >= self.flush_interval:
            self.flush()

    def flush(self):
        """
        Writes the buffered logs to the JSON file on disk.
        """
        if not self.buffer:
            return
            
        # Read existing data
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
            
        # Append new data
        data.extend(self.buffer)
        
        # Clear buffer
        self.buffer = []
        self.frame_count = 0
        
        # Write back to file safely
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def close(self):
        """
        Forces a final flush before shutting down.
        """
        self.flush()
