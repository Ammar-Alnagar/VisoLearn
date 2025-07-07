import cv2
import numpy as np
import os
from pathlib import Path
from PIL import Image

class AutomatedCollageSplitter:
    def __init__(self):
        # Parameters for contour detection and filtering from reference
        self.min_segment_area_ratio = 0.01
        self.max_segment_area_ratio = 0.95
        self.min_aspect_ratio = 0.2
        self.max_aspect_ratio = 5.0
        self.min_solidity = 0.9
        self.nms_threshold = 0.3

        # Upscaler initialization
        self.upscaler = None
        self._initialize_upscaler()

    def _initialize_upscaler(self):
        if self.upscaler is not None:
            return
        try:
            model_name = 'fsrcnn'
            
            # Construct a robust path to the model file relative to this script's location
            script_dir = Path(__file__).parent.resolve()
            model_path = script_dir / 'models' / 'weights' / 'FSRCNN-small_x4.pb'

            scale = 4
            if not model_path.is_file():
                raise FileNotFoundError(f"Model file not found at {model_path}")

            self.upscaler = cv2.dnn_superres.DnnSuperResImpl_create()
            self.upscaler.readModel(str(model_path))
            self.upscaler.setModel(model_name, scale)
            print(f"✓ OpenCV DNN upscaler model loaded: {model_name} with scale x{scale}")
        except Exception as e:
            print(f"⚠ Could not initialize OpenCV DNN upscaler: {e}. Proceeding without upscaling.")
            self.upscaler = None

    def _upscale_image(self, image_array):
        if not self.upscaler:
            print("❌ Upscaling skipped because the upscaler is not available.")
            return image_array
        try:
            return self.upscaler.upsample(image_array)
        except Exception as e:
            print(f"❌ Error during image upscaling: {e}")
            return image_array

    def preprocess_for_contours(self, image):
        """Pre-process the image to make panel borders stand out for contour detection."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            21, # Block size, must be odd
            8   # Constant to subtract from mean, tuned for better border detection
        )

        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

        return closed

    def find_panel_contours(self, processed_image, original_shape):
        """Find and filter contours that are likely to be comic panels."""
        contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        height, width = original_shape[:2]
        total_area = height * width
        min_area = total_area * self.min_segment_area_ratio
        max_area = total_area * self.max_segment_area_ratio

        potential_panels = []
        for contour in contours:
            area = cv2.contourArea(contour)

            if not (min_area < area < max_area):
                continue

            x, y, w, h = cv2.boundingRect(contour)

            if h == 0: continue
            aspect_ratio = w / h
            if not (self.min_aspect_ratio < aspect_ratio < self.max_aspect_ratio):
                continue

            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            if hull_area == 0: continue
            solidity = float(area) / hull_area
            if solidity < self.min_solidity:
                continue

            potential_panels.append([x, y, x + w, y + h, area])

        return np.array(potential_panels)

    def apply_non_maximum_suppression(self, boxes):
        """Apply NMS to merge overlapping bounding boxes."""
        if len(boxes) == 0:
            return []

        boxes = boxes[boxes[:, 4].argsort()[::-1]]

        picked_boxes = []
        while len(boxes) > 0:
            best_box = boxes[0]
            picked_boxes.append(best_box)

            remaining_boxes = boxes[1:]

            x1 = np.maximum(best_box[0], remaining_boxes[:, 0])
            y1 = np.maximum(best_box[1], remaining_boxes[:, 1])
            x2 = np.minimum(best_box[2], remaining_boxes[:, 2])
            y2 = np.minimum(best_box[3], remaining_boxes[:, 3])

            inter_w = np.maximum(0, x2 - x1)
            inter_h = np.maximum(0, y2 - y1)
            intersection_area = inter_w * inter_h

            best_box_area = (best_box[2] - best_box[0]) * (best_box[3] - best_box[1])
            remaining_boxes_area = (remaining_boxes[:, 2] - remaining_boxes[:, 0]) * (remaining_boxes[:, 3] - remaining_boxes[:, 1])

            union_area = best_box_area + remaining_boxes_area - intersection_area
            iou = intersection_area / union_area

            boxes = remaining_boxes[iou < self.nms_threshold]

        return np.array(picked_boxes)

    def split_collage(self, image_path, output_dir=None, debug=False):
        """Main function to automatically split collage using contour detection and NMS."""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image from {image_path}")

        print(f"Processing image: {image_path}")
        print(f"Image dimensions: {img.shape[1]}x{img.shape[0]}")

        processed_image = self.preprocess_for_contours(img)
        print("✓ Preprocessed image for contour detection")

        potential_panels = self.find_panel_contours(processed_image, img.shape)
        print(f"✓ Found {len(potential_panels)} potential panel contours")

        final_panels = self.apply_non_maximum_suppression(potential_panels)
        print(f"✓ Refined to {len(final_panels)} panels after Non-Maximum Suppression")

        if len(final_panels) > 0:
            img_height = img.shape[0]
            panel_heights = [box[3] - box[1] for box in final_panels]
            if panel_heights:
                max_panel_height = max(panel_heights)

                if max_panel_height > 0:
                    bottom_margin = 10
                    height_threshold_ratio = 0.8

                    truly_final_panels = []
                    for box in final_panels:
                        h = box[3] - box[1]
                        y2 = box[3]

                        is_at_bottom = y2 >= (img_height - bottom_margin)
                        is_too_short = h < (max_panel_height * height_threshold_ratio)

                        if is_at_bottom and is_too_short:
                            print(f"Skipping potentially incomplete panel at the bottom (h={h} vs max_h={max_panel_height})")
                            continue
                        truly_final_panels.append(box)

                    final_panels = truly_final_panels

        if len(final_panels) < 4:
            print("⚠ Contour detection found too few panels. Creating fallback 2x2 grid...")
            h, w = img.shape[:2]
            final_panels = np.array([
                [0, 0, w//2, h//2, 0],
                [w//2, 0, w, h//2, 0],
                [0, h//2, w//2, h, 0],
                [w//2, h//2, w, h, 0]
            ])

        final_panels = sorted(final_panels, key=lambda b: (b[1], b[0]))

        if output_dir is None:
            output_dir = Path(image_path).parent / f"{Path(image_path).stem}_segments"
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        saved_segments_info = []
        for i, box in enumerate(final_panels):
            x1, y1, x2, y2, _ = map(int, box)

            padding = 3
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img.shape[1], x2 + padding)
            y2 = min(img.shape[0], y2 + padding)

            segment = img[y1:y2, x1:x2]
            original_dims = (segment.shape[1], segment.shape[0])

            upscaled_segment_np = self._upscale_image(segment)

            final_image = Image.fromarray(cv2.cvtColor(upscaled_segment_np, cv2.COLOR_BGR2RGB))

            final_dims = (final_image.width, final_image.height)
            output_path = output_dir / f"segment_{i+1:02d}.png"
            final_image.save(str(output_path))

            caption = (
                f"Panel {i+1}<br>"
                f"Original: {original_dims[0]}x{original_dims[1]}<br>"
                f"Upscaled: {final_dims[0]}x{final_dims[1]}"
            )

            saved_segments_info.append({
                "path": str(output_path),
                "caption": caption
            })
            print(f"  Saved segment {i+1}: {final_dims[0]}x{final_dims[1]} pixels to {output_path}")

        if debug:
            debug_potential_panels = self.find_panel_contours(processed_image, img.shape)
            self.create_debug_images(img, processed_image, debug_potential_panels, final_panels, output_dir)

        print(f"\n🎉 Successfully split collage into {len(saved_segments_info)} segments!")
        print(f"📁 Segments saved in: {output_dir}")
        return saved_segments_info

    def create_debug_images(self, original, processed, potential_boxes, final_boxes, output_dir):
        """Create debug images showing the processing steps."""
        cv2.imwrite(str(output_dir / "debug_01_binary_closed.png"), processed)

        potential_img = original.copy()
        if len(potential_boxes) > 0:
            for x1, y1, x2, y2, _ in potential_boxes:
                cv2.rectangle(potential_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 255), 2)
        cv2.imwrite(str(output_dir / "debug_02_potential_boxes.png"), potential_img)

        final_img = original.copy()
        if len(final_boxes) > 0:
            for x1, y1, x2, y2, _ in final_boxes:
                cv2.rectangle(final_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
        cv2.imwrite(str(output_dir / "debug_03_final_panels.png"), final_img)

        print("🔍 Debug images saved:")
        print("  - debug_01_binary_closed.png (preprocessed)")
        print("  - debug_02_potential_boxes.png (before NMS)")
        print("  - debug_03_final_panels.png (after NMS)")

def main():
    """Example usage"""
    splitter = AutomatedCollageSplitter()

    image_path = "path/to/your/comic_image.png"

    try:
        if not Path(image_path).exists():
             print(f"❌ Image file not found: {image_path}")
             print("Please update the image_path variable with the correct path to your collage image.")
             return

        segments = splitter.split_collage(
            image_path=image_path,
            debug=True
        )

        print(f"\n📊 Processing complete!")
        print(f"Generated {len(segments)} separate images from the collage")

    except Exception as e:
        print(f"❌ Error processing image: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
