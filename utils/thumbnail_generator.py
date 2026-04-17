"""
Advanced Thumbnail Generator for Music Bot
Creates beautiful thumbnails with blurred background, circular cover image, and progress bar
Based on ANNIEMUSIC thumbnail.py
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO
import os
import re
import logging

logger = logging.getLogger(__name__)

PLAY_ICONS_PATH = "/Users/nishkarshkr/Desktop/BOT/play_icons.png"


def change_image_size(max_width, max_height, image):
    """Resize image maintaining aspect ratio"""
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    new_image = image.resize((new_width, new_height))
    return new_image


def truncate_text(text):
    """Truncate text to fit in two lines of 30 chars each"""
    words = text.split(" ")
    line1 = ""
    line2 = ""
    
    for word in words:
        if len(line1) + len(word) < 30:
            line1 += " " + word
        elif len(line2) + len(word) < 30:
            line2 += " " + word
    
    return [line1.strip(), line2.strip()]


def crop_center_circle(img, output_size, border, crop_scale=1.5):
    """Crop center of image in a circular shape"""
    half_width = img.size[0] / 2
    half_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    
    img = img.crop((
        half_width - larger_size/2,
        half_height - larger_size/2,
        half_width + larger_size/2,
        half_height + larger_size/2
    ))
    
    img = img.resize((output_size - 2*border, output_size - 2*border))
    
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    
    final_img.paste(img, (border, border), mask_main)
    
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    return result


def create_thumbnail(
    title="Unknown Title",
    artist="Unknown Artist",
    views="0 views",
    duration="0:00",
    cover_url=None,
    video_id=None,
    output="thumb.png"
):
    """
    Create a simple thumbnail - just the original song thumbnail image
    
    Args:
        title: Song title
        artist: Artist name
        views: View count
        duration: Song duration
        cover_url: YouTube thumbnail URL
        video_id: YouTube video ID
        output: Output file path
        
    Returns:
        Path to generated thumbnail
    """
    try:
        # Simply download and save the original thumbnail
        if cover_url:
            response = requests.get(cover_url, timeout=10)
            
            # Save the original image
            os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
            
            with open(output, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Thumbnail saved: {output}")
            return output
        else:
            logger.warning("No cover URL provided for thumbnail")
            return None

    except Exception as e:
        logger.error(f"❌ Failed to create thumbnail: {e}")
        return None
