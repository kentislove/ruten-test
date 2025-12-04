import os
import logging
import hmac
import hashlib
import json
import time
import requests
from urllib.parse import urljoin, urlencode
from typing import Dict, Any
from zoneinfo import ZoneInfo
from datetime import datetime

class RutenAPIClient:
    """露天拍賣 API 客戶端 - 僅限查詢商品相關功能"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, salt_key: str = None):
        self.base_url = "https://partner.ruten.com.tw"
        self.api_key = api_key or os.getenv('RUTEN_API_KEY')
        self.secret_key = secret_key or os.getenv('RUTEN_SECRET_KEY')
        self.salt_key = salt_key or os.getenv('RUTEN_SALT_KEY')
        
        if not all([self.api_key, self.secret_key, self.salt_key]):
            raise ValueError("缺少必要的憑證：RUTEN_API_KEY、RUTEN_SECRET_KEY、RUTEN_SALT_KEY")
        
        # 設置日誌
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        logging.debug(f"初始化完成：api_key={self.api_key[:8]}..., secret_key={self.secret_key[:8]}..., salt_key={self.salt_key}")
        
        # 檢查本地系統時間
        self._check_system_time()
    
    def _check_system_time(self) -> None:
        """檢查本地系統時間是否合理同步"""
        try:
            response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Taipei', timeout=5)
            if response.status_code == 200:
                server_time = datetime.fromisoformat(response.json()['datetime'].replace('Z', '+00:00'))
                local_time = datetime.utcnow()
                time_diff = abs((server_time - local_time).total_seconds())
                if time_diff > 300:  # 5 分鐘的時間差
                    logging.warning(f"本地系統時間可能未同步。與伺服器時間差異：{time_diff} 秒")
                else:
                    logging.debug(f"本地系統時間已同步。與伺服器時間差異：{time_diff} 秒")
        except Exception as e:
            logging.warning(f"無法驗證系統時間：{str(e)}")
    
    def _generate_signature(self, url_path: str, request_body: str = "", timestamp: str = None, params: Dict[str, Any] = None) -> tuple:
        """生成 HMAC-SHA256 簽章"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        if request_body != '':
            request_body_string = json.dumps(request_body, separators=(',', ':'))  # 確保格式一致
        else:
            request_body_string = ''

        sign_string = f"{self.salt_key}{url_path}{request_body_string}{timestamp}"
        logging.debug(f"簽章字串：{sign_string}, 時間戳記：{timestamp}")
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature, timestamp
    
    def _get_headers(self, url_path: str, request_body: str = "", content_type: str = "application/json", params: Dict[str, Any] = None) -> Dict[str, str]:
        """生成請求標頭"""
        now = datetime.now(ZoneInfo("Asia/Taipei"))
        timestamp = int(now.timestamp())
        local_timestamp = str(timestamp)
        signature, timestamp = self._generate_signature(url_path, request_body, timestamp=local_timestamp)

        logging.debug(f"生成標頭：簽章={signature[:8]}..., 時間戳記={timestamp}")
        
        return {
            'User-Agent': 'ruten-api',
            'Content-Type': content_type,
            'X-RT-Key': self.api_key,
            'X-RT-Timestamp': str(timestamp),
            'X-RT-Authorization': signature
        }
    
    def _make_request(self, method: str, endpoint: str, request_body: str="", params: Dict[str, Any] = None) -> Dict[str, Any]:
        """發送 API 請求"""
        now = datetime.now(ZoneInfo("Asia/Taipei"))
        timestamp = int(now.timestamp())
        local_timestamp = str(timestamp)
        
        full_url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(url_path=endpoint, request_body=request_body)
        logging.debug(f"Ruten API 請求：{method} {full_url}, 標頭={headers}, 參數={params}, 本地時間戳記={local_timestamp}")
        
        try:
            response = requests.get(full_url, headers=headers, timeout=30)
            server_time = response.headers.get('Date', '未提供')
            cloudflare_ray_id = response.headers.get('CF-Ray', '未提供')
            logging.debug(f"伺服器時間（來自回應標頭）：{server_time}, Cloudflare Ray ID：{cloudflare_ray_id}")
            response.raise_for_status()
            result = response.json()
            logging.debug(f"Ruten API 回應：狀態碼={response.status_code}, 主體={result}, 伺服器時間={server_time}")
            if result.get('status') == 'success':
                logging.info(f"API 呼叫成功：端點={endpoint}, 狀態={result.get('status')}")
            else:
                logging.error(f"API 呼叫失敗：端點={endpoint}, 狀態={result.get('status')}, 錯誤碼={result.get('error_code')}, 錯誤訊息={result.get('error_msg')}, 伺服器時間={server_time}, Cloudflare Ray ID={cloudflare_ray_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            server_time = response.headers.get('Date', '未提供') if 'response' in locals() else '不可用'
            cloudflare_ray_id = response.headers.get('CF-Ray', '未提供') if 'response' in locals() else '不可用'
            error_response = {
                'error': True,
                'message': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'response_body': getattr(e.response, 'text', '無回應主體') if hasattr(e, 'response') else '無回應'
            }
            try:
                if hasattr(e, 'response') and e.response:
                    content_type = e.response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        error_body = e.response.json()
                        error_response['error_code'] = error_body.get('error_code', 'N/A')
                        error_response['error_msg'] = error_body.get('error_msg', 'N/A')
                    else:
                        error_response['error_code'] = 'N/A'
                        error_response['error_msg'] = '非 JSON 回應（可能是 HTML）'
                    logging.error(f"Ruten API 錯誤：端點={endpoint}, 狀態碼={error_response['status_code']}, 錯誤碼={error_response['error_code']}, 錯誤訊息={error_response['error_msg']}, 回應主體={error_response['response_body'][:500]}..., 伺服器時間={server_time}, 本地時間戳記={local_timestamp}, Cloudflare Ray ID={cloudflare_ray_id}")
                else:
                    logging.error(f"Ruten API 錯誤：端點={endpoint}, 訊息={error_response['message']}, 回應主體={error_response['response_body'][:500]}..., 伺服器時間={server_time}, 本地時間戳記={local_timestamp}, Cloudflare Ray ID={cloudflare_ray_id}")
            except (ValueError, AttributeError):
                logging.error(f"Ruten API 錯誤：端點={endpoint}, 狀態碼={error_response['status_code']}, 訊息={error_response['message']}, 回應主體={error_response['response_body'][:500]}..., 伺服器時間={server_time}, 本地時間戳記={local_timestamp}, Cloudflare Ray ID={cloudflare_ray_id}")
            return error_response
    
    def get_products(self, page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """查詢商品列表"""
        api_path = "/api/v1/product/list"
        params = {
            'status': 'all',
            'offset': page, 
            'limit':page_size
        }

        endpoint = f"{api_path}?{urlencode(params)}"
        result = self._make_request('GET', endpoint)
        if result.get('status') == 'success' and not result.get('data'):
            logging.info(f"未找到商品：頁數={page}, 每頁數量={page_size}")
        return result
    
    def get_product(self, item_id: str) -> Dict[str, Any]:
        """取得商品資訊"""
        result = self._make_request('GET', f'/api/v1/product/item/{item_id}')
        if result.get('status') == 'success' and not result.get('data'):
            logging.info(f"未找到商品：商品ID={item_id}")
        return result
    
    def verify_credentials(self) -> Dict[str, Any]:
        """驗證 API 憑證"""
        try:
            result = self.get_products()
            logging.debug(f"驗證憑證回應：{result}")
            if 'error' in result:
                logging.error(f"憑證驗證失敗：狀態碼={result.get('status_code')}, 訊息={result.get('message', '未知錯誤')}, 錯誤碼={result.get('error_code', 'N/A')}, 錯誤訊息={result.get('error_msg', 'N/A')}")
                return {'valid': False, 'message': f"API 錯誤：{result.get('error_msg', result.get('message', '未知錯誤'))}"}
            return {'valid': True, 'message': '憑證有效'}
        except Exception as e:
            logging.error(f"驗證憑證錯誤：{str(e)}")
            return {'valid': False, 'message': str(e)}