import logging
import tempfile
import os
from pathlib import Path
from typing import Union, List, Optional
import requests
from urllib.parse import urlparse

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.datamodel.base_models import InputFormat, DocumentStream
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import ImageRefMode

_log = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(
        self,
        output_dir: Union[str, Path] = "output_files",
        image_resolution_scale: float = 2.0,
        max_pages: Optional[int] = -1,
        max_file_size: Optional[int] = -1,
    ):
        self.output_dir = Path(output_dir)
        self.image_resolution_scale = image_resolution_scale
        self.max_pages = max_pages
        self.max_file_size = max_file_size
        self._initialize_converter()

    def _initialize_converter(self):
        """Initialize the document converter with all supported formats"""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = self.image_resolution_scale
        pipeline_options.generate_page_images = True
        pipeline_options.generate_table_images = True
        pipeline_options.generate_picture_images = True

        self.converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
                InputFormat.ASCIIDOC,
                InputFormat.MD,
            ],
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=StandardPdfPipeline,
                    pipeline_options=pipeline_options,
                ),
                InputFormat.DOCX: WordFormatOption(pipeline_cls=SimplePipeline),
            },
        )

    def _download_file(self, url: str) -> Path:
        """Download a file from URL and return its temporary path"""
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Create temp file with correct extension
        parsed_url = urlparse(url)
        extension = os.path.splitext(parsed_url.path)[1]

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        temp_file.close()

        return Path(temp_file.name)

    def process_document(self, source: Union[str, Path]) -> Path:
        """Process a document from file path or URL"""
        temp_file = None
        try:
            if isinstance(source, str) and (
                source.startswith("http://") or source.startswith("https://")
            ):
                source = self._download_file(source)
                temp_file = source

            conv_result = self.converter.convert(
                source,
                max_num_pages=self.max_pages if self.max_pages is not None else -1,
                max_file_size=(
                    self.max_file_size if self.max_file_size is not None else -1
                ),
            )

            if source.suffix.lower() == ".pdf":
                output_dir = self._process_pdf(conv_result, source)
            else:
                output_dir = self._process_other(conv_result, source)

            return output_dir

        finally:
            if temp_file and temp_file.exists():
                temp_file.unlink()

    def _process_pdf(self, conv_result, input_path: Path) -> Path:
        """Process PDF document with image extraction"""
        pdf_dir = self.output_dir / input_path.stem
        pdf_dir.mkdir(parents=True, exist_ok=True)

        images_dir = pdf_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Save page images and other content
        self._save_images(conv_result, images_dir)
        self._save_outputs(conv_result, pdf_dir)

        return pdf_dir

    def _process_other(self, conv_result, input_path: Path) -> Path:
        """Process non-PDF documents"""
        out_path = self.output_dir
        out_path.mkdir(parents=True, exist_ok=True)

        for subdir in ["markdown", "json", "yaml", "document_tokens"]:
            (out_path / subdir).mkdir(exist_ok=True)

        self._save_outputs(conv_result, out_path, input_path.stem)
        return out_path

    def _save_images(self, conv_result, images_dir: Path):
        """Save all images from the document"""
        for page_no, page in conv_result.document.pages.items():
            page_image_path = images_dir / f"page_{page.page_no}.png"
            page.image.pil_image.save(page_image_path, format="PNG")

    def _save_outputs(self, conv_result, output_dir: Path, filename_prefix: str = None):
        """Save document in various formats"""
        if filename_prefix is None:
            filename_prefix = conv_result.input.file.stem

        # Save markdown with embedded images
        content_md = conv_result.document.export_to_markdown(
            image_mode=ImageRefMode.EMBEDDED
        )
        (output_dir / f"{filename_prefix}_with_images.md").write_text(content_md)

        # Save other formats
        formats = {
            "json": lambda: conv_result.document.export_to_dict(),
            "yaml": lambda: conv_result.document.export_to_dict(),
            "txt": lambda: conv_result.document.export_to_document_tokens(),
        }

        for ext, export_func in formats.items():
            output_path = output_dir / f"{filename_prefix}.{ext}"
            with output_path.open("w") as fp:
                fp.write(str(export_func()))
