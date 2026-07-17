"""
Configuration settings for the Smart Theft Detection System.
Contains constants, thresholds, and environment-specific variables.
"""

# App Information
APP_NAME = "Smart Theft Detection"
VERSION = "1.0.0"

# AI/ML Thresholds & Parameters
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45          # Aggressive NMS to avoid duplicate boxes
INFERENCE_SIZE = 144          # Target YOLO resolution (640 is standard)
HALF_PRECISION = False         # Use FP16 on GPU for maximum speed

# Allowed Classes for Detection
ALLOWED_CLASSES = [
    "person", "bottle", "cup", "apple", "banana", "orange",
    "backpack", "handbag", "cell phone", "book", "shopping cart", 
    "chair", "laptop", "mouse", "keyboard", "remote", "tv",
    "box"
]

# Express Server Configuration for Telemetry
EXPRESS_SERVER_URL = "http://localhost:3001"

