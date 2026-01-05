# backend/app/services/yolo_detector.py

import cv2
import numpy as np
import onnxruntime as ort
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class YOLOTableDetector:
    def __init__(self, model_path: str, conf_threshold: float = 0.85):
        """
        Initialize YOLO detector with ONNX model
        
        Args:
            model_path: Path to ONNX model file
            conf_threshold: Confidence threshold for detection
        """
        self.conf_threshold = conf_threshold
        
        try:
            self.session = ort.InferenceSession(
                model_path,
                providers=["CPUExecutionProvider"]
            )
            logger.info(f"YOLO model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def letterbox(self, img: np.ndarray, new_shape=(640, 640), color=(114, 114, 114)):
        """Resize image with padding (letterbox)"""
        h, w = img.shape[:2]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        r = min(new_shape[0] / h, new_shape[1] / w)
        new_unpad = (int(round(w * r)), int(round(h * r)))

        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        dw /= 2
        dh /= 2

        img_resized = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh)), int(round(dh))
        left, right = int(round(dw)), int(round(dw))

        # Ensure final dimensions are exactly new_shape
        img_padded = cv2.copyMakeBorder(
            img_resized, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=color
        )

        # Final check: ensure exact dimensions (handle rounding edge cases)
        if img_padded.shape[0] != new_shape[0] or img_padded.shape[1] != new_shape[1]:
            img_padded = cv2.resize(img_padded, (new_shape[1], new_shape[0]), interpolation=cv2.INTER_LINEAR)

        return img_padded, (r, r), (left, top)

    def preprocess(self, img: np.ndarray) -> Tuple[np.ndarray, Tuple, Tuple]:
        """Preprocess image for YOLO inference"""
        img_lb, ratio, dwdh = self.letterbox(img, (640, 640))
        img_lb = img_lb[:, :, ::-1] / 255.0
        img_lb = np.transpose(img_lb, (2, 0, 1)).astype(np.float32)
        img_lb = np.expand_dims(img_lb, axis=0)
        return img_lb, ratio, dwdh

    def scale_boxes(self, img_shape: Tuple[int, int], boxes: list, ratio: Tuple, dwdh: Tuple) -> list:
        """Scale boxes back to original image coordinates"""
        h0, w0 = img_shape
        gain = ratio[0]
        pad_w, pad_h = dwdh

        corrected = []
        for x1, y1, x2, y2, conf in boxes:
            x1 = (x1 - pad_w) / gain
            y1 = (y1 - pad_h) / gain
            x2 = (x2 - pad_w) / gain
            y2 = (y2 - pad_h) / gain

            x1 = max(0, min(int(x1), w0))
            y1 = max(0, min(int(y1), h0))
            x2 = max(0, min(int(x2), w0))
            y2 = max(0, min(int(y2), h0))

            corrected.append([x1, y1, x2, y2, conf])
        return corrected

    def detect_and_crop(self, image_path: str, output_path: str) -> Optional[np.ndarray]:
        """
        Detect table in image and save cropped result
        
        Args:
            image_path: Path to input image
            output_path: Path to save cropped table
            
        Returns:
            Cropped image array or None if no detection
        """
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Could not read image: {image_path}")
            return None
            
        h, w = img.shape[:2]

        # Preprocess
        inp, ratio, dwdh = self.preprocess(img)

        # Inference
        try:
            pred = self.session.run(None, {"images": inp})[0]  # (1,5,8400)
            pred = pred[0].T  # -> (8400, 5)
        except Exception as e:
            logger.error(f"YOLO inference error: {e}")
            return None

        # Collect boxes
        det_boxes = []
        for cx, cy, bw, bh, conf in pred:
            if conf < self.conf_threshold:
                continue

            x1 = cx - bw / 2
            y1 = cy - bh / 2
            x2 = cx + bw / 2
            y2 = cy + bh / 2
            det_boxes.append([x1, y1, x2, y2, conf])

        if not det_boxes:
            logger.info(f"No table detected in {Path(image_path).name}")
            return None

        # Scale to original coordinates
        det_boxes = self.scale_boxes((h, w), det_boxes, ratio, dwdh)

        # Choose highest confidence box
        x1, y1, x2, y2, conf = sorted(det_boxes, key=lambda x: x[4], reverse=True)[0]

        # Crop
        crop = img[y1:y2, x1:x2]

        # Save output
        cv2.imwrite(output_path, crop)
        logger.info(f"Table detected and cropped: {Path(image_path).name} -> {Path(output_path).name} (conf={conf:.2f})")

        return crop