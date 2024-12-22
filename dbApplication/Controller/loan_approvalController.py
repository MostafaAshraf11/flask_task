from flask import Response, request, jsonify
import pandas as pd
import os
from Models.loan_models import LoanApproval
from Models.dbModel import db
from sqlalchemy import func, or_, and_
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Use the non-GUI backend
import matplotlib.pyplot as plt
import io
import base64



UPLOAD_FOLDER = 'uploads'

# Create uploads folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def upload_csv(file):
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if not file.filename.endswith('.csv'):
        return {'error': 'Invalid file format, please upload a CSV file'}, 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Read the CSV file
        data = pd.read_csv(filepath)

        # Validate required columns
        required_columns = ['loan_id', 'income', 'loan_amount', 'credit_score', 'loan_status', 'asset_value']
        for col in required_columns:
            if col not in data.columns:
                return {'error': f'Missing required column: {col}'}, 400

        # Clean the data:
        # Strip spaces from column values (for text columns)
        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Drop rows where any required column is empty
        data.dropna(subset=required_columns, inplace=True)

        # Round float values to the first decimal place for relevant columns
        float_columns = ['income', 'loan_amount', 'credit_score', 'asset_value']
        data[float_columns] = data[float_columns].round(1)

        # Insert rows into the database
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
    required_fields = ['income', 'loan_amount', 'credit_score', 'asset_value', 'loan_status']
    for field in required_fields:
        if field not in data:
            return {'error': f'Missing required field: {field}'}, 400

    # Create a new LoanApproval object
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
    loan = LoanApproval.query.get_or_404(loan_id)
    db.session.delete(loan)
    db.session.commit()
    return {'message': 'Loan approval deleted'}

def apply_filters(query, filters):
    """
    Apply filters to the query.
    """
    filter_conditions = []
    for condition in filters:
        column = condition.get('column')
        value = condition.get('value')
        operator = condition.get('operator', 'equals')

        if column not in ['income', 'loan_amount', 'credit_score', 'loan_status', 'asset_value']:
            return {"error": f"Unsupported column: {column}"}, 400

        if operator == 'equals':
            if column == 'income':
                filter_conditions.append(LoanApproval.income == value)
            elif column == 'loan_amount':
                filter_conditions.append(LoanApproval.loan_amount == value)
            elif column == 'credit_score':
                filter_conditions.append(LoanApproval.credit_score == value)
            elif column == 'loan_status':
                filter_conditions.append(LoanApproval.loan_status == value)
            elif column == 'asset_value':
                filter_conditions.append(LoanApproval.asset_value == value)
        
        elif operator == 'greater_than':
            if column == 'income':
                filter_conditions.append(LoanApproval.income > value)
            elif column == 'loan_amount':
                filter_conditions.append(LoanApproval.loan_amount > value)
            elif column == 'credit_score':
                filter_conditions.append(LoanApproval.credit_score > value)
            elif column == 'asset_value':
                filter_conditions.append(LoanApproval.asset_value > value)
        
        elif operator == 'less_than':
            if column == 'income':
                filter_conditions.append(LoanApproval.income < value)
            elif column == 'loan_amount':
                filter_conditions.append(LoanApproval.loan_amount < value)
            elif column == 'credit_score':
                filter_conditions.append(LoanApproval.credit_score < value)
            elif column == 'asset_value':
                filter_conditions.append(LoanApproval.asset_value < value)
        
        else:
            return {"error": f"Unsupported operator: {operator}"}, 400

    if filter_conditions:
        query = query.filter(and_(*filter_conditions))
    
    return query


def calculate_aggregate(query, aggregate_type, field):
    """
    Perform the aggregation based on the specified type.
    """
    if aggregate_type == 'sum':
        result = db.session.query(func.sum(getattr(LoanApproval, field))).scalar()
    elif aggregate_type == 'avg':
        result = db.session.query(func.avg(getattr(LoanApproval, field))).scalar()
    elif aggregate_type == 'count':
        result = db.session.query(func.count()).scalar()
    elif aggregate_type == 'max':
        result = db.session.query(func.max(getattr(LoanApproval, field))).scalar()
    elif aggregate_type == 'min':
        result = db.session.query(func.min(getattr(LoanApproval, field))).scalar()
    else:
        return {"error": "Unsupported aggregate type"}, 400
    
    return result


