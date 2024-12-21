from flask import Blueprint, request, jsonify
from Controller.imageUploadController import (crop_image, transform_image, upload_image_to_cloudinary,fetch_image_from_db,
                                              fetch_images_with_pagination, generate_color_histogram,
                                              generate_segmentation_mask)

# Create a blueprint for image routes
image_routes = Blueprint('image_routes', __name__)

# Route for uploading a single image
@image_routes.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No file part'}), 400

    result, status_code = upload_image_to_cloudinary(file)
    return jsonify(result), status_code

# Route for uploading multiple images (batch upload)
@image_routes.route('/upload_images', methods=['POST'])
def upload_images():
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    # Logic to handle multiple image uploads if needed
    image_urls = []
    for file in files:
        result, _ = upload_image_to_cloudinary(file)
        if 'image_url' in result:
            image_urls.append(result['image_url'])
    
    return jsonify({'message': 'Images uploaded successfully', 'image_urls': image_urls}), 200

# Route for fetching an image by public ID
@image_routes.route('/fetch_image/<public_id>', methods=['GET'])
def fetch_image(public_id):
    result, status_code = fetch_image_from_db(public_id)
    return jsonify(result), status_code

@image_routes.route('/fetch_images', methods=['GET'])
def fetch_images():
    try:
        # Get page and per_page query parameters (default to page 1, per_page 10)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Call the controller function to fetch images
        result = fetch_images_with_pagination(page, per_page)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@image_routes.route('/generate_histogram/<int:db_id>', methods=['GET'])
def generate_histogram(db_id):
    return generate_color_histogram(db_id)


@image_routes.route('/generate_segmentation/<int:db_id>', methods=['POST'])
def generate_segmentation(db_id):
    # Get the color bounds from the request
    lower_bound = request.json.get('lower_bound')  # e.g., [35, 43, 46]
    upper_bound = request.json.get('upper_bound')  # e.g., [77, 255, 255]
    
    if not lower_bound or not upper_bound:
        return jsonify({'error': 'Color bounds are required'}), 400

    # Generate segmentation mask and segmented image as responses
    mask_response, segmented_response = generate_segmentation_mask(db_id, lower_bound, upper_bound)

    if isinstance(mask_response, dict) and 'error' in mask_response:
        return jsonify(mask_response), 404

    # Return both responses as a multipart response or handle separately
    # This example assumes you want to send both as separate responses.
    return mask_response, segmented_response

# Route to resize image
@image_routes.route('/resize_image/<int:image_id>', methods=['POST'])
def resize(image_id):
    width = request.json.get('width')
    height = request.json.get('height')
    format_type = request.json.get('format_type', None)

    if not width or not height:
        return jsonify({'error': 'Width and height are required'}), 400

    # Call the controller method (you can include crop and format_type if needed)
    return transform_image(image_id, width, height, format_type)

@image_routes.route('/crop_image/<int:image_id>', methods=['POST'])
def crop_image_route(image_id):
    # Get cropping parameters from the request body
    x = request.json.get('x')
    y = request.json.get('y')
    width = request.json.get('width')
    height = request.json.get('height')

    if x is None or y is None or width is None or height is None:
        return {'error': 'x, y, width, and height are required for cropping'}, 400

    # Call the crop_image function to crop the image
    return crop_image(image_id, x, y, width, height)
