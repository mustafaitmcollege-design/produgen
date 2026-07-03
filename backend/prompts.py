"""
ProduGen - AI Prompt Templates
All system prompts and prompt templates for AI services.
"""


# =============================================================================
# QUESTIONNAIRE SYSTEM PROMPT
# =============================================================================
# This prompt instructs Gemini to act as a product photography consultant.
# It conducts an intelligent interview to gather all details needed for
# generating professional product images.

QUESTIONNAIRE_SYSTEM_PROMPT = """You are ProduGen AI — a professional product photography consultant helping small business owners create stunning product images for social media and websites.

Your job is to conduct a friendly, intelligent interview to understand:
1. The product details (name, category, key features)
2. The business context (brand name, industry, target audience)
3. The visual style preferences (mood, colors, backgrounds)
4. The intended platforms (Instagram, Facebook, website, etc.)

RULES:
- Ask ONE question at a time. Keep questions short and conversational.
- Start by greeting the user and asking about their product.
- After each answer, acknowledge it briefly and ask the next relevant question.
- Adapt your questions based on previous answers (e.g., if they sell jewelry, ask about material/finish).
- After collecting enough information (usually 5-8 questions), summarize everything and confirm with the user.
- When the user confirms, respond with a JSON block wrapped in ```json``` markers containing the generation brief.

The generation brief JSON must have this structure:
```json
{
  "status": "complete",
  "product_name": "...",
  "product_category": "...",
  "product_description": "...",
  "key_features": ["...", "..."],
  "brand_name": "...",
  "target_audience": "...",
  "style_mood": "...",
  "color_preferences": ["...", "..."],
  "background_preference": "...",
  "platforms": ["instagram", "facebook", "website"],
  "additional_notes": "..."
}
```

Remember: You are warm, professional, and encouraging. Small business owners may not know photography jargon — keep it simple and friendly."""


# =============================================================================
# IMAGE GENERATION PROMPT TEMPLATE
# =============================================================================
# This template is filled with data from the questionnaire brief
# and sent to the image generation AI (Replicate / FLUX).

IMAGE_GENERATION_PROMPT = """Professional product photography of {product_name}.

Product: {product_description}
Key features: {key_features}
Style: {style_mood}
Brand colors: {color_preferences}
Background: {background_preference}

Shot specifications:
- High-resolution, commercial-grade product photography
- {lighting_style} lighting
- Clean, sharp focus on the product
- {composition_style} composition
- Professional color grading
- Ready for {platform} marketing use

Quality: Ultra-high detail, 8K quality, professional studio photography, commercial product shot"""


# =============================================================================
# VARIATION PROMPTS
# =============================================================================
# Different styles for generating multiple image variations

IMAGE_VARIATIONS = {
    "studio_clean": {
        "description": "Clean studio shot with neutral background",
        "lighting_style": "Soft, even studio",
        "composition_style": "Centered, minimal",
        "background_extra": "Pure white or light gray seamless background, subtle shadows",
    },
    "lifestyle": {
        "description": "Product in a lifestyle/usage context",
        "lighting_style": "Natural, warm ambient",
        "composition_style": "Environmental, contextual",
        "background_extra": "Realistic lifestyle setting showing the product in use",
    },
    "dramatic": {
        "description": "Bold, eye-catching social media shot",
        "lighting_style": "Dramatic, high-contrast",
        "composition_style": "Dynamic, bold angles",
        "background_extra": "Vibrant gradient or textured background, social media optimized",
    },
    "minimal": {
        "description": "Minimalist, premium presentation",
        "lighting_style": "Soft, directional",
        "composition_style": "Minimalist with negative space",
        "background_extra": "Solid muted color background, elegant simplicity",
    },
    "luxury": {
        "description": "Premium, high-end presentation",
        "lighting_style": "Golden hour, warm and luxurious",
        "composition_style": "Elegant, aspirational",
        "background_extra": "Dark, rich background with subtle textures, premium feel",
    },
}


def build_image_prompt(brief: dict, variation: str = "studio_clean", platform: str = "instagram") -> str:
    """
    Build a complete image generation prompt from the questionnaire brief
    and the selected variation style.
    
    Args:
        brief: The generation brief dict from the AI questionnaire
        variation: One of the keys from IMAGE_VARIATIONS
        platform: Target platform (instagram, facebook, website)
    
    Returns:
        A formatted prompt string ready for the image generation API
    """
    var = IMAGE_VARIATIONS.get(variation, IMAGE_VARIATIONS["studio_clean"])

    prompt = IMAGE_GENERATION_PROMPT.format(
        product_name=brief.get("product_name", "product"),
        product_description=brief.get("product_description", ""),
        key_features=", ".join(brief.get("key_features", [])),
        style_mood=brief.get("style_mood", "professional"),
        color_preferences=", ".join(brief.get("color_preferences", [])),
        background_preference=brief.get("background_preference", var["background_extra"]),
        lighting_style=var["lighting_style"],
        composition_style=var["composition_style"],
        platform=platform,
    )

    return prompt
