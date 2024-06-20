from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ProductTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    date_of_transaction = db.Column(db.DateTime, nullable=False)

@app.before_first_request
def setup_db():
    db.create_all()

@app.route('/transactions', methods=['GET'])
def get_transactions():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = ProductTransaction.query

    if search:
        search = f'%{search}%'
        query = query.filter(
            or_(
                ProductTransaction.title.ilike(search),
                ProductTransaction.description.ilike(search),
                ProductTransaction.price.ilike(search)
            )
        )

    transactions = query.paginate(page=page, per_page=per_page, error_out=False)

    data = [
        {
            'id': transaction.id,
            'title': transaction.title,
            'description': transaction.description,
            'price': transaction.price,
            'date_of_transaction': transaction.date_of_transaction.strftime('%Y-%m-%d %H:%M:%S')
        } for transaction in transactions.items
    ]

    response = {
        'total': transactions.total,
        'pages': transactions.pages,
        'page': transactions.page,
        'per_page': transactions.per_page,
        'data': data
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
