from Models.dbModel import db

class LoanApproval(db.Model):
    __tablename__ = 'loan_approval'

    loan_id = db.Column(db.Integer, primary_key=True)  # Primary key
    income = db.Column(db.Float, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    loan_status = db.Column(db.String(20), nullable=False)
    asset_value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<LoanApproval loan_id={self.loan_id} loan_status={self.loan_status}>"
    
    def to_dict(self):
        return {
            "loan_id": self.loan_id,
            "income": self.income,
            "loan_amount": self.loan_amount,
            "asset_value": self.asset_value,
            "loan_status": self.loan_status,
            "credit_score": self.credit_score
        }
