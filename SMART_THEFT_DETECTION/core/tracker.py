import supervision as sv
import numpy as np

class ObjectTracker:
    """
    Tracker Module.
    Handles tracking of detected objects across multiple video frames using ByteTrack.
    Currently configured to ONLY track people, assigning them unique Customer IDs.
    """
    def __init__(self):
        """
        Initializes the ByteTrack tracking algorithm via Supervision.
        """
        self.tracker = sv.ByteTrack()

    def update(self, detections_list, class_names):
        """
        Updates the tracker with new detections. Filters for people only.
        
        Args:
            detections_list: List of current frame detections (box_xyxy, confidence, class_id).
            class_names: Dictionary mapping class IDs to names (used to identify 'person').
            
        Returns:
            list: Tracked people with unique IDs + untracked other objects:
                  (box_xyxy, confidence, class_id, [tracker_id])
        """
        person_detections = []
        other_detections = []
        
        # Separate people from other objects
        for det in detections_list:
            cls_id = int(det[2])
            class_name = class_names.get(cls_id, "").lower()
            if class_name == "person":
                person_detections.append(det)
            else:
                other_detections.append(det)
                
        # Convert raw person detections to supervision Detections object
        if len(person_detections) > 0:
            xyxy = np.array([d[0] for d in person_detections])
            confidence = np.array([d[1] for d in person_detections])
            class_id = np.array([d[2] for d in person_detections])
            
            detections_sv = sv.Detections(
                xyxy=xyxy,
                confidence=confidence,
                class_id=class_id
            )
        else:
            detections_sv = sv.Detections.empty()
            
        # Update the tracker for people
        tracked_sv = self.tracker.update_with_detections(detections_sv)
        
        # Reconstruct the results list
        result = []
        
        # 1. Add tracked people (they get a tracker_id)
        if len(tracked_sv) > 0:
            for i in range(len(tracked_sv)):
                xyxy_box = tracked_sv.xyxy[i]
                conf = tracked_sv.confidence[i]
                cls_id = tracked_sv.class_id[i]
                track_id = tracked_sv.tracker_id[i]
                result.append((xyxy_box, conf, cls_id, track_id))
                
        # 2. Add other non-person objects (no tracker_id, just the raw detection)
        result.extend(other_detections)
                
        return result
