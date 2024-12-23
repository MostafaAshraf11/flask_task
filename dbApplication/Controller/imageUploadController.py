import io
import cloudinary
import cloudinary.api
from cloudinary.uploader import upload, destroy
from werkzeug.utils import secure_filename
from Models.image_model import Image
from Models.dbModel import db 
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

def upload_image_to_cloudinary(file):
    """
    Upload a single image to Cloudinary and save its details to the database.

    Input: 
        file (FileStorage): The image file to upload.
    Output: 
        dict: Success message with image URL, or an error message.
        int: HTTP status code.
    """
    try:
        filename = secure_filename(file.filename)
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']
        public_id = upload_result['public_id']

        image = Image(filename=filename, url=image_url, public_id=public_id)
        db.session.add(image)
        db.session.commit()

        return {'message': 'Image uploaded successfully', 'image_url': image_url}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

def upload_images_to_cloudinary(files):
    """
    Upload multiple images to Cloudinary and save their details to the database.

    Input:
        files (list): List of FileStorage objects representing the images.
    Output:
        dict: Success message with details of uploaded images, or an error message.
        int: HTTP status code.
    """
    uploaded_images = []
    try:
        for file in files:
            filename = secure_filename(file.filename)
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result['secure_url']
            public_id = upload_result['public_id']

            image = Image(filename=filename, url=image_url, public_id=public_id)
            db.session.add(image)
            uploaded_images.append({'filename': filename, 'image_url': image_url, 'public_id': public_id})

        db.session.commit()
        return {'message': 'Images uploaded successfully', 'uploaded_images': uploaded_images}, 200
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

def fetch_image_from_db(db_id):
    """
    Fetch image details from the database by ID.

    Input: 
        db_id (int): The ID of the image record.
    Output: 
        dict: Image details or an error message.
        int: HTTP status code.
    """
    try:
        image = Image.query.get(db_id)
        if image:
            return {'filename': image.filename, 'url': image.url}, 200
        else:
            return {'error': 'Image not found in database'}, 404
    except Exception as e:
        return {'error': str(e)}, 500

def fetch_images_with_pagination(page, per_page):
    """
    Fetch paginated images from the database.

    Input:
        page (int): Current page number.
        per_page (int): Number of images per page.
    Output:
        dict: Paginated image details or an error message.
    """
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
    Fetch an image from a given URL and return it as a NumPy array.

    Input:
        image_url (str): URL of the image to fetch.
    Output:
        numpy.ndarray: Image as an array or None on failure.
    """
    try:
        response = requests.get(image_url)
        img = PILImage.open(BytesIO(response.content))
        img = np.array(img)
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
    except Exception:
        return None

def generate_color_histogram(db_id):
    """
    Generate a color histogram for an image in the database.

    Input:
        db_id (int): The ID of the image in the database.
    Output:
        Response: Graph image as a PNG response or an error message.
    """
    try:
        image_data, status_code = fetch_image_from_db(db_id)
        if status_code != 200:
            return {'error': 'Image not found'}, 404

        image_url = image_data['url']
        image = fetch_image_from_url(image_url)
        if image is None:
            return {'error': 'Image could not be retrieved from the URL'}, 404

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        color_channels = ('r', 'g', 'b')

        plt.figure(figsize=(10, 6))
        for i, col in enumerate(color_channels):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            plt.plot(hist, color=col, label=f'{col.upper()} channel')
        
        plt.title('Color Histogram')
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Frequency')
        plt.legend()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        return Response(buffer, mimetype='image/png')
    except Exception as e:
        return {'error': str(e)}, 500

def generate_segmentation_mask(db_id, lower_bound, upper_bound):
    """
    Generate a segmentation mask for an image based on HSV thresholds and return the result.

    In this method, we apply an HSV-based mask to isolate specific regions in an image
    using the given lower and upper HSV thresholds. The result is returned as a PNG image
    in a byte stream.

    Input:
        db_id (int): ID of the image record in the database.
        lower_bound (list[int]): Lower HSV threshold as a list of integers [H, S, V].
        upper_bound (list[int]): Upper HSV threshold as a list of integers [H, S, V].

    Output:
        BytesIO: Segmented image in PNG format as a byte stream, or an error message with a status code.
    """
    image_data, status_code = fetch_image_from_db(db_id)
    if status_code != 200:
        return image_data  

    image_url = image_data['url']  
    image = fetch_image_from_url(image_url)
    if image is None:
        return {'error': 'Image could not be retrieved from the URL'}, 404

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, np.array(lower_bound), np.array(upper_bound))
    segmented_image = cv2.bitwise_and(image, image, mask=mask)

    _, segmented_image_buffer = cv2.imencode('.png', segmented_image)
    segmented_image_bytes = io.BytesIO(segmented_image_buffer.tobytes())

    return segmented_image_bytes

def transform_image(image_id, width, height, format_type=None):
    """
    Transform an image by resizing it to the specified dimensions and optionally converting its format.
    The transformed image is uploaded back to Cloudinary, and its URL is updated in the database.

    Input:
        image_id (int): ID of the image record in the database.
        width (int): New width for the image.
        height (int): New height for the image.
        format_type (str, optional): Target image format (e.g., 'JPEG', 'PNG'). Defaults to None.

    Output:
        dict: Success message with the new image URL, or an error message with a status code.
    """
    try:
        image = Image.query.get(image_id)
        if not image:
            return {'error': 'Image not found'}, 404

        image_url = image.url
        image_file = BytesIO(requests.get(image_url).content)
        img = PILImage.open(image_file)
        img = img.resize((width, height))

        if format_type:
            format_type = format_type.upper()
            if format_type == 'JPG':
                format_type = 'JPEG'
            img_format = format_type
        else:
            img_format = img.format if img.format else 'PNG'

        new_image_stream = BytesIO()
        img.save(new_image_stream, format=img_format)
        new_image_stream.seek(0)

        upload_result = upload(new_image_stream, public_id=image.public_id, overwrite=True)
        new_url = upload_result['secure_url']

        image.url = new_url
        db.session.commit()

        return {'message': 'Image resized and transformed successfully', 'image_url': new_url}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def crop_image(image_id, x, y, width, height):
    """
    Crop an image to the specified dimensions and upload the cropped result to Cloudinary.
    The image URL in the database is updated after the crop.

    Input:
        image_id (int): ID of the image record in the database.
        x (int): X-coordinate of the top-left corner of the crop box.
        y (int): Y-coordinate of the top-left corner of the crop box.
        width (int): Width of the crop box.
        height (int): Height of the crop box.

    Output:
        dict: Success message with the new image URL, or an error message with a status code.
    """
    try:
        image = Image.query.get(image_id)
        if not image:
            return {'error': 'Image not found'}, 404

        image_data = cloudinary.api.resource(image.public_id)
        image_url = image_data['secure_url']

        image_file = BytesIO(requests.get(image_url).content)
        img = PILImage.open(image_file)

        image_width, image_height = img.size
        if x + width > image_width or y + height > image_height:
            return {'error': "Crop area exceeds image bounds"}, 400

        cropped_image = img.crop((x, y, x + width, y + height))

        new_image_stream = BytesIO()
        cropped_image.save(new_image_stream, format=img.format)
        new_image_stream.seek(0)

        upload_result = upload(new_image_stream, public_id=image.public_id, overwrite=True)
        new_url = upload_result['secure_url']

        image.url = new_url
        db.session.commit()

        return {'message': 'Image cropped successfully', 'image_url': new_url}, 200
    except Exception as e:
        return {'error': str(e)}, 500
