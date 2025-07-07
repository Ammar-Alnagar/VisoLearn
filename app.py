import os
from google.generativeai import configure
from ui.interface import create_interface
import config

def main():
    # Configure Google API
    configure(api_key=config.GOOGLE_API_KEY)

    # Create and launch the Gradio interface
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)

if __name__ == "__main__":
    main()
