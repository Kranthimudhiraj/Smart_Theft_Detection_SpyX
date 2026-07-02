import cv2
import os
from datetime import datetime
import time

from core.detector import ObjectDetector
from core.tracker import ObjectTracker
from core.communication import DataLogger
from core.video_stream import VideoStream
from utils.fps import FPSCounter
from utils.drawing import draw_bounding_boxes, draw_ui

def main():
    """
    Main application loop for the Smart Retail Theft Detection System.
    Uses a high-performance multithreaded architecture.
    """
    print("Starting Smart Theft Detection System...")
    
    # Ensure output directories exist
    os.makedirs(os.path.join("outputs", "screenshots"), exist_ok=True)
    os.makedirs(os.path.join("outputs", "videos"), exist_ok=True)
    
    # Initialize Core Components
    detector = ObjectDetector(model_path="yolo11n.pt")
    tracker = ObjectTracker()
    data_logger = DataLogger(file_path="data/detections.json", flush_interval=15)
    fps_counter = FPSCounter()
    
    # Open WebCam via Multithreading (Producer-Consumer architecture)
    try:
        cap = VideoStream(0)
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Allow camera sensor to warm up
    time.sleep(1.0)

    # Video recording state setup
    is_recording = False
    video_writer = None
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    print("========================================")
    print("System Ready. Monitoring Started.")
    print("Controls:")
    print("  Q : Quit Application")
    print("  S : Save Screenshot")
    print("  R : Start/Stop Video Recording")
    print("========================================")

    try:
        while True:
            # Grab latest frame from background thread (Non-blocking)
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Error: Failed to grab frame from webcam stream. Exiting...")
                break

            # 1. AI Inference (Stateless Object Detection)
            detections = detector.detect(frame)
            
            # 2. Tracking (Filters internally to only track 'person' class)
            tracked_detections = tracker.update(detections, detector.class_names)
            
            # 3. Log Structured Data
            data_logger.log_detections(tracked_detections, detector.class_names)
            
            # 4. Update FPS
            fps_counter.update()
            
            # 5. Draw UI Overlays
            annotated_frame = draw_bounding_boxes(frame.copy(), tracked_detections, detector.class_names)
            annotated_frame = draw_ui(annotated_frame, fps_counter.get_fps(), is_recording)

            # 6. Handle Video Recording
            if is_recording and video_writer is not None:
                video_writer.write(annotated_frame)

            # 7. Display Frame
            cv2.imshow("SMART_THEFT_DETECTION - Live Feed", annotated_frame)

            # 8. Keyboard Controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join("outputs", "screenshots", f"screenshot_{timestamp}.png")
                cv2.imwrite(filepath, annotated_frame)
                print(f"[Info] Screenshot saved: {filepath}")
            elif key == ord('r'):
                is_recording = not is_recording
                if is_recording:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = os.path.join("outputs", "videos", f"recording_{timestamp}.mp4")
                    video_writer = cv2.VideoWriter(filepath, fourcc, 20.0, (frame_width, frame_height))
                    print(f"[Info] Started recording: {filepath}")
                else:
                    if video_writer:
                        video_writer.release()
                        video_writer = None
                    print("[Info] Stopped recording.")

    finally:
        # Graceful cleanup
        data_logger.close()
        cap.release()
        if video_writer:
            video_writer.release()
        cv2.destroyAllWindows()
        print("Application closed gracefully.")

if __name__ == "__main__":
    main()
