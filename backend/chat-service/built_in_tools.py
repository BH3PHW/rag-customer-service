"""
Built-in Tools for Agent System

Includes:
1. Order query tool
2. Knowledge base search tool
3. Product info tool
4. Customer service transfer tool
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from .tool_system import (
    ToolDefinition,
    ParameterDefinition,
    ToolType,
    get_tool_registry
)


# =============================================
# Example Data (for demonstration purposes)
# In production, this would be from your order-service
# =============================================
SAMPLE_ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "status": "shipped",
        "customer_name": "张三",
        "total_amount": 299.99,
        "items": [{"name": "智能音箱", "quantity": 1, "price": 299.99}],
        "shipping_info": {
            "address": "北京市朝阳区xxx街道",
            "tracking_number": "SF1234567890",
            "carrier": "顺丰速运"
        },
        "estimated_delivery": "2024-05-20"
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "status": "processing",
        "customer_name": "李四",
        "total_amount": 899.00,
        "items": [{"name": "无线蓝牙耳机", "quantity": 1, "price": 899.00}],
        "shipping_info": {
            "address": "上海市浦东新区xxx路",
            "tracking_number": None,
            "carrier": None
        },
        "estimated_delivery": "2024-05-22"
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "status": "delivered",
        "customer_name": "王五",
        "total_amount": 1599.00,
        "items": [{"name": "4K显示器", "quantity": 1, "price": 1599.00}],
        "shipping_info": {
            "address": "广州市天河区xxx街",
            "tracking_number": "YZ9876543210",
            "carrier": "韵达快递"
        },
        "estimated_delivery": "2024-05-15"
    }
}

SAMPLE_PRODUCTS = {
    "prod-001": {
        "id": "prod-001",
        "name": "智能音箱 Pro",
        "price": 299.99,
        "category": "智能家居",
        "description": "支持语音助手、音乐播放、智能家居控制",
        "stock": 500,
        "warranty": "1年质保"
    },
    "prod-002": {
        "id": "prod-002",
        "name": "无线蓝牙耳机 Ultra",
        "price": 899.00,
        "category": "音频设备",
        "description": "主动降噪、续航40小时、IPX7防水",
        "stock": 250,
        "warranty": "2年质保"
    }
}


# =============================================
# Tool 1: Order Query
# =============================================
def order_query_tool(
    order_id: str,
    enterprise_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询订单信息
    
    Args:
        order_id: 订单号
        enterprise_id: 企业ID（自动注入）
        user_id: 用户ID（自动注入）
    
    Returns:
        订单详细信息
    """
    if order_id in SAMPLE_ORDERS:
        order = SAMPLE_ORDERS[order_id]
        
        # Format status for better readability
        status_map = {
            "pending": "待处理",
            "processing": "处理中",
            "shipped": "已发货",
            "delivered": "已送达"
        }
        
        result = {
            "success": True,
            "order_id": order["order_id"],
            "status": status_map.get(order["status"], order["status"]),
            "status_english": order["status"],
            "customer_name": order["customer_name"],
            "total_amount": order["total_amount"],
            "items": order["items"],
            "estimated_delivery": order["estimated_delivery"]
        }
        
        if order["shipping_info"]["tracking_number"]:
            result["shipping"] = {
                "tracking_number": order["shipping_info"]["tracking_number"],
                "carrier": order["shipping_info"]["carrier"],
                "address": order["shipping_info"]["address"]
            }
        
        return result
    else:
        return {
            "success": False,
            "error": f"订单 '{order_id}' 不存在，请确认订单号是否正确",
            "available_orders": list(SAMPLE_ORDERS.keys())[:5]
        }


