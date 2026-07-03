"""
ProduGen - Image Generator Module
Uses Replicate API (FLUX Schnell) to generate professional product images.
"""

import os
import uuid
import requests
import replicate
from backend.config import Config
from backend.prompts import build_image_prompt, IMAGE_VARIATIONS


class ImageGenerator:
    """
    Generates professional product images using the Replicate API.
    Uses FLUX Schnell model for fast, affordable image generation.
    """

    # FLUX Schnell model on Replicate — fast and cheap (~$0.003/image)
    MODEL = "black-forest-labs/flux-schnell"

    def __init__(self):
        """Initialize the Replicate client."""
        if not Config.REPLICATE_API_TOKEN or Config.REPLICATE_API_TOKEN == "your_replicate_api_token_here":
            raise ValueError(
                "Replicate API token not configured. "
                "Get your token at https://replicate.com/account/api-tokens "
                "and add it to your .env file."
            )

        os.environ["REPLICATE_API_TOKEN"] = Config.REPLICATE_API_TOKEN
        self.client = replicate.Client(api_token=Config.REPLICATE_API_TOKEN)

    def generate_images(
        self,
        brief: dict,
        num_images: int = 1,
        platform: str = "instagram_post",
        session_id: str = None,
    ) -> list[dict]:
        """
        Generate product images based on the questionnaire brief.

        Args:
            brief: The generation brief dict from the AI questionnaire
            num_images: Number of images to generate (1, 3, or 5)
            platform: Target platform for dimensions
            session_id: Optional session ID for organizing outputs

        Returns:
            List of dicts with image paths and metadata.
        """
        session_id = session_id or str(uuid.uuid4())[:8]
        output_dir = os.path.join(Config.OUTPUT_DIR, session_id)
        os.makedirs(output_dir, exist_ok=True)

        # Select which variations to use based on num_images
        variation_keys = list(IMAGE_VARIATIONS.keys())
        selected_variations = variation_keys[:num_images]

        results = []
        for i, variation in enumerate(selected_variations):
            print(f"  🎨 Generating image {i + 1}/{num_images} ({variation})...")

            # Build the prompt for this variation
            prompt = build_image_prompt(brief, variation=variation, platform=platform)

            try:
                # Get platform dimensions
                width, height = Config.PLATFORM_SIZES.get(platform, (1024, 1024))

                # Call Replicate API
                output = self.client.run(
                    self.MODEL,
                    input={
                        "prompt": prompt,
                        "num_outputs": 1,
                        "aspect_ratio": self._get_aspect_ratio(width, height),
                        "output_format": "png",
                        "output_quality": 90,
                    },
                )

                # Download the generated image
                if output:
                    image_url = output[0] if isinstance(output, list) else str(output)

                    # Handle FileOutput objects from replicate
                    image_url = str(image_url)

                    filename = f"product_{variation}_{i + 1}.png"
                    filepath = os.path.join(output_dir, filename)

                    # Download and save
                    self._download_image(image_url, filepath)

                    results.append({
                        "path": filepath,
                        "filename": filename,
                        "variation": variation,
                        "variation_description": IMAGE_VARIATIONS[variation]["description"],
                        "prompt_used": prompt,
                        "platform": platform,
                        "session_id": session_id,
                    })
                    print(f"  ✅ Image {i + 1} saved: {filename}")

            except Exception as e:
                print(f"  ❌ Error generating image {i + 1}: {e}")
                results.append({
                    "path": None,
                    "filename": None,
                    "variation": variation,
                    "error": str(e),
                    "session_id": session_id,
                })

        return results

    def _get_aspect_ratio(self, width: int, height: int) -> str:
        """
        Convert pixel dimensions to FLUX aspect ratio string.

        Args:
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Aspect ratio string (e.g., "1:1", "16:9")
        """
        ratio = width / height

        # Map to supported FLUX aspect ratios
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16 / 9) < 0.1:
            return "16:9"
        elif abs(ratio - 9 / 16) < 0.1:
            return "9:16"
        elif abs(ratio - 4 / 3) < 0.1:
            return "4:3"
        elif abs(ratio - 3 / 4) < 0.1:
            return "3:4"
        elif ratio > 1:
            return "16:9"
        else:
            return "9:16"

    def _download_image(self, url: str, filepath: str):
        """
        Download an image from a URL and save it locally.

        Args:
            url: The image URL to download
            filepath: Local path to save the image
        """
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


# =============================================================================
# Standalone test
# =============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("🎨 ProduGen Image Generator - Test Mode")
    print("=" * 50)

    # Test with a sample brief
    sample_brief = {
        "status": "complete",
        "product_name": "Handmade Ceramic Mug",
        "product_category": "Kitchenware",
        "product_description": "A beautifully handcrafted ceramic coffee mug with a speckled glaze finish",
        "key_features": ["Handmade", "Ceramic", "Speckled glaze", "12oz capacity"],
        "brand_name": "Clay & Co",
        "target_audience": "Coffee lovers, home decor enthusiasts",
        "style_mood": "Warm, artisanal, cozy",
        "color_preferences": ["Earth tones", "Warm brown", "Cream"],
        "background_preference": "Natural wood surface with soft morning light",
        "platforms": ["instagram_post"],
        "additional_notes": "Show the mug in a cozy setting",
    }

    try:
        generator = ImageGenerator()
        print("\n📸 Generating 1 test image...")
        results = generator.generate_images(sample_brief, num_images=1)

        for result in results:
            if result.get("path"):
                print(f"\n✅ Success! Image saved to: {result['path']}")
            else:
                print(f"\n❌ Failed: {result.get('error')}")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
