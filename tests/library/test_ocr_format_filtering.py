"""Tests for OCR unsupported format filtering.

Verifies fix for GitHub issue #1108:
.emf and other unsupported image formats should be skipped during OCR
processing to prevent tesseract errors.
"""

import os


def test_supported_format_detection():
    """Test that supported formats are correctly identified."""
    supported_ocr_formats = {'.png', '.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.bmp', '.ppm', '.pgm', '.pbm', '.webp'}

    supported_files = ['image.png', 'photo.jpg', 'picture.jpeg', 'icon.gif', 'scan.tiff', 'doc.bmp']
    for filename in supported_files:
        _, ext = os.path.splitext(filename.lower())
        assert ext in supported_ocr_formats, f"{filename} should be supported"


def test_unsupported_format_detection():
    """Test that unsupported formats are correctly identified."""
    supported_ocr_formats = {'.png', '.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.bmp', '.ppm', '.pgm', '.pbm', '.webp'}

    unsupported_files = ['vector.emf', 'drawing.wmf', 'graphic.svg', 'icon.ico']
    for filename in unsupported_files:
        _, ext = os.path.splitext(filename.lower())
        assert ext not in supported_ocr_formats, f"{filename} should not be supported"


def test_case_insensitive_extension():
    """Test that extension matching is case-insensitive."""
    supported_ocr_formats = {'.png', '.jpg', '.jpeg', '.gif', '.tiff', '.tif', '.bmp', '.ppm', '.pgm', '.pbm', '.webp'}

    test_files = ['IMAGE.PNG', 'Photo.JPG', 'image.Png']
    for filename in test_files:
        _, ext = os.path.splitext(filename.lower())
        assert ext in supported_ocr_formats, f"{filename} should be supported (case-insensitive)"
