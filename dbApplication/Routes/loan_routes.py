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
        """
        Upload a CSV file to populate the loan approval dataset.

        Input:
            Form-Data with:
            - "file" (file): The CSV file to be uploaded.

        Output:
            JSON response indicating success or failure of the upload, along with the HTTP status code.
        """
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        response, status_code = upload_csv(file)
        return jsonify(response), status_code

    @app.route('/loan_approval', methods=['POST'])
    def create_loan_route():
        """
        Create a new loan approval record.

        Input:
            JSON object with:
            - "income" (float): Applicant's income.
            - "loan_amount" (float): Loan amount requested.
            - "credit_score" (int): Applicant's credit score.
            - "asset_value" (float): Value of the applicant's assets.
            - "loan_status" (str): Approval status of the loan (e.g., "Approved", "Rejected").

        Output:
            JSON response indicating success or failure of the record creation, along with the HTTP status code.
        """
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
        """
        Apply filters, aggregation, or both to the loan approval dataset.

        Input:
            JSON object with the following optional keys:
            - "filters" (list[dict]): List of filter conditions, each as a dictionary with keys:
                - "column" (str): The column to filter (e.g., "loan_status").
                - "value" (varies): The value to compare against.
                - "operator" (str): The comparison operator (e.g., "equals", "greater_than").
            - "aggregate_type" (str, optional): Aggregation type (e.g., "avg", "sum").
            - "field" (str, optional): The column on which to perform aggregation.
            - "page" (int, optional): Page number for paginated results.

        Output:
            JSON response with filtered or aggregated data, along with the HTTP status code.
        """
        data = request.get_json()
        response, status_code = filter_and_aggregate(data)
        return jsonify(response), status_code


    @app.route('/loan_approval/stats', methods=['POST'])
    def stats_route():
        """
        Compute advanced statistics for a specified column in the loan approval dataset.

        Input:
            JSON object with:
            - "column_name" (str): The column for which to compute statistics (e.g., "income").

        Output:
            JSON response with statistics or an error message if the column is not provided, along with the HTTP status code.
        """
        data = request.get_json()
        if not data or "column_name" not in data:
            return jsonify({"error": "Please provide a 'column_name' in the request body"}), 400

        column_name = data["column_name"]
        response, status_code = compute_advanced_stats(column_name)
        return jsonify(response), status_code


    @app.route('/loan_approval/chart', methods=['POST'])
    def chart_route():
        """
        Generate a bar chart for a specified column in the loan approval dataset.

        Input:
            JSON object with:
            - "column_name" (str): The column for which to generate the bar chart.

        Output:
            The generated bar chart or an error message if the column is not provided.
        """
        data = request.get_json()
        if not data or "column_name" not in data:
            return jsonify({"error": "Please provide a 'column_name' in the request body"}), 400

        column_name = data["column_name"]
        return generate_bar_chart(column_name)


    @app.route('/loan_approval/graph', methods=['POST'])
    def graph_route():
        """
        Generate a line graph for a specified column in the loan approval dataset.

        Input:
            JSON object with:
            - "column_name" (str): The column for which to generate the line graph.

        Output:
            The generated line graph or an error message if the column is not provided.
        """
        data = request.get_json()
        if not data or "column_name" not in data:
            return jsonify({"error": "Please provide a 'column_name' in the request body"}), 400

        column_name = data["column_name"]
        return generate_line_graph(column_name)


