from flask import request, jsonify
from Controller.loan_approvalController import (
    generate_bar_chart,
    generate_line_graph,
    upload_csv,
    create_loan,
    get_all_loans,
    get_loan_by_id,
    update_loan,
    delete_loan,
    filter_and_aggregate,
    compute_advanced_stats
)


def register_routes(app, db):
    @app.route('/upload_csv', methods=['POST'])
    def upload_csv_route():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        response, status_code = upload_csv(file)
        return jsonify(response), status_code

    @app.route('/loan_approval', methods=['POST'])
    def create_loan_route():
        data = request.get_json()
        response, status_code = create_loan(data)
        return jsonify(response), status_code

    @app.route('/loan_approval', methods=['GET'])
    def get_all_loans_route():
        page = request.args.get('page', 1, type=int)
        response = get_all_loans(page)
        return jsonify(response)

    @app.route('/loan_approval/<int:loan_id>', methods=['GET'])
    def get_loan_route(loan_id):
        response = get_loan_by_id(loan_id)
        return jsonify(response)

    @app.route('/loan_approval/<int:loan_id>', methods=['PUT'])
    def update_loan_route(loan_id):
        data = request.get_json()
        response = update_loan(loan_id, data)
        return jsonify(response)

    @app.route('/loan_approval/<int:loan_id>', methods=['DELETE'])
    def delete_loan_route(loan_id):
        response = delete_loan(loan_id)
        return jsonify(response)
    
    @app.route('/loan_approval/filter', methods=['POST'])
    def filter_route():
        data = request.get_json()
        response, status_code = filter_and_aggregate(data)
        return jsonify(response), status_code
    
    @app.route('/loan_approval/stats', methods=['POST'])
    def stats_route():
        data = request.get_json()
        if not data or "column_name" not in data:
            return jsonify({"error": "Please provide a 'column_name' in the request body"}), 400

        column_name = data["column_name"]
        response, status_code = compute_advanced_stats(column_name)
        return jsonify(response), status_code
    
# POST route for Bar Chart (Histogram)
    @app.route('/loan_approval/chart', methods=['POST'])
    def chart_route():
        data = request.get_json()
        if not data or "column_name" not in data:
            return jsonify({"error": "Please provide a 'column_name' in the request body"}), 400

        column_name = data["column_name"]
        
        # Call generate_bar_chart to get the bar chart image and return the response directly
        return generate_bar_chart(column_name)


    # POST route for Line Graph
    @app.route('/loan_approval/graph', methods=['POST'])
    def graph_route():
        data = request.get_json()
        if not data or "column_name" not in data:
            return jsonify({"error": "Please provide a 'column_name' in the request body"}), 400

        column_name = data["column_name"]
        
        # Call generate_line_graph to get the line graph image and return the response directly
        return generate_line_graph(column_name)
        
        


