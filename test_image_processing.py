import os
from pathlib import Path
from new_image_splitting import AutomatedCollageSplitter

def run_test():
    """
    Initializes the splitter and runs the image processing test.
    """
    print("--- Starting Image Splitting and Upscaling Test ---")
    
    # Initialize the splitter
    try:
        splitter = AutomatedCollageSplitter()
        print("✓ AutomatedCollageSplitter initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize AutomatedCollageSplitter: {e}")
        return

    # Define the input image path
    image_path = Path("Story Sessions/The_Pebble_s_Journey_20250624_190429/story_comic.png")

    # Check if the image exists
    if not image_path.exists():
        print(f"❌ Test image not found at: {image_path.resolve()}")
        print("Please ensure 'image.jpg' is in the root directory of the project.")
        return
    
    print(f"Found test image: {image_path.resolve()}")

    # Define the output directory
    output_dir = Path("test_output_segments")
    print(f"Output will be saved to: {output_dir.resolve()}")

    # Run the main splitting and upscaling logic
    try:
        print("\nProcessing collage...")
        segments_info = splitter.split_collage(
            image_path=str(image_path),
            output_dir=str(output_dir),
            debug=True  # Enable debug images to verify each step
        )

        if segments_info:
            print("\n--- Test Summary ---")
            print(f"✅ Successfully processed and split the image into {len(segments_info)} segments.")
            for i, info in enumerate(segments_info):
                print(f"  - Segment {i+1}: {info['path']}")
            print(f"Debug images and segments saved in '{output_dir.resolve()}'")
            print("\n--- Test PASSED ---")
        else:
            print("\n--- Test FAILED ---")
            print("Image processing completed but returned no segments.")
            
    except Exception as e:
        print(f"\n--- Test FAILED ---")
        print(f"An error occurred during the splitting process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test() 