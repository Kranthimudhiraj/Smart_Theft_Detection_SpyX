import cv2
import threading
import time

class VideoStream:
    """
    Multithreaded Video Capture to eliminate I/O blocking.
    Continuously reads frames in a background thread and exposes the most recent frame.
    """
    def __init__(self, src=0):
        """
        Initializes the video stream and starts the background thread.
        """
        self.stream = cv2.VideoCapture(src, cv2.CAP_V4L2)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        if not self.stream.isOpened():
            raise ValueError(f"Failed to open video source: {src}")
            
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        
        # Start the background thread
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True # Daemon thread exits when main program exits
        self.thread.start()
        
    def update(self):
        """
        Continuously polls the camera for new frames.
        """
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if not grabbed:
                self.stop()
                break
                
            self.grabbed, self.frame = grabbed, frame
            # Prevent thread starvation 
            time.sleep(0.005)
            
    def read(self):
        """
        Returns the latest frame instantly without waiting on I/O.
        """
        return self.grabbed, self.frame
        
    def stop(self):
        """
        Flags the thread to stop polling.
        """
        self.stopped = True
        
    def release(self):
        """
        Cleans up thread and camera resources.
        """
        self.stop()
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.stream.release()
        
    def get(self, prop_id):
        return self.stream.get(prop_id)
        
    def isOpened(self):
        return self.stream.isOpened
