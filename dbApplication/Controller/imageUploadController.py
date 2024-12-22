import io
import os
import cloudinary
import cloudinary.api
from cloudinary.uploader import upload, destroy
from werkzeug.utils import secure_filename
from Models.image_model import Image
from Models.dbModel import db  # Import the database instance and Image model
import requests
import cv2
import numpy as np
from io import BytesIO
from PIL import Image as PILImage
import matplotlib.pyplot as plt
from flask import Response


# Cloudinary Configuration
cloudinary.config( 
    cloud_name="dgfukkkda", 
    api_key="555114447294219", 
    api_secret="JqV25j1fKLKRXGn2-PX55YoCYX4",  # Your API Secret
    secure=True
)

# Method for uploading a single image to Cloudinary and saving it to the database
def upload_image_to_cloudinary(file):
    try:
        # Secure the filename
        filename = secure_filename(file.filename)

        # Upload image to Cloudinary
        upload_result = cloudinary.uploader.upload(file)

        # Get the secure URL and public_id for the uploaded image
        image_url = upload_result['secure_url']
        public_id = upload_result['public_id']

        # Save the image record in the database (including public_id)
        image = Image(filename=filename, url=image_url, public_id=public_id)
        db.session.add(image)
        db.session.commit()

        return {'message': 'Image uploaded successfully', 'image_url': image_url}, 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return {'error': str(e)}, 500

# Method for batch uploading images to Cloudinary and saving them to the database
def upload_images_to_cloudinary(files):
    uploaded_images = []
    try:
        for file in files:
            filename = secure_filename(file.filename)
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result['secure_url']
            public_id = upload_result['public_id']

            # Save image details in the database (including public_id)
            image = Image(filename=filename, url=image_url, public_id=public_id)
            db.session.add(image)
            uploaded_images.append({'filename': filename, 'image_url': image_url, 'public_id': public_id})

        db.session.commit()

        return {'message': 'Images uploaded successfully', 'uploaded_images': uploaded_images}, 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return {'error': str(e)}, 500

def fetch_image_from_db(db_id):
    try:
        # Fetch the image record from the database using the provided ID
        image = Image.query.get(db_id)
        if image:
            # Return the image data (URL and other relevant info)
            return {'filename': image.filename, 'url': image.url}, 200
        else:
            return {'error': 'Image not found in database'}, 404
    except Exception as e:
        # Handle any errors that occur during the process
        return {'error': str(e)}, 500

def fetch_images_with_pagination(page, per_page):
    try:
        images = Image.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'images': [image.to_dict() for image in images.items],
            'total': images.total,
            'pages': images.pages,
            'current_page': images.page
        }
    except Exception as e:
        raise Exception(f"Error fetching images: {str(e)}")

def fetch_image_from_url(image_url):
    """
    Fetch the image from the URL and return it as a NumPy array.
    """
    try:
        response = requests.get(image_url)
        img = PILImage.open(BytesIO(response.content))
        img = np.array(img)
        # Convert RGB to BGR (OpenCV uses BGR by default)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img
    except Exception as e:
        return None   

def generate_color_histogram(db_id):
    """
    Generate a color histogram for the image located at the given database ID and return it as a graph.
    """
    try:
        # Fetch the image data (URL and filename) from the database using db_id
        image_data, status_code = fetch_image_from_db(db_id)
        if status_code != 200:
            return {'error': 'Image not found'}, 404

        image_url = image_data['url']  # Get the URL from the database record

        # Fetch the image from the URL
        image = fetch_image_from_url(image_url)
        if image is None:
            return {'error': 'Image could not be retrieved from the URL'}, 404

        # Convert the image from BGR to RGB (for visualization consistency)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Calculate histogram for each color channel (R, G, B)
        color_channels = ('r', 'g', 'b')

        # Plot the histograms
        plt.figure(figsize=(10, 6))
        for i, col in enumerate(color_channels):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            plt.plot(hist, color=col, label=f'{col.upper()} channel')
        
        plt.title('Color Histogram')
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Frequency')
        plt.legend()
        
        # Save the plot to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()  # Close the plot to free resources
        
        # Return the graph as a response
        return Response(buffer, mimetype='image/png')

    except Exception as e:
        # Handle unexpected errors
        return {'error': str(e)}, 500

