from flask import Response, request, jsonify
import pandas as pd
import os
from Models.loan_models import LoanApproval
from Models.dbModel import db
from sqlalchemy import func, or_, and_
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_csv(file):
    """
    Uploads a CSV file to the server, validates its content, processes the data using pandas, and inserts the records into the database using SQLAlchemy and pandas.
    
    Input: file (CSV file)
    Expected Output: JSON response with a success message or error details.
    """
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if not file.filename.endswith('.csv'):
        return {'error': 'Invalid file format, please upload a CSV file'}, 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        data = pd.read_csv(filepath)
        required_columns = ['loan_id', 'income', 'loan_amount', 'credit_score', 'loan_status', 'asset_value']
        for col in required_columns:
            if col not in data.columns:
                return {'error': f'Missing required column: {col}'}, 400

        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        data.dropna(subset=required_columns, inplace=True)
        float_columns = ['income', 'loan_amount', 'credit_score', 'asset_value']
        data[float_columns] = data[float_columns].round(1)

        for _, row in data.iterrows():
            new_loan = LoanApproval(
                loan_id=row['loan_id'],
                income=row['income'],
                loan_amount=row['loan_amount'],
                credit_score=row['credit_score'],
                loan_status=row['loan_status'],
                asset_value=row['asset_value']
            )
            db.session.add(new_loan)

        db.session.commit()
        return {'message': f'{len(data)} loans successfully added to the database'}, 201

    except Exception as e:
        return {'error': str(e)}, 500

def create_loan(data):
    """
    Creates a new loan approval entry in the database using SQLAlchemy.
    Input: data (dictionary containing loan fields)
    Expected Output: JSON response with loan ID and success message.
    """
    required_fields = ['income', 'loan_amount', 'credit_score', 'asset_value', 'loan_status']
    for field in required_fields:
        if field not in data:
            return {'error': f'Missing required field: {field}'}, 400

    new_loan = LoanApproval(
        income=data['income'],
        loan_amount=data['loan_amount'],
        credit_score=data['credit_score'],
        asset_value=data['asset_value'],
        loan_status=data['loan_status']
    )

    db.session.add(new_loan)
    db.session.commit()

    return {'message': 'Loan approval created', 'loan_id': new_loan.loan_id}, 201

def get_all_loans(page, per_page=20):
    """
    Retrieves a paginated list of all loan approvals from the database using SQLAlchemy.
    Input: page (integer), per_page (integer, optional, default 20)
    Expected Output: JSON response with loan details and pagination metadata.
    """
    loans = LoanApproval.query.paginate(page=page, per_page=per_page)

    loans_list = [{
        'loan_id': loan.loan_id,
        'income': loan.income,
        'loan_amount': loan.loan_amount,
        'credit_score': loan.credit_score,
        'asset_value': loan.asset_value,
        'loan_status': loan.loan_status
    } for loan in loans.items]

    return {
        'page': loans.page,
        'per_page': loans.per_page,
        'total_pages': loans.pages,
        'total_items': loans.total,
        'data': loans_list
    }

def get_loan_by_id(loan_id):
    """
    Retrieves the details of a specific loan approval by ID using SQLAlchemy.
    Input: loan_id (integer)
    Expected Output: JSON response with loan details or error message.
    """
    loan = LoanApproval.query.get_or_404(loan_id)
    return {
        'loan_id': loan.loan_id,
        'income': loan.income,
        'loan_amount': loan.loan_amount,
        'credit_score': loan.credit_score,
        'asset_value': loan.asset_value,
        'loan_status': loan.loan_status
    }

def update_loan(loan_id, data):
    """
    Updates an existing loan approval entry in the database using SQLAlchemy.
    
    Input: loan_id (integer), data (dictionary containing updated loan fields)
    Expected Output: JSON response with success or error message.
    """
    loan = LoanApproval.query.get_or_404(loan_id)

    if 'income' in data:
        loan.income = data['income']

    if 'loan_amount' in data:
        loan.loan_amount = data['loan_amount']

    if 'asset_value' in data:
        loan.asset_value = data['asset_value']

    if 'credit_score' in data:
        loan.credit_score = data['credit_score']

    if 'loan_status' in data:
        loan.loan_status = data['loan_status']

    db.session.commit()
    return {'message': 'Loan approval updated'}

def delete_loan(loan_id):
    """
    Deletes a specific loan approval entry from the database using SQLAlchemy .

    Input: loan_id (integer)
    Expected Output: JSON response with success or error message.
    """
    loan = LoanApproval.query.get_or_404(loan_id)
    db.session.delete(loan)
    db.session.commit()
    return {'message': 'Loan approval deleted'}

def apply_filters(query, filters):
    """
    Applies filtering conditions to the database query based on specified filters.
    
    Input: query (SQLAlchemy query object), filters (list of filtering conditions)
    Expected Output: Filtered query or error message.
    """
    filter_conditions = []
    for condition in filters:
        column = condition.get('column')
        value = condition.get('value')
        operator = condition.get('operator', 'equals')

        if column not in ['income', 'loan_amount', 'credit_score', 'loan_status', 'asset_value']:
            return {"error": f"Unsupported column: {column}"}, 400

        if operator == 'equals':
            filter_conditions.append(getattr(LoanApproval, column) == value)
        elif operator == 'greater_than':
            filter_conditions.append(getattr(LoanApproval, column) > value)
        elif operator == 'less_than':
            filter_conditions.append(getattr(LoanApproval, column) < value)
        else:
            return {"error": f"Unsupported operator: {operator}"}, 400

    if filter_conditions:
        query = query.filter(and_(*filter_conditions))

    return query