def filter_and_aggregate(data):
    # Retrieve filters, aggregate type, field, and pagination parameters from the request data
    filters = data.get('filters', [])
    aggregate_type = data.get('aggregate_type')
    field = data.get('field')
    page = data.get('page', 1)
    per_page = data.get('per_page', 20)
    
    # Start with the base query
    query = LoanApproval.query

    # Apply filters if present
    if filters:
        query = apply_filters(query, filters)

    # If aggregate is requested, calculate the aggregate
    if aggregate_type and field:
        aggregate_result = calculate_aggregate(query, aggregate_type, field)
        return {
            "aggregate_type": aggregate_type,
            "field": field,
            "result": aggregate_result
        }, 200

    # Apply pagination to the query
    pagination_query = query.paginate(page=page, per_page=per_page, error_out=False)
    filtered_loans = pagination_query.items

    # Format the response
    loan_list = [loan.to_dict() for loan in filtered_loans]
    
    return {
        "filtered_loans": loan_list,
        "total": pagination_query.total,
        "pages": pagination_query.pages,
        "current_page": pagination_query.page,
        "per_page": pagination_query.per_page
    }, 200


def compute_advanced_stats(column_name):
    try:
        # Fetch data from the specified column in the database
        rows = db.session.query(getattr(LoanApproval, column_name)).all()

        # Flatten the list of tuples and filter out None values
        column_values = [row[0] for row in rows if row[0] is not None]

        # Ensure there are enough data points for statistical calculations
        if len(column_values) < 2:
            return {"error": "Not enough data points to compute statistics"}, 400

        # Remove NaN values and convert to a numpy array
        column_values = np.array(column_values)
        column_values = column_values[~np.isnan(column_values)]

        # Perform calculations
        mean = round(np.mean(column_values), 1)
        median = round(np.median(column_values), 1)
        mode_result = stats.mode(column_values, keepdims=True)  # Updated to ensure compatibility
        mode = round(mode_result.mode[0], 1) if mode_result.count[0] > 0 else None  # Safeguard against empty mode
        q1 = round(np.percentile(column_values, 25), 1)
        q3 = round(np.percentile(column_values, 75), 1)
        iqr = q3 - q1

        # Calculate outliers
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = column_values[(column_values < lower_bound) | (column_values > upper_bound)]

        return {
            "mean": mean,
            "median": median,
            "mode": mode,
            "q1": q1,
            "q3": q3,
            "outliers": [round(outlier, 1) for outlier in outliers]  # Round outliers to one decimal point
        }, 200

    except AttributeError:
        return {"error": f"Column '{column_name}' does not exist in the LoanApproval table"}, 400
    except Exception as e:
        return {"error": str(e)}, 500

# Function to generate Bar Chart (Histogram)
def generate_bar_chart(column_name):
    try:
        # Dynamically fetch the column object from the LoanApproval table
        column = getattr(LoanApproval, column_name, None)
        if column is None:
            return {"error": f"Column '{column_name}' does not exist in the LoanApproval table"}, 400

        # Fetch data for the specified column
        data = [row[0] for row in LoanApproval.query.with_entities(column).all()]

        # Check if data is empty
        if not data:
            return {"error": f"No data available for column '{column_name}'"}, 400

        # Generate a simple bar chart using matplotlib
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=10, color='blue', edgecolor='black', alpha=0.7)
        plt.title(f"Distribution of {column_name}")
        plt.xlabel(column_name.capitalize())
        plt.ylabel("Frequency")

        # Save the bar chart to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        # Return the image as a response directly to Postman
        return Response(buffer, mimetype='image/png')

    except Exception as e:
        return {"error": str(e)}, 500


# Function to generate Line Graph
def generate_line_graph(column_name):
    try:
        # Dynamically fetch the column object from the LoanApproval table
        column = getattr(LoanApproval, column_name, None)
        if column is None:
            return {"error": f"Column '{column_name}' does not exist in the LoanApproval table"}, 400

        # Fetch data for the specified column
        data = [row[0] for row in LoanApproval.query.with_entities(column).all()]

        # Check if data is empty
        if not data:
            return {"error": f"No data available for column '{column_name}'"}, 400

        # Generate a line graph using matplotlib
        plt.figure(figsize=(10, 6))
        plt.plot(sorted(data), color='blue', alpha=0.7)
        plt.title(f"Line Graph of {column_name}")
        plt.xlabel("Index")
        plt.ylabel(column_name.capitalize())

        # Save the line graph to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        # Return the image as a response directly to Postman
        return Response(buffer, mimetype='image/png')

    except Exception as e:
        return {"error": str(e)}, 500