from flask import Blueprint, Response, request, jsonify
from Controller.imageUploadController import (crop_image, transform_image, upload_image_to_cloudinary,fetch_image_from_db,
                                              fetch_images_with_pagination, generate_color_histogram,
                                              generate_segmentation_mask)

# Create a blueprint for image routes
image_routes = Blueprint('image_routes', __name__)

"""
Image Routes Documentation:
Provides APIs for uploading, fetching, and manipulating images.
"""

# Route for uploading a single image
@image_routes.route('/upload_image', methods=['POST'])
def upload_image():
    """
    Upload a single image.

    Input:
        Form-Data with:
        - "image" (file): The image file to be uploaded.

    Output:
        JSON response with:
        - "image_url" (str): URL of the uploaded image.
        - HTTP status code.
    """
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No file part'}), 400

    result, status_code = upload_image_to_cloudinary(file)
    return jsonify(result), status_code

# Route for uploading multiple images (batch upload)
@image_routes.route('/upload_images', methods=['POST'])
def upload_images():
    """
    Upload multiple images.

    Input:
        Form-Data with:
        - "images" (file[]): List of image files to be uploaded.

    Output:
        JSON response with:
        - "message" (str): Success message.
        - "image_urls" (list[str]): List of URLs for the uploaded images.
        - HTTP status code.
    """
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    image_urls = []
    for file in files:
        result, _ = upload_image_to_cloudinary(file)
        if 'image_url' in result:
            image_urls.append(result['image_url'])
    
    return jsonify({'message': 'Images uploaded successfully', 'image_urls': image_urls}), 200

# Route for fetching an image by public ID
@image_routes.route('/fetch_image/<public_id>', methods=['GET'])
def fetch_image(public_id):
    """
    Fetch an image by its public ID.

    Input:
        Path Parameter:
        - "public_id" (str): The public ID of the image to fetch.

    Output:
        JSON response with:
        - Image details (e.g., URL, metadata).
        - HTTP status code.
    """
    result, status_code = fetch_image_from_db(public_id)
    return jsonify(result), status_code

# Route for fetching images with pagination
@image_routes.route('/fetch_images', methods=['GET'])
def fetch_images():
    """
    Fetch multiple images with pagination.

    Input:
        Query Parameters:
        - "page" (int): Page number (default: 1).
        - "per_page" (int): Number of images per page (default: 10).

    Output:
        JSON response with:
        - List of images (paginated).
        - HTTP status code.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result = fetch_images_with_pagination(page, per_page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for generating a color histogram
@image_routes.route('/generate_histogram/<int:db_id>', methods=['GET'])
def generate_histogram(db_id):
    """
    Generate a color histogram for an image.

    Input:
        Path Parameter:
        - "db_id" (int): Database ID of the image.

    Output:
        PNG image of the histogram.
    """
    return generate_color_histogram(db_id)

# Route for generating a segmentation mask
@image_routes.route('/generate_segmentation/<int:db_id>', methods=['POST'])
def generate_segmentation(db_id):
    """
    Generate a segmentation mask for an image based on color bounds.

    Input:
        Path Parameter:
        - "db_id" (int): Database ID of the image.
        JSON Body:
        - "lower_bound" (list[int]): Lower color bound (e.g., [35, 43, 46]).
        - "upper_bound" (list[int]): Upper color bound (e.g., [77, 255, 255]).

    Output:
        PNG image of the segmentation mask.
    """
    lower_bound = request.json.get('lower_bound')
    upper_bound = request.json.get('upper_bound')
    
    if not lower_bound or not upper_bound:
        return jsonify({'error': 'Color bounds are required'}), 400

    segmented_image_bytes = generate_segmentation_mask(db_id, lower_bound, upper_bound)

    if isinstance(segmented_image_bytes, dict) and 'error' in segmented_image_bytes:
        return jsonify(segmented_image_bytes), 404

    return Response(segmented_image_bytes, mimetype='image/png')

# Route to resize an image
@image_routes.route('/resize_image/<int:image_id>', methods=['POST'])
def resize(image_id):
    """
    Resize an image to specified dimensions.

    Input:
        Path Parameter:
        - "image_id" (int): ID of the image to resize.
        JSON Body:
        - "width" (int): New width of the image.
        - "height" (int): New height of the image.
        - "format_type" (str, optional): Format of the resized image (e.g., "png", "jpeg").

    Output:
        JSON response with:
        - Resized image details.
        - HTTP status code.
    """
    width = request.json.get('width')
    height = request.json.get('height')
    format_type = request.json.get('format_type', None)

    if not width or not height:
        return jsonify({'error': 'Width and height are required'}), 400

    return transform_image(image_id, width, height, format_type)

# Route to crop an image
@image_routes.route('/crop_image/<int:image_id>', methods=['POST'])
def crop_image_route(image_id):
    """
    Crop an image using specified dimensions.

    Input:
        Path Parameter:
        - "image_id" (int): ID of the image to crop.
        JSON Body:
        - "x" (int): X-coordinate of the top-left corner.
        - "y" (int): Y-coordinate of the top-left corner.
        - "width" (int): Width of the cropped area.
        - "height" (int): Height of the cropped area.

    Output:
        JSON response with:
        - Cropped image details.
        - HTTP status code.
    """
    x = request.json.get('x')
    y = request.json.get('y')
    width = request.json.get('width')
    height = request.json.get('height')

    if x is None or y is None or width is None or height is None:
        return jsonify({'error': 'x, y, width, and height are required for cropping'}), 400

    return crop_image(image_id, x, y, width, height)