# =============================================
# Tool 2: Product Info Query
# =============================================
def product_info_tool(
    product_name: str,
    product_id: Optional[str] = None,
    enterprise_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询产品信息
    
    Args:
        product_name: 产品名称或关键词
        product_id: 产品ID（可选）
        enterprise_id: 企业ID
        user_id: 用户ID
    
    Returns:
        产品详细信息
    """
    results = []
    
    # Search by product ID first
    if product_id and product_id in SAMPLE_PRODUCTS:
        results.append(SAMPLE_PRODUCTS[product_id])
    
    # Search by name
    for product in SAMPLE_PRODUCTS.values():
        if (product_name.lower() in product["name"].lower() 
            or product_name.lower() in product["category"].lower()
            or product_name.lower() in product["description"].lower()):
            if product not in results:
                results.append(product)
    
    if not results:
        return {
            "success": False,
            "error": f"未找到与 '{product_name}' 相关的产品",
            "available_products": [p["name"] for p in SAMPLE_PRODUCTS.values()]
        }
    
    return {
        "success": True,
        "count": len(results),
        "products": results[:3]
    }


# =============================================
# Tool 3: Knowledge Base Search (Enhanced)
# =============================================
def kb_search_tool(
    query: str,
    knowledge_base_id: Optional[str] = None,
    top_k: int = 5,
    enterprise_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    搜索企业知识库
    
    Args:
        query: 搜索关键词
        knowledge_base_id: 指定知识库（可选）
        top_k: 返回结果数量
        enterprise_id: 企业ID
        user_id: 用户ID
    
    Returns:
        搜索结果
    """
    # In production, this would call knowledge-service API
    return {
        "success": True,
        "query": query,
        "top_k": top_k,
        "results": [
            {
                "title": f"关于{query}的常见问题",
                "content": f"这是关于{query}的详细说明文档，包含使用指南、注意事项等。",
                "relevance_score": 0.92,
                "source": "帮助中心"
            },
            {
                "title": f"{query}操作教程",
                "content": f"详细教程，教您如何使用{query}功能。",
                "relevance_score": 0.85,
                "source": "教程文档"
            }
        ]
    }


# =============================================
# Tool 4: Customer Service Transfer
# =============================================
def human_transfer_tool(
    reason: str = "用户请求转接",
    priority: str = "normal",
    enterprise_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    请求转接人工客服
    
    Args:
        reason: 转接原因
        priority: 优先级 (low/normal/high/urgent)
        enterprise_id: 企业ID
        user_id: 用户ID
    
    Returns:
        转接结果
    """
    # In production, this would trigger alert-service
    ticket_id = f"TKT-{int(datetime.utcnow().timestamp())}"
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "message": "已为您转接人工客服",
        "estimated_wait": "约2-5分钟",
        "priority": priority
    }


# =============================================
# Tool 5: FAQ Lookup
# =============================================
def faq_lookup_tool(
    question: str,
    category: Optional[str] = None,
    enterprise_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    查询常见问题
    
    Args:
        question: 用户问题
        category: 问题分类
        enterprise_id: 企业ID
        user_id: 用户ID
    
    Returns:
        FAQ匹配结果
    """
    # Sample FAQ database
    faqs = {
        "如何退货": {
            "answer": "退货流程：1. 登录账号 2. 找到订单 3. 点击申请退货 4. 填写原因并提交 5. 等待审核 6. 寄回商品。",
            "category": "售后",
            "related_links": ["https://example.com/returns"]
        },
        "如何退款": {
            "answer": "退款将在收到退货后的3-5个工作日内原路返回您的支付账户。",
            "category": "售后",
            "related_links": []
        },
        "发货时间": {
            "answer": "订单通常在24小时内发货，周末及节假日可能顺延。",
            "category": "配送",
            "related_links": []
        },
        "联系方式": {
            "answer": "客服电话：400-123-4567；工作时间：9:00-21:00；邮箱：support@example.com",
            "category": "联系",
            "related_links": []
        }
    }
    
    # Simple keyword matching
    matched_question = None
    for q in faqs:
        if any(keyword in question for keyword in q.split(' ')) or q in question:
            matched_question = q
            break
    
    if matched_question:
        return {
            "success": True,
            "question": matched_question,
            "answer": faqs[matched_question]["answer"],
            "category": faqs[matched_question]["category"],
            "related_links": faqs[matched_question]["related_links"]
        }
    else:
        return {
            "success": False,
            "error": "未找到匹配的FAQ",
            "suggested_questions": list(faqs.keys())
        }


# =============================================
# Register all tools
# =============================================
def register_standard_tools() -> None:
    """Register all standard built-in tools"""
    registry = get_tool_registry()
    
    # 1. Order Query Tool
    registry.register(ToolDefinition(
        name="query_order",
        description="查询订单状态、物流信息、订单详情等",
        tool_type=ToolType.BUSINESS_ACTION,
        parameters=[
            ParameterDefinition(
                name="order_id",
                type="string",
                description="订单号，例如 ORD-1001",
                required=True
            )
        ],
        handler=order_query_tool
    ))
    
    # 2. Product Info Tool
    registry.register(ToolDefinition(
        name="query_product",
        description="查询产品信息、价格、库存、规格等",
        tool_type=ToolType.DATA_QUERY,
        parameters=[
            ParameterDefinition(
                name="product_name",
                type="string",
                description="产品名称或关键词",
                required=True
            ),
            ParameterDefinition(
                name="product_id",
                type="string",
                description="产品ID（可选）",
                required=False
            )
        ],
        handler=product_info_tool
    ))
    
    # 3. Knowledge Base Search Tool
    registry.register(ToolDefinition(
        name="search_kb",
        description="搜索企业知识库中的文档和帮助内容",
        tool_type=ToolType.KNOWLEDGE_RETRIEVAL,
        parameters=[
            ParameterDefinition(
                name="query",
                type="string",
                description="搜索关键词或问题",
                required=True
            ),
            ParameterDefinition(
                name="top_k",
                type="integer",
                description="返回结果数量，默认5",
                required=False,
                default=5
            )
        ],
        handler=kb_search_tool
    ))
    
    # 4. Human Transfer Tool
    registry.register(ToolDefinition(
        name="transfer_human",
        description="为用户转接人工客服",
        tool_type=ToolType.BUSINESS_ACTION,
        parameters=[
            ParameterDefinition(
                name="reason",
                type="string",
                description="转接原因（可选）",
                required=False,
                default="用户请求转接"
            ),
            ParameterDefinition(
                name="priority",
                type="string",
                description="优先级",
                required=False,
                default="normal",
                enum=["low", "normal", "high", "urgent"]
            )
        ],
        handler=human_transfer_tool
    ))
    
    # 5. FAQ Lookup Tool
    registry.register(ToolDefinition(
        name="lookup_faq",
        description="查询常见问题库",
        tool_type=ToolType.KNOWLEDGE_RETRIEVAL,
        parameters=[
            ParameterDefinition(
                name="question",
                type="string",
                description="用户问题",
                required=True
            )
        ],
        handler=faq_lookup_tool
    ))


# Initialize and register tools on module load
register_standard_tools()
