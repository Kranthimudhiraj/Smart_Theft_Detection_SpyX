# Smart Retail Theft Detection System (SMART_THEFT_DETECTION)

An AI-powered smart retail theft detection system designed with a modular and scalable architecture, ready for production use.

## Technology Stack
- **Language**: Python 3.12
- **AI/ML**: YOLOv11 (Ultralytics) for object detection
- **Vision**: OpenCV, NumPy
- **Tracking**: Supervision, ByteTrack (planned)
- **Database**: SQLite (planned for local storage)

## Project Structure
- `app.py`: Main application entry point.
- `config/`: Configuration settings and constants.
- `core/`: Core logic including detection, tracking, and communication.
- `data/`: Local data storage for customers, products, and logs.
- `utils/`: Utility functions and helpers.
- `assets/`, `docs/`, `models/`, `outputs/`, `tests/`: Supporting directories for assets, documentation, model weights, and tests.

## Setup Instructions

1. Ensure you have **Python 3.12** installed.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