def generate_segmentation_mask(db_id, lower_bound, upper_bound):
    """
    Generate a segmentation mask and save the results as images.
    """
    # Fetch the image data (URL and filename) from the database using db_id
    image_data, status_code = fetch_image_from_db(db_id)
    if status_code != 200:
        return image_data  # Return error message if the image is not found
    
    image_url = image_data['url']  # Get the URL from the database record

    # Fetch the image from the URL
    image = fetch_image_from_url(image_url)
    if image is None:
        return {'error': 'Image could not be retrieved from the URL'}, 404
    
    # Convert to HSV (Hue, Saturation, Value) color space for easier thresholding
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Apply the mask to the image
    mask = cv2.inRange(hsv_image, np.array(lower_bound), np.array(upper_bound))
    
    # Apply the mask to get the segmented regions
    segmented_image = cv2.bitwise_and(image, image, mask=mask)

    # Encode the segmented image to PNG format and save to a buffer
    _, segmented_image_buffer = cv2.imencode('.png', segmented_image)
    
    # Create a byte buffer for the segmented image
    segmented_image_bytes = io.BytesIO(segmented_image_buffer.tobytes())
    
    return segmented_image_bytes


def transform_image(image_id, width, height, format_type=None):
    try:
        # Get the image record from the database
        image = Image.query.get(image_id)
        if not image:
            return {'error': 'Image not found'}, 404

        # Download the image using the stored URL
        image_url = image.url  # Use the URL from the database directly
        image_file = BytesIO(requests.get(image_url).content)
        
        # Open the image using Pillow
        img = PILImage.open(image_file)

        # Resize the image
        img = img.resize((width, height))  # Resize the image

        # Convert the format if a format type is provided (e.g., to JPEG or PNG)
        if format_type:
            format_type = format_type.upper()  # Ensure it's in uppercase
            if format_type == 'JPG':
                format_type = 'JPEG'  # PIL uses 'JPEG' for jpg
            img_format = format_type
        else:
            img_format = img.format if img.format else 'PNG'  # Default to PNG if no format is provided

        # Save the image to a BytesIO object to upload back to Cloudinary
        new_image_stream = BytesIO()
        img.save(new_image_stream, format=img_format)
        new_image_stream.seek(0)

        # Upload the transformed image back to Cloudinary, overwriting the original image
        upload_result = upload(new_image_stream, public_id=image.public_id, overwrite=True)

        # Get the new URL
        new_url = upload_result['secure_url']

        # Update the image record in the database with the new URL
        image.url = new_url
        db.session.commit()

        return {'message': 'Image resized and transformed successfully', 'image_url': new_url}, 200
    except Exception as e:
        return {'error': str(e)}, 500

def crop_image(image_id, x, y, width, height):
    try:
        # Get the image record from the database
        image = Image.query.get(image_id)
        if not image:
            return {'error': 'Image not found'}, 404

        # Download the image from Cloudinary using the public_id
        image_data = cloudinary.api.resource(image.public_id)
        image_url = image_data['secure_url']

        # Open the image using Pillow
        image_file = BytesIO(requests.get(image_url).content)
        img = PILImage.open(image_file)

        # Ensure the crop area is within the image bounds
        image_width, image_height = img.size
        if x + width > image_width or y + height > image_height:
            return {'error': "Crop area exceeds image bounds"}, 400

        # Crop the image
        cropped_image = img.crop((x, y, x + width, y + height))

        # Save the cropped image to a BytesIO object
        new_image_stream = BytesIO()
        cropped_image.save(new_image_stream, format=img.format)
        new_image_stream.seek(0)

        # Upload the cropped image to Cloudinary
        upload_result = upload(new_image_stream, public_id=image.public_id, overwrite=True)

        # Get the new URL for the cropped image
        new_url = upload_result['secure_url']

        # Update the image record in the database with the new URL
        image.url = new_url
        db.session.commit()

        return {'message': 'Image cropped successfully', 'image_url': new_url}, 200
    except Exception as e:
        return {'error': str(e)}, 500
