"""
Premium PNG image generator for Crush Proposal Bot.
Generates a romantic scrapbook-style congratulations image using Pillow.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

# Ensure generated directory exists
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)


def get_font(size: int, bold: bool = False):
    """Get a font, falling back to default if custom fonts aren't available."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]

    if bold:
        bold_paths = [p for p in font_paths if "Bold" in p]
        for path in bold_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)

    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def draw_rounded_rect(draw, coords, radius, fill, outline=None, width=1):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = coords
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def draw_heart(draw, center_x, center_y, size, fill):
    """Draw a simple heart shape."""
    s = size
    points = []
    import math
    for t_val in range(0, 360):
        t = math.radians(t_val)
        x = s * 16 * (math.sin(t) ** 3)
        y = -s * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        points.append((center_x + x / 16, center_y + y / 16))
    if len(points) > 2:
        draw.polygon(points, fill=fill)


def generate_yes_image(crush_name: str, creator_name: str, date: str, time: str) -> BytesIO:
    """
    Generate a premium congratulations image when crush says YES.
    Returns a BytesIO object containing the PNG image.
    """
    # Image dimensions
    width, height = 800, 1000

    # Create base image with warm paper texture color
    img = Image.new("RGB", (width, height), (255, 248, 240))
    draw = ImageDraw.Draw(img)

    # Draw paper texture effect (subtle noise pattern)
    import random
    random.seed(42)  # Consistent pattern
    for _ in range(3000):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        shade = random.randint(240, 255)
        draw.point((x, y), fill=(shade, shade - 8, shade - 16))

    # Draw soft border
    draw_rounded_rect(draw, (20, 20, width - 20, height - 20), 30,
                      fill=None, outline=(255, 182, 193), width=3)
    draw_rounded_rect(draw, (30, 30, width - 30, height - 30), 25,
                      fill=None, outline=(255, 105, 135), width=2)

    # Draw decorative hearts
    heart_positions = [
        (80, 80, 2, (255, 105, 135)),
        (720, 80, 1.5, (255, 182, 193)),
        (100, 900, 1.8, (255, 150, 170)),
        (700, 880, 2.2, (255, 105, 135)),
        (650, 200, 1.2, (255, 200, 210)),
        (150, 200, 1.0, (255, 180, 190)),
    ]
    for hx, hy, hs, hc in heart_positions:
        draw_heart(draw, hx, hy, hs, hc)

    # Draw envelope shape at top
    env_y = 100
    draw.polygon([(350, env_y), (450, env_y), (470, env_y + 50),
                  (400, env_y + 80), (330, env_y + 50)],
                 fill=(255, 228, 225), outline=(255, 150, 170))
    # Heart on envelope
    draw_heart(draw, 400, env_y + 40, 1.5, (255, 80, 100))

    # Title section
    title_font = get_font(42, bold=True)
    subtitle_font = get_font(28, bold=True)
    body_font = get_font(22)
    emoji_font = get_font(36)

    # Main celebration text
    title_text = "SHE SAID YES"
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) / 2, 220), title_text, fill=(220, 20, 60), font=title_font)

    # Heart emojis around title
    draw.text(((width - tw) / 2 - 50, 218), "🎉", font=emoji_font)
    draw.text(((width + tw) / 2 + 10, 218), "❤️", font=emoji_font)

    # Decorative line
    line_y = 290
    draw.line([(150, line_y), (650, line_y)], fill=(255, 182, 193), width=2)

    # Draw glassmorphism-style card background
    card_y = 320
    card_height = 450
    # Semi-transparent card effect
    card_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)
    card_draw.rounded_rectangle(
        (80, card_y, width - 80, card_y + card_height),
        radius=20,
        fill=(255, 255, 255, 200),
        outline=(255, 182, 193, 255),
        width=2
    )
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, card_overlay)
    draw = ImageDraw.Draw(img)

    # Content inside card
    y_offset = card_y + 40

    # Crush name
    crush_label = f"💕 Crush Name:"
    draw.text((120, y_offset), crush_label, fill=(150, 50, 80), font=body_font)
    y_offset += 35
    draw.text((140, y_offset), crush_name, fill=(220, 20, 60), font=subtitle_font)
    y_offset += 55

    # Creator name
    creator_label = f"👤 Created By:"
    draw.text((120, y_offset), creator_label, fill=(150, 50, 80), font=body_font)
    y_offset += 35
    draw.text((140, y_offset), creator_name, fill=(100, 60, 80), font=subtitle_font)
    y_offset += 55

    # Date
    date_label = f"📅 Date:"
    draw.text((120, y_offset), date_label, fill=(150, 50, 80), font=body_font)
    y_offset += 35
    draw.text((140, y_offset), date, fill=(100, 60, 80), font=body_font)
    y_offset += 45

    # Time
    time_label = f"⏰ Time:"
    draw.text((120, y_offset), time_label, fill=(150, 50, 80), font=body_font)
    y_offset += 35
    draw.text((140, y_offset), time, fill=(100, 60, 80), font=body_font)
    y_offset += 55

    # Congratulations message
    congrats_font = get_font(20)
    draw.text((120, y_offset), "🥰 Congratulations!", fill=(220, 20, 60), font=subtitle_font)
    y_offset += 40
    draw.text((120, y_offset), "Your crush accepted your proposal ❤️",
              fill=(150, 80, 100), font=congrats_font)

    # Bottom decoration
    bottom_y = height - 80
    footer_font = get_font(16)
    footer_text = "Made with 💕 Crush Proposal Bot"
    bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    fw = bbox[2] - bbox[0]
    draw.text(((width - fw) / 2, bottom_y), footer_text, fill=(180, 130, 150), font=footer_font)

    # Draw more decorative hearts at bottom
    for i in range(5):
        hx = 200 + i * 100
        draw_heart(draw, hx, bottom_y - 30, 0.8, (255, 182, 193))

    # Convert to RGB for PNG save
    img = img.convert("RGB")

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format="PNG", quality=95)
    buffer.seek(0)

    return buffer


def save_yes_image(crush_name: str, creator_name: str, date: str, time: str) -> str:
    """Generate and save the image to disk. Returns the file path."""
    buffer = generate_yes_image(crush_name, creator_name, date, time)
    filename = f"yes_{crush_name.replace(' ', '_')}_{date}.png"
    filepath = os.path.join(GENERATED_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(buffer.read())
    return filepath
