

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_sale = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Sale {self.id}>'


@app.before_first_request
def setup_db():
    db.create_all()


@app.route('/initialize', methods=['GET'])
def initialize_database():
    url = 'https://api.example.com/sales_data' 
    response = requests.get(url)
    
    if response.status_code == 200:
        sales_data = response.json()
        
        for sale in sales_data:
            date_of_sale = datetime.strptime(sale['dateOfSale'], '%Y-%m-%dT%H:%M:%S')
            new_sale = Sale(date_of_sale=date_of_sale, amount=sale['amount'])
            db.session.add(new_sale)
        
        db.session.commit()
        return 'Database initialized with seed data.'
    
    return 'Failed to fetch data from the third-party API.', 500


@app.route('/sales', methods=['GET'])
def get_sales_by_month():
    month = request.args.get('month')
    
    try:
        month_number = datetime.strptime(month, '%B').month
    except ValueError:
        return 'Invalid month format. Please provide month name like January, February, etc.', 400
    
    sales = Sale.query.filter(func.extract('month', Sale.date_of_sale) == month_number).all()
    
   
    sales_data = [{'date_of_sale': sale.date_of_sale.strftime('%Y-%m-%d %H:%M:%S'), 'amount': sale.amount} for sale in sales]
    
    return jsonify(sales_data)

if __name__ == '__main__':
    app.run(debug=True)