def calculate_aggregate(query, aggregate_type, field):
    """
    Calculates aggregate values such as sum, average, count, max, or min for a specified field.
    Input: query (SQLAlchemy query object), aggregate_type (string), field (string)
    Expected Output: Aggregate value or error message.
    """
    try:
        result = db.session.query(getattr(func, aggregate_type)(getattr(LoanApproval, field))).scalar()
        return result
    except Exception as e:
        return {"error": str(e)}, 400


def filter_and_aggregate(data):
    """
    Filters and aggregates data from the LoanApproval table based on request parameters.

    Args:
        data (dict): A dictionary containing:
            - filters (list): List of filters to apply to the query.
            - aggregate_type (str): Type of aggregation (e.g., 'sum', 'avg').
            - field (str): Field on which to perform the aggregation.
            - page (int): Current page for pagination.
            - per_page (int): Number of items per page.

    Returns:
        tuple: Response dictionary containing filtered data or aggregate results, and HTTP status code.
    """
    filters = data.get('filters', [])
    aggregate_type = data.get('aggregate_type')
    field = data.get('field')
    page = data.get('page', 1)
    per_page = data.get('per_page', 20)

    query = LoanApproval.query

    if filters:
        query = apply_filters(query, filters)

    if aggregate_type and field:
        aggregate_result = calculate_aggregate(query, aggregate_type, field)
        return {
            "aggregate_type": aggregate_type,
            "field": field,
            "result": aggregate_result
        }, 200

    pagination_query = query.paginate(page=page, per_page=per_page, error_out=False)
    filtered_loans = pagination_query.items

    loan_list = [loan.to_dict() for loan in filtered_loans]

    return {
        "filtered_loans": loan_list,
        "total": pagination_query.total,
        "pages": pagination_query.pages,
        "current_page": pagination_query.page,
        "per_page": pagination_query.per_page
    }, 200


def compute_advanced_stats(column_name):
    """
    Computes advanced statistical measures for a specified column in the LoanApproval table.

    Args:
        column_name (str): Name of the column to analyze.

    Returns:
        tuple: Response dictionary containing statistical measures or error message, and HTTP status code.
    """
    try:
        rows = db.session.query(getattr(LoanApproval, column_name)).all()
        column_values = [row[0] for row in rows if row[0] is not None]

        if len(column_values) < 2:
            return {"error": "Not enough data points to compute statistics"}, 400

        column_values = np.array(column_values)
        column_values = column_values[~np.isnan(column_values)]

        mean = round(np.mean(column_values), 1)
        median = round(np.median(column_values), 1)
        mode_result = stats.mode(column_values, keepdims=True)
        mode = round(mode_result.mode[0], 1) if mode_result.count[0] > 0 else None
        q1 = round(np.percentile(column_values, 25), 1)
        q3 = round(np.percentile(column_values, 75), 1)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = column_values[(column_values < lower_bound) | (column_values > upper_bound)]

        return {
            "mean": mean,
            "median": median,
            "mode": mode,
            "q1": q1,
            "q3": q3,
            "outliers": [round(outlier, 1) for outlier in outliers]
        }, 200

    except AttributeError:
        return {"error": f"Column '{column_name}' does not exist in the LoanApproval table"}, 400
    except Exception as e:
        return {"error": str(e)}, 500


def generate_bar_chart(column_name):
    """
    Generates a bar chart (histogram) for a specified column in the LoanApproval table.

    Args:
        column_name (str): Name of the column to generate the chart for.

    Returns:
        Response: A PNG image of the bar chart or error message with HTTP status code.
    """
    try:
        column = getattr(LoanApproval, column_name, None)
        if column is None:
            return {"error": f"Column '{column_name}' does not exist in the LoanApproval table"}, 400

        data = [row[0] for row in LoanApproval.query.with_entities(column).all()]
        if not data:
            return {"error": f"No data available for column '{column_name}'"}, 400

        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=10, color='blue', edgecolor='black', alpha=0.7)
        plt.title(f"Distribution of {column_name}")
        plt.xlabel(column_name.capitalize())
        plt.ylabel("Frequency")

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        return Response(buffer, mimetype='image/png')

    except Exception as e:
        return {"error": str(e)}, 500


def generate_line_graph(column_name):
    """
    Generates a line graph for a specified column in the LoanApproval table.

    Args:
        column_name (str): Name of the column to generate the graph for.

    Returns:
        Response: A PNG image of the line graph or error message with HTTP status code.
    """
    try:
        column = getattr(LoanApproval, column_name, None)
        if column is None:
            return {"error": f"Column '{column_name}' does not exist in the LoanApproval table"}, 400

        data = [row[0] for row in LoanApproval.query.with_entities(column).all()]
        if not data:
            return {"error": f"No data available for column '{column_name}'"}, 400

        plt.figure(figsize=(10, 6))
        plt.plot(sorted(data), color='blue', alpha=0.7)
        plt.title(f"Line Graph of {column_name}")
        plt.xlabel("Index")
        plt.ylabel(column_name.capitalize())

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        return Response(buffer, mimetype='image/png')

    except Exception as e:
        return {"error": str(e)}, 500
