import React, { useState } from 'react';
import './styles.css';

function App() {
  const [itemId, setItemId] = useState('');
  const [page, setPage] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/verify');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('驗證失敗：' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGetProduct = async () => {
    if (!itemId) {
      setError('請輸入商品 ID');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/api/product/${itemId}`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('查詢失敗：' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGetProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/api/products?page=${page}`);
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('查詢失敗：' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">露天拍賣 API 查詢</h1>
        
        <div className="mb-4">
          <button
            onClick={handleVerify}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
            disabled={loading}
          >
            {loading ? '驗證中...' : '驗證憑證'}
          </button>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700">商品 ID</label>
          <input
            type="text"
            value={itemId}
            onChange={(e) => setItemId(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="輸入商品 ID"
          />
          <button
            onClick={handleGetProduct}
            className="w-full bg-green-500 text-white py-2 px-4 rounded mt-2 hover:bg-green-600"
            disabled={loading}
          >
            {loading ? '查詢中...' : '查詢單一商品'}
          </button>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700">頁數</label>
          <input
            type="number"
            value={page}
            onChange={(e) => setPage(e.target.value)}
            className="w-full p-2 border rounded"
            min="1"
          />
          <button
            onClick={handleGetProducts}
            className="w-full bg-purple-500 text-white py-2 px-4 rounded mt-2 hover:bg-purple-600"
            disabled={loading}
          >
            {loading ? '查詢中...' : '查詢商品列表'}
          </button>
        </div>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        {result && (
          <div className="bg-gray-50 p-4 rounded">
            <h2 className="text-lg font-semibold mb-2">查詢結果</h2>
            <pre className="text-sm overflow-auto">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;