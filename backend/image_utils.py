"""
ProduGen - Image Utility Functions
Handles image resizing, format conversion, and thumbnail generation.
"""

import os
from PIL import Image
from backend.config import Config


def resize_for_platform(image_path: str, platform: str, output_dir: str = None) -> str:
    """
    Resize an image to match a specific social media platform's dimensions.

    Args:
        image_path: Path to the source image
        platform: Platform key from Config.PLATFORM_SIZES
                  (instagram_post, instagram_story, facebook_post, website_banner, square)
        output_dir: Directory to save the resized image (defaults to Config.OUTPUT_DIR)

    Returns:
        Path to the resized image file.
    """
    if platform not in Config.PLATFORM_SIZES:
        raise ValueError(
            f"Unknown platform '{platform}'. "
            f"Supported: {list(Config.PLATFORM_SIZES.keys())}"
        )

    target_width, target_height = Config.PLATFORM_SIZES[platform]
    output_dir = output_dir or Config.OUTPUT_DIR

    with Image.open(image_path) as img:
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # Resize using high-quality Lanczos resampling
        # Use thumbnail-style fit (maintains aspect ratio, fits within bounds)
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # Image is wider — fit to width, crop height
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Image is taller — fit to height, crop width
            new_height = target_height
            new_width = int(target_height * img_ratio)

        img_resized = img.resize((new_width, new_height), Image.LANCZOS)

        # Create a canvas of the exact target size and paste centered
        canvas = Image.new("RGB", (target_width, target_height), (255, 255, 255))
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2

        if img_resized.mode == "RGBA":
            canvas.paste(img_resized, (offset_x, offset_y), img_resized)
        else:
            canvas.paste(img_resized, (offset_x, offset_y))

        # Save the resized image
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_{platform}{ext}"
        output_path = os.path.join(output_dir, output_filename)

        canvas.save(output_path, quality=95)
        return output_path


def create_thumbnail(image_path: str, size: tuple = (300, 300), output_dir: str = None) -> str:
    """
    Create a thumbnail of an image.

    Args:
        image_path: Path to the source image
        size: Thumbnail dimensions (width, height)
        output_dir: Directory to save thumbnail

    Returns:
        Path to the thumbnail file.
    """
    output_dir = output_dir or Config.OUTPUT_DIR

    with Image.open(image_path) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        img.thumbnail(size, Image.LANCZOS)

        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_thumb{ext}"
        output_path = os.path.join(output_dir, output_filename)

        img.save(output_path, quality=85)
        return output_path


def get_image_info(image_path: str) -> dict:
    """
    Get basic information about an image file.

    Args:
        image_path: Path to the image

    Returns:
        Dict with width, height, format, mode, and file size.
    """
    with Image.open(image_path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "file_size_kb": round(os.path.getsize(image_path) / 1024, 1),
        }


def validate_upload(image_path: str, max_size_mb: int = 10) -> dict:
    """
    Validate an uploaded image file.

    Args:
        image_path: Path to the uploaded image
        max_size_mb: Maximum allowed file size in MB

    Returns:
        Dict with 'valid' boolean and 'error' message if invalid.
    """
    # Check file exists
    if not os.path.exists(image_path):
        return {"valid": False, "error": "File not found"}

    # Check file size
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return {"valid": False, "error": f"File too large ({file_size_mb:.1f}MB). Max: {max_size_mb}MB"}

    # Check it's a valid image
    try:
        with Image.open(image_path) as img:
            img.verify()
        return {"valid": True, "error": None}
    except Exception:
        return {"valid": False, "error": "Invalid image file"}
