#!/usr/bin/env python3
"""
Add sample cover images to opportunities for testing
"""

import os
import sys
import django
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Add the project root to the Python path
sys.path.append('/home/mirzosharif/MVP/chinor_id_new/opportuni_backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

from django.core.files.base import ContentFile
from apps.opportunities.models import Opportunity

def create_sample_cover_image(title, org_name, opportunity_type):
    """Create a sample cover image for an opportunity"""
    # Create image
    width, height = 800, 400
    
    # Color scheme based on opportunity type
    color_schemes = {
        'internship': ('#2563eb', '#3b82f6'),  # Blue
        'volunteer': ('#dc2626', '#ef4444'),   # Red
        'scholarship': ('#059669', '#10b981'), # Green
        'competition': ('#7c2d12', '#ea580c'), # Orange
        'job': ('#4338ca', '#6366f1'),         # Indigo
        'workshop': ('#9333ea', '#a855f7'),    # Purple
        'conference': ('#0891b2', '#06b6d4'),  # Cyan
    }
    
    primary_color, secondary_color = color_schemes.get(opportunity_type, ('#2563eb', '#3b82f6'))
    
    # Create image with gradient background
    image = Image.new('RGB', (width, height), primary_color)
    draw = ImageDraw.Draw(image)
    
    # Create gradient effect (simple version)
    for i in range(height):
        alpha = i / height
        # Simple gradient by varying the color intensity
        r = int(37 + (59 - 37) * alpha)  # From #2563eb to #3b82f6 (blue example)
        g = int(99 + (130 - 99) * alpha)
        b = int(235 + (246 - 235) * alpha)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Add overlay for better text readability
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
    image = Image.alpha_composite(image.convert('RGBA'), overlay)
    
    # Try to use a better font, fallback to default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        org_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        type_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        org_font = ImageFont.load_default()
        type_font = ImageFont.load_default()
    
    # Add text
    y_pos = height // 2 - 60
    
    # Title
    title_text = title[:40] + "..." if len(title) > 40 else title
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, y_pos), title_text, fill='white', font=title_font)
    
    # Organization
    org_bbox = draw.textbbox((0, 0), org_name, font=org_font)
    org_width = org_bbox[2] - org_bbox[0]
    draw.text(((width - org_width) // 2, y_pos + 60), org_name, fill=(255, 255, 255, 230), font=org_font)
    
    # Type badge
    type_text = opportunity_type.upper()
    type_bbox = draw.textbbox((0, 0), type_text, font=type_font)
    type_width = type_bbox[2] - type_bbox[0]
    
    # Badge background
    badge_padding = 20
    badge_x = (width - type_width - badge_padding * 2) // 2
    badge_y = y_pos + 120
    draw.rounded_rectangle([badge_x, badge_y, badge_x + type_width + badge_padding * 2, badge_y + 40], 
                          radius=20, fill=(255, 255, 255, 50))
    
    # Badge text
    draw.text((badge_x + badge_padding, badge_y + 8), type_text, fill='white', font=type_font)
    
    # Convert back to RGB
    image = image.convert('RGB')
    
    # Save to BytesIO
    img_io = BytesIO()
    image.save(img_io, format='JPEG', quality=85)
    img_io.seek(0)
    
    return img_io

def add_cover_images():
    """Add cover images to existing opportunities"""
    print("🖼️  ADDING COVER IMAGES TO OPPORTUNITIES")
    print("=" * 50)
    
    opportunities = Opportunity.objects.all()
    print(f"📋 Found {opportunities.count()} opportunities")
    
    for opportunity in opportunities:
        try:
            if opportunity.cover_image:
                print(f"⏭️  Skipping #{opportunity.id} - already has cover image")
                continue
            
            print(f"🎨 Creating cover image for: #{opportunity.id} - {opportunity.title[:30]}...")
            
            # Create cover image
            img_io = create_sample_cover_image(
                opportunity.title, 
                opportunity.organization.name,
                opportunity.opportunity_type
            )
            
            # Save to opportunity
            filename = f"opportunity_{opportunity.id}_cover.jpg"
            opportunity.cover_image.save(
                filename,
                ContentFile(img_io.getvalue()),
                save=True
            )
            
            print(f"   ✅ Cover image saved: {opportunity.cover_image.url}")
            
        except Exception as e:
            print(f"   ❌ Error creating cover for #{opportunity.id}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Cover images processed!")
    print(f"🌐 You can now test the opportunity details page with cover images")
    print(f"🔗 Visit: http://localhost:8080/opportunity-details.html?id=1")
    print("=" * 50)

if __name__ == "__main__":
    try:
        add_cover_images()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
