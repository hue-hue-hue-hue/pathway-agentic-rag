import logging
from pathlib import Path
import time
from docprocessor.processor import DocumentProcessor

_log = logging.getLogger(__name__)


def main():
    input_paths = [
        Path("input_files/adaRAG.pdf"),
        # Add other paths as needed
    ]

    processor = DocumentProcessor(
        output_dir="output_files",
        image_resolution_scale=2.0,
        output_formats=["md", "json", "yaml", "txt"],
    )

    for input_path in input_paths:
        start_time = time.time()
        try:
            output_dir = processor.process_document(input_path)

            processing_time = time.time() - start_time
            print(
                f"Document {input_path.name} processed in {processing_time:.2f} seconds."
                f"\nOutput saved to: {output_dir}"
            )

        except Exception as e:
            _log.error(f"Error processing {input_path}: {str(e)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
