from flask import Flask, request, jsonify
from flask_cors import CORS
from ruten_client import RutenAPIClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # 允許跨域請求

try:
    client = RutenAPIClient(
        api_key=os.getenv('RUTEN_API_KEY'),
        secret_key=os.getenv('RUTEN_SECRET_KEY'),
        salt_key=os.getenv('RUTEN_SALT_KEY')
    )
except ValueError as e:
    print(f"初始化錯誤：{e}")
    exit(1)

@app.route('/api/verify', methods=['GET'])
def verify_credentials():
    result = client.verify_credentials()
    return jsonify(result)

@app.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', default=1, type=int)
    page_size = request.args.get('page_size', default=30, type=int)
    result = client.get_products(page=page, page_size=page_size)
    return jsonify(result)

@app.route('/api/product/<item_id>', methods=['GET'])
def get_product(item_id):
    result = client.get_product(item_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))