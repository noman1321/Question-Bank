"""
Image Processor Module - Fixed Version
Handles image extraction, processing, and AI analysis
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import base64
import io
from PIL import Image
import fitz  # PyMuPDF for better PDF image extraction
import docx
from urllib.parse import urljoin
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

# Load environment variables


def get_openai_api_key():
    """
    Returns the OpenAI API key.
    Priority: 1) .env file, 2) Streamlit secrets
    """
    # Try environment variable first (from .env)
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key:
        return env_key
    
    # Try Streamlit secrets (for cloud deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Return None if neither source has the key
        return None
class ImageProcessor:
    def __init__(self):
        api_key = get_openai_api_key()
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            st.warning("⚠️ OpenAI API key not found - image analysis will be limited")
    
    def encode_image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image if too large (max 1024px on longest side)
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            img_data = buffer.getvalue()
            return base64.b64encode(img_data).decode('utf-8')
        except Exception as e:
            st.error(f"Error encoding image: {str(e)}")
            return None
    
    def extract_images_from_pdf(self, pdf_file):
        """Extract images from PDF using PyMuPDF"""
        images = []
        try:
            pdf_file.seek(0)
            pdf_data = pdf_file.read()
            
            # Use PyMuPDF for better image extraction
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Convert to PIL Image
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("ppm")
                            pil_image = Image.open(io.BytesIO(img_data))
                            
                            # Filter out very small images (likely decorative)
                            if pil_image.width > 100 and pil_image.height > 100:
                                images.append({
                                    'image': pil_image,
                                    'source': f"PDF Page {page_num + 1}, Image {img_index + 1}",
                                    'base64': self.encode_image_to_base64(pil_image)
                                })
                        
                        pix = None
                    except Exception as e:
                        st.warning(f"Could not extract image from page {page_num + 1}: {str(e)}")
                        continue
            
            doc.close()
            st.success(f"📸 Extracted {len(images)} images from PDF")
            
        except Exception as e:
            st.error(f"❌ Error extracting images from PDF: {str(e)}")
        
        return images
    
    def extract_images_from_docx(self, docx_file):
        """Extract images from DOCX file"""
        images = []
        try:
            docx_file.seek(0)
            doc = docx.Document(docx_file)
            
            # Extract images from document relationships
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    try:
                        img_data = rel.target_part.blob
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        # Filter out very small images
                        if pil_image.width > 100 and pil_image.height > 100:
                            images.append({
                                'image': pil_image,
                                'source': f"DOCX Document Image",
                                'base64': self.encode_image_to_base64(pil_image)
                            })
                    except Exception as e:
                        st.warning(f"Could not process image from DOCX: {str(e)}")
                        continue
            
            st.success(f"📸 Extracted {len(images)} images from DOCX")
            
        except Exception as e:
            st.error(f"❌ Error extracting images from DOCX: {str(e)}")
        
        return images
    
    def extract_images_from_url(self, url):
        """Extract images from web page"""
        images = []
        try:
            st.info(f"🖼️ Looking for images at: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all image tags
            img_tags = soup.find_all('img')
            
            for i, img_tag in enumerate(img_tags[:10]):  # Limit to 10 images
                try:
                    img_url = img_tag.get('src')
                    if not img_url:
                        continue
                    
                    # Convert relative URLs to absolute
                    img_url = urljoin(url, img_url)
                    
                    # Skip very small images, icons, etc.
                    if any(skip in img_url.lower() for skip in ['icon', 'logo', 'avatar', 'thumbnail']):
                        continue
                    
                    # Download image
                    img_response = requests.get(img_url, timeout=10, headers=headers)
                    img_response.raise_for_status()
                    
                    # Open with PIL
                    pil_image = Image.open(io.BytesIO(img_response.content))
                    
                    # Filter by size
                    if pil_image.width > 200 and pil_image.height > 200:
                        alt_text = img_tag.get('alt', f'Image {i+1}')
                        images.append({
                            'image': pil_image,
                            'source': f"Web Image: {alt_text}",
                            'base64': self.encode_image_to_base64(pil_image),
                            'url': img_url
                        })
                
                except Exception as e:
                    continue  # Skip problematic images
            
            st.success(f"📸 Extracted {len(images)} images from web page")
            
        except Exception as e:
            st.error(f"❌ Error extracting images from URL: {str(e)}")
        
        return images

    def analyze_image_with_vision(self, image_data):
        """Analyze image using OpenAI Vision API"""
        if not self.client:
            return f"Image from {image_data['source']} - Analysis unavailable (no API key)"
            
        try:
            # Try multiple models in order of preference
            models_to_try = [
                "gpt-4o",           # Latest GPT-4 with vision
                "gpt-4o-mini",      # Faster, cheaper GPT-4 with vision
                "gpt-4-turbo",      # GPT-4 Turbo with vision
            ]
            
            for model in models_to_try:
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyze this image in detail. Describe what you see, including any text, charts, graphs, diagrams, data, concepts, or educational content. Focus on elements that could be used for educational questions."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_data['base64']}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=1000
                    )
                    
                    st.success(f"✅ Image analyzed using {model}")
                    return response.choices[0].message.content
                    
                except Exception as model_error:
                    st.warning(f"⚠️ Model {model} failed: {str(model_error)}")
                    continue
            
            # If all models fail, return a basic description
            st.error("❌ All vision models failed. Using basic description.")
            return f"Image from {image_data['source']} - Visual content detected but analysis unavailable"
            
        except Exception as e:
            st.error(f"❌ Error analyzing image: {str(e)}")
            return f"Image from {image_data['source']} (analysis failed)"
    
    def process_all_images(self, uploaded_files, urls, ref_file):
        """Extract and analyze all images from sources - FIXED VERSION"""
        all_images = []
        image_analyses = []
        
        # Process uploaded files for images
        if uploaded_files:
            for file in uploaded_files:
                st.info(f"🖼️ Looking for images in {file.name}...")
                
                if file.type == "application/pdf":
                    images = self.extract_images_from_pdf(file)
                elif "wordprocessingml" in file.type:
                    images = self.extract_images_from_docx(file)
                else:
                    continue
                
                all_images.extend(images)
        
        # Process reference file for images - FIX THE BUG HERE
        if ref_file:
            st.info(f"🖼️ Looking for images in reference file...")
            
            # Handle list of reference files (fixed from original bug)
            for file in ref_file:
                # Safety check - ensure file has the expected attributes
                if not hasattr(file, 'type'):
                    st.warning(f"⚠️ Reference file missing 'type' attribute: {type(file)}")
                    continue
                    
                if file.type == "application/pdf":
                    ref_images = self.extract_images_from_pdf(file)
                elif "wordprocessingml" in file.type:
                    ref_images = self.extract_images_from_docx(file)
                else:
                    ref_images = []
                    
                all_images.extend(ref_images)
        
        # Process URLs for images
        for url in urls:
            if url.strip():
                url_images = self.extract_images_from_url(url.strip())
                all_images.extend(url_images)
        
        # Analyze images with Vision API
        if all_images:
            st.info(f"🔍 Analyzing {len(all_images)} images with AI...")
            
            progress_bar = st.progress(0)
            for i, image_data in enumerate(all_images):
                analysis = self.analyze_image_with_vision(image_data)
                image_analyses.append({
                    'source': image_data['source'],
                    'analysis': analysis,
                    'image': image_data['image']
                })
                progress_bar.progress((i + 1) / len(all_images))
                time.sleep(0.5)  # Rate limiting
            
            progress_bar.empty()
            st.success(f"✅ Analyzed {len(image_analyses)} images successfully!")
        
        return image_analyses