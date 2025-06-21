from flask import Flask, jsonify
from ruten_client import RutenAPIClient

app = Flask(__name__)

# 使用提供的憑證初始化 RutenAPIClient
client = RutenAPIClient(
    api_key="dsu6tjuf8dvc8xdc7uajk6da8agdxxhv",
    secret_key="wu68zrcikttdjnieqv3pyydixmxbjady",
    salt_key="dma29ifwy56i"
)

@app.route("/test", methods=["GET"])
def test_ruten_api():
    try:
        # 測試 get_products 端點
        result = client.get_products(page=1, page_size=10)
        if result.get("status") == "success":
            return jsonify({
                "success": True,
                "message": "成功連接到 Ruten API",
                "data": result.get("data", [])
            })
        else:
            return jsonify({
                "success": False,
                "message": f"API 調用失敗：{result.get('error_msg', '未知錯誤')}",
                "error_code": result.get("error_code", "N/A")
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"連接到 Ruten API 時出錯：{str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)