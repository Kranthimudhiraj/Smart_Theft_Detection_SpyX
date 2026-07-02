import time

class FPSCounter:
    """
    Utility class to compute average FPS during processing.
    """
    def __init__(self, smoothing_factor=0.9):
        self.smoothing_factor = smoothing_factor
        self.fps = 0.0
        self.last_time = time.time()

    def update(self):
        """
        Updates the FPS counter upon processing a new frame.
        """
        current_time = time.time()
        time_diff = current_time - self.last_time
        self.last_time = current_time
        
        if time_diff > 0:
            current_fps = 1.0 / time_diff
            if self.fps == 0.0:
                self.fps = current_fps
            else:
                self.fps = (self.fps * self.smoothing_factor) + (current_fps * (1.0 - self.smoothing_factor))

    def get_fps(self):
        """
        Calculates the current average FPS.
        
        Returns:
            float: Frames per second.
        """
        return self.fps
