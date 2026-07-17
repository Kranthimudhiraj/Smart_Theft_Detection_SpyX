import json
import os
from datetime import datetime
import time
import queue
import threading
import requests

class HttpSender:
    """
    Asynchronous HTTP client to send telemetry events to the Express server
    without blocking the OpenCV / YOLO thread.
    """
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def send_event(self, endpoint, data):
        self.queue.put((endpoint, data))

    def _run(self):
        while True:
            endpoint, data = self.queue.get()
            try:
                url = f"{self.server_url}{endpoint}"
                requests.post(url, json=data, timeout=3)
            except Exception as e:
                # Silently drop request if server is offline
                pass
            finally:
                self.queue.task_done()

class DataLogger:
    """
    Communication Module.
    Handles structuring detection data, logging it to a JSON file,
    and dispatching telemetry alerts to the retail guardian server.
    """
    def __init__(self, file_path="data/detections.json", flush_interval=15):
        """
        Initializes the DataLogger.
        
        Args:
            file_path: Path to the JSON log file.
            flush_interval: Number of frames to buffer before writing to disk.
        """
        self.file_path = file_path
        self.flush_interval = flush_interval
        self.buffer = []
        self.frame_count = 0
        
        # Track active customers to trigger entry/exit events
        self.active_customers = {} # maps track_id to last_seen_frame
        self.frame_number = 0
        self.last_item_sent_time = 0
        
        # Initialize HttpSender using config
        try:
            from config.settings import EXPRESS_SERVER_URL
            self.http_sender = HttpSender(EXPRESS_SERVER_URL)
        except Exception:
            self.http_sender = HttpSender("http://localhost:3001")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        # Initialize an empty JSON array if starting fresh
        with open(self.file_path, 'w') as f:
            json.dump([], f)

    def log_detections(self, detections, class_names):
        """
        Structures and buffers current frame detections, and sends
        live HTTP telemetry events to the main Express dashboard.
        
        Args:
            detections: List of (box_xyxy, conf, cls_id, track_id)
            class_names: Dictionary mapping class IDs to names
        """
        if not detections:
            return
            
        self.frame_number += 1
        timestamp = datetime.now().isoformat()
        
        current_frame_customers = []
        has_items = False
        detected_items = []
        
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
            obj_name = class_names.get(cls_id, f"Unknown_{cls_id}").lower()
            
            if obj_name == "person":
                if track_id != -1:
                    current_frame_customers.append(track_id)
                    # If this is a new customer, trigger entry alert
                    if track_id not in self.active_customers:
                        customer_id_str = f"CUST-{track_id:03d}"
                        self.http_sender.send_event("/api/hardware/yolo", {
                            "event": "customer_entered",
                            "customerId": customer_id_str
                        })
                        print(f"[Telemetry] Sent customer_entered for {customer_id_str}")
                    # Update last seen frame
                    self.active_customers[track_id] = self.frame_number
            else:
                detected_items.append(obj_name)
                has_items = True
            
            # Create structured log entry
            log_entry = {
                "timestamp": timestamp,
                "customer_id": track_id,
                "object": obj_name.capitalize(),
                "confidence": round(conf, 2),
                "location": [x1, y1, w, h]
            }
            self.buffer.append(log_entry)
            
        # Clean up stale customers (not seen for 100 frames)
        stale_ids = [tid for tid, last_frame in self.active_customers.items() 
                     if self.frame_number - last_frame > 100]
        for tid in stale_ids:
            del self.active_customers[tid]
            
        # If non-person items are detected, send item picked event with a debounce
        if has_items:
            current_time = time.time()
            if current_time - self.last_item_sent_time > 5.0: # 5 second debounce
                self.last_item_sent_time = current_time
                # Fallback to the first active customer in current frame, or fallback to first overall
                active_cust_id = current_frame_customers[0] if current_frame_customers else 1
                customer_id_str = f"CUST-{active_cust_id:03d}"
                self.http_sender.send_event("/api/hardware/yolo", {
                    "event": "item_picked",
                    "customerId": customer_id_str,
                    "itemsPicked": len(detected_items)
                })
                print(f"[Telemetry] Sent item_picked ({', '.join(detected_items)}) for {customer_id_str}")
                
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
