# 露天拍賣 API 查詢專案

這是一個基於 Python Flask 和 React 的網頁應用程式，用於查詢露天拍賣的商品資訊。後端使用 `RutenAPIClient` 與露天拍賣 API 互動，前端提供簡單的介面讓使用者輸入商品 ID 或查詢商品列表。

## 功能
- 驗證 API 憑證是否有效
- 查詢單一商品詳情（透過商品 ID）
- 查詢商品列表（支援分頁）

## 專案結構
```
ruten-api-client/
├── backend/                # Flask 後端
│   ├── app.py              # 主應用程式
│   ├── ruten_client.py     # 露天 API 客戶端
│   ├── requirements.txt    # Python 依賴
│   └── Procfile           # Render 部署配置
├── frontend/               # React 前端
│   ├── public/
│   │   └── index.html      # HTML 入口
│   ├── src/
│   │   ├── App.jsx         # 主組件
│   │   ├── index.js        # React 入口
│   │   └── styles.css      # Tailwind CSS
│   ├── package.json        # Node.js 依賴
│   └── tailwind.config.js  # Tailwind 配置
├── README.md               # 說明文件
└── .env.example            # 環境變數範例
```

## 安裝與執行

### 後端
1. 進入 `backend` 目錄：
   ```bash
   cd backend
   ```
2. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
3. 複製 `.env.example` 為 `.env`，並填入您的 API 憑證：
   ```bash
   cp ../.env.example .env
   ```
4. 啟動 Flask 伺服器：
   ```bash
   python app.py
   ```

### 前端
1. 進入 `frontend` 目錄：
   ```bash
   cd frontend
   ```
2. 安裝依賴：
   ```bash
   npm install
   ```
3. 啟動開發伺服器：
   ```bash
   npm start
   ```

## 部署到 Render
1. 將專案推送到 GitHub。
2. 在 Render 建立一個新的 Web Service，選擇您的 GitHub 儲存庫。
3. 設定環境變數（參考 `.env.example`）。
4. 選擇 Python 環境，指定 `Procfile` 進行部署。

## 環境變數
參考 `.env.example`：
```
RUTEN_API_KEY=your_api_key
RUTEN_SECRET_KEY=your_secret_key
RUTEN_SALT_KEY=your_salt_key
PORT=5000
```

## 注意事項
- 確保您的 API 憑證有效。
- 前端目前使用 `http://localhost:5000` 作為後端 API 地址，部署時需更新為實際的後端 URL。
- 本專案僅支援查詢功能，不包含商品管理或修改功能。

## 授權
MIT License