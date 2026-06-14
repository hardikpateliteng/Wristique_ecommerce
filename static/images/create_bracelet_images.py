"""
Generate sample bracelet images for the Wristique store
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_bracelet_image(filename, color1, color2, style_name, description):
    """Create a bracelet image with specified colors"""
    width, height = 400, 400
    image = Image.new('RGB', (width, height), '#F8F6F1')
    draw = ImageDraw.Draw(image)
    
    # Draw circular bracelet
    center_x, center_y = width // 2, height // 2
    radius = 80
    
    # Draw beads in a circle
    beads = 12
    for i in range(beads):
        angle = (i / beads) * 360
        rad = angle * 3.14159 / 180
        x = center_x + radius * 1.2 * os.math.cos(rad)
        y = center_y + radius * 1.2 * os.math.sin(rad)
        
        # Alternate colors for bead design
        bead_color = color1 if i % 2 == 0 else color2
        draw.ellipse([x - 15, y - 15, x + 15, y + 15], fill=bead_color, outline='#333', width=2)
        
        # Add shine effect
        draw.ellipse([x - 10, y - 12, x - 3, y - 5], fill='white', width=0)
    
    # Draw center circle
    draw.ellipse([center_x - 50, center_y - 50, center_x + 50, center_y + 50], 
                 fill='none', outline='#D4AF37', width=3)
    
    # Add text
    try:
        # Try to use a nice font, fallback to default
        font = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw style name
    draw.text((width // 2, height - 80), style_name, fill='#0F3460', font=font, anchor='mm')
    draw.text((width // 2, height - 45), description, fill='#666', font=font_small, anchor='mm')
    
    # Save image
    image_path = os.path.join(os.path.dirname(__file__), filename)
    image.save(image_path)
    print(f"Created: {filename}")

# Create bracelet images
bracelet_designs = [
    ('emerald_elegance.png', '#2D5016', '#D4AF37', 'Emerald Elegance', 'Premium Green & Gold'),
    ('sapphire_serenity.png', '#0F3460', '#E8D5B7', 'Sapphire Serenity', 'Royal Blue Collection'),
    ('rose_radiance.png', '#C1666B', '#FFB6C1', 'Rose Radiance', 'Romantic Pink Beads'),
    ('ocean_waves.png', '#4ECDC4', '#0F3460', 'Ocean Waves', 'Teal & Navy Mix'),
    ('sunset_glow.png', '#FF6B6B', '#FFD93D', 'Sunset Glow', 'Orange & Gold'),
    ('midnight_sparkle.png', '#1A1A1A', '#D4AF37', 'Midnight Sparkle', 'Black & Gold'),
    ('crystal_clear.png', '#E8D5B7', '#D4AF37', 'Crystal Clear', 'Neutral Beige'),
    ('nature_bloom.png', '#2D5016', '#FF6B6B', 'Nature Bloom', 'Green & Red'),
]

# Create images folder if it doesn't exist
os.makedirs(os.path.dirname(__file__), exist_ok=True)

for design in bracelet_designs:
    create_bracelet_image(*design)

print("All bracelet images created successfully!")
