"""
Agent 协议适配器

支持多种协议：HTTP, gRPC, WebSocket 等
统一调用接口
"""

import httpx
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from loguru import logger


class ProtocolAdapter(ABC):
    """协议适配器基类"""
    
    @abstractmethod
    async def invoke(self, endpoint: str, action: str, input_data: Dict, 
                     auth: Optional[Dict] = None) -> Dict:
        """
        调用 Agent
        
        Args:
            endpoint: 端点地址
            action: 动作 (chat, query, execute 等)
            input_data: 输入数据
            auth: 认证信息
            
        Returns:
            调用结果
        """
        pass
    
    @abstractmethod
    async def health_check(self, endpoint: str, auth: Optional[Dict] = None) -> bool:
        """
        健康检查
        
        Args:
            endpoint: 端点地址
            auth: 认证信息
            
        Returns:
            是否健康
        """
        pass


class HTTPAdapter(ProtocolAdapter):
    """HTTP 协议适配器"""
    
    def __init__(self, timeout: int = 30):
        """
        初始化 HTTP 适配器
        
        Args:
            timeout: 超时时间 (秒)
        """
        self.timeout = timeout
        self.logger = logger
    
    async def invoke(self, endpoint: str, action: str, input_data: Dict,
                     auth: Optional[Dict] = None) -> Dict:
        """
        HTTP 调用 Agent
        
        Args:
            endpoint: API 端点
            action: 动作
            input_data: 输入数据
            auth: 认证信息 {type: "bearer"|"basic", value: "token"}
            
        Returns:
            调用结果
        """
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 构建请求头
                headers = {"Content-Type": "application/json"}
                
                if auth:
                    auth_type = auth.get("type", "none")
                    auth_value = auth.get("value")
                    
                    if auth_type == "bearer" and auth_value:
                        headers["Authorization"] = f"Bearer {auth_value}"
                    elif auth_type == "basic" and auth_value:
                        headers["Authorization"] = f"Basic {auth_value}"
                
                # 构建请求体
                payload = {
                    "action": action,
                    "input": input_data,
                    "timestamp": start_time.isoformat()
                }
                
                self.logger.info(f"HTTP 调用：{endpoint}, action: {action}")
                
                # 发送请求
                response = await client.post(endpoint, headers=headers, json=payload)
                
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                # 解析响应
                if response.status_code < 400:
                    result = response.json()
                    self.logger.info(
                        f"HTTP 调用成功：{endpoint}, "
                        f"耗时：{duration:.2f}s, "
                        f"状态码：{response.status_code}"
                    )
                    
                    return {
                        "success": True,
                        "data": result,
                        "status_code": response.status_code,
                        "duration": duration,
                        "timestamp": end_time.isoformat()
                    }
                else:
                    self.logger.error(
                        f"HTTP 调用失败：{endpoint}, "
                        f"状态码：{response.status_code}, "
                        f"响应：{response.text}"
                    )
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "message": response.text,
                        "status_code": response.status_code,
                        "duration": duration,
                        "timestamp": end_time.isoformat()
                    }
                    
        except httpx.TimeoutException as e:
            end_time = datetime.utcnow()
            self.logger.error(f"HTTP 调用超时：{endpoint}, 超时：{self.timeout}s")
            
            return {
                "success": False,
                "error": "timeout",
                "message": f"请求超时 ({self.timeout}s)",
                "duration": self.timeout,
                "timestamp": end_time.isoformat()
            }
            
        except httpx.NetworkError as e:
            end_time = datetime.utcnow()
            self.logger.error(f"HTTP 网络错误：{endpoint}, 错误：{str(e)}")
            
            return {
                "success": False,
                "error": "network_error",
                "message": str(e),
                "duration": 0,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            end_time = datetime.utcnow()
            self.logger.error(f"HTTP 调用异常：{endpoint}, 错误：{str(e)}")
            
            return {
                "success": False,
                "error": "unknown_error",
                "message": str(e),
                "duration": 0,
                "timestamp": end_time.isoformat()
            }
    
    async def health_check(self, endpoint: str, auth: Optional[Dict] = None) -> bool:
        """
        HTTP 健康检查
        
        发送 GET 请求检查端点是否可达
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {}
                
                if auth:
                    auth_type = auth.get("type", "none")
                    auth_value = auth.get("value")
                    
                    if auth_type == "bearer" and auth_value:
                        headers["Authorization"] = f"Bearer {auth_value}"
                    elif auth_type == "basic" and auth_value:
                        headers["Authorization"] = f"Basic {auth_value}"
                
                response = await client.get(endpoint, headers=headers)
                return response.status_code < 400
                
        except Exception:
            return False


class WebSocketAdapter(ProtocolAdapter):
    """WebSocket 协议适配器 (待实现)"""
    
    async def invoke(self, endpoint: str, action: str, input_data: Dict,
                     auth: Optional[Dict] = None) -> Dict:
        # TODO: 实现 WebSocket 调用
        return {
            "success": False,
            "error": "not_implemented",
            "message": "WebSocket 适配器尚未实现"
        }
    
    async def health_check(self, endpoint: str, auth: Optional[Dict] = None) -> bool:
        return False


class GRPCAdapter(ProtocolAdapter):
    """gRPC 协议适配器 (待实现)"""
    
    async def invoke(self, endpoint: str, action: str, input_data: Dict,
                     auth: Optional[Dict] = None) -> Dict:
        # TODO: 实现 gRPC 调用
        return {
            "success": False,
            "error": "not_implemented",
            "message": "gRPC 适配器尚未实现"
        }
    
    async def health_check(self, endpoint: str, auth: Optional[Dict] = None) -> bool:
        return False


# 适配器工厂
def get_adapter(protocol: str) -> ProtocolAdapter:
    """
    获取协议适配器
    
    Args:
        protocol: 协议类型 (http, https, ws, wss, grpc)
        
    Returns:
        协议适配器实例
    """
    protocol = protocol.lower()
    
    if protocol in ["http", "https"]:
        return HTTPAdapter()
    elif protocol in ["ws", "wss"]:
        return WebSocketAdapter()
    elif protocol == "grpc":
        return GRPCAdapter()
    else:
        # 默认使用 HTTP
        return HTTPAdapter()
