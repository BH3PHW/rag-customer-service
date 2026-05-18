"""
Agent Core with Function Calling Integration

Features:
1. Tool decision and execution
2. Multi-step reasoning (if needed)
3. Integration with LLM flow
4. Tool result formatting for LLM
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import json

from .tool_system import (
    get_tool_registry,
    get_tool_executor,
    ToolExecutionResult,
    ToolDefinition
)
from .built_in_tools import register_standard_tools


class AgentDecision:
    """Agent decision about whether to use tools"""
    
    def __init__(
        self,
        use_tools: bool,
        tools_to_call: List[Dict[str, Any]] = None,
        reasoning: str = ""
    ):
        self.use_tools = use_tools
        self.tools_to_call = tools_to_call or []
        self.reasoning = reasoning


class AgentExecutor:
    """
    Agent executor that manages function calling workflow
    
    Flow:
    1. Analyze user query
    2. Decide which tools to use
    3. Execute tools
    4. Format results for LLM
    5. Let LLM generate final answer
    """
    
    def __init__(self):
        self.registry = get_tool_registry()
        self.executor = get_tool_executor()
        
        # Register standard tools
        register_standard_tools()
    
    async def analyze_and_execute(
        self,
        query: str,
        conversation_history: List[Dict[str, Any]] = None,
        enterprise_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[bool, List[ToolExecutionResult], str]:
        """
        Analyze query and execute necessary tools
        
        Args:
            query: User query
            conversation_history: Previous conversation
            enterprise_id: Enterprise context
            user_id: User context
        
        Returns:
            Tuple of (tools_used, results, debug_info)
        """
        # First, use simple rule-based tool selection for demonstration
        # In production, this would be handled by LLM with function calling
        
        tools_used, tools_to_call = self._rule_based_tool_selection(query)
        
        if not tools_used:
            return False, [], "No tools needed for this query"
        
        results = []
        for tool_call in tools_to_call:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})
            
            result = await self.executor.execute(
                tool_name=tool_name,
                arguments=arguments,
                enterprise_id=enterprise_id,
                user_id=user_id
            )
            
            results.append({
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result
            })
        
        return True, results, f"Used {len(results)} tools"
    
    def _rule_based_tool_selection(self, query: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Simple rule-based tool selection (for demonstration)
        
        In production, this would use LLM function calling
        """
        query_lower = query.lower()
        tools_to_call = []
        
        # Order query detection
        if any(keyword in query_lower for keyword in ["订单", "发货", "物流", "ord-"]):
            # Try to extract order ID
            import re
            order_match = re.search(r'(ORD-\d+|[A-Z]{2,}-\d+)', query.upper())
            if order_match:
                tools_to_call.append({
                    "name": "query_order",
                    "arguments": {
                        "order_id": order_match.group(1)
                    }
                })
            else:
                tools_to_call.append({
                    "name": "query_order",
                    "arguments": {
                        "order_id": "ORD-1001"  # Default for demo
                    }
                })
        
        # Product query detection
        elif any(keyword in query_lower for keyword in ["产品", "价格", "库存", "规格", "多少钱", "有货吗"]):
            # Simple product name extraction
            product_name = query
            tools_to_call.append({
                "name": "query_product",
                "arguments": {
                    "product_name": product_name
                }
            })
        
        # FAQ lookup detection
        elif any(keyword in query_lower for keyword in ["如何", "怎么", "什么是", "FAQ", "常见问题"]):
            tools_to_call.append({
                "name": "lookup_faq",
                "arguments": {
                    "question": query
                }
            })
        
        # Human transfer detection
        elif any(keyword in query_lower for keyword in ["人工", "客服", "转人工"]):
            tools_to_call.append({
                "name": "transfer_human",
                "arguments": {
                    "reason": "用户请求人工客服",
                    "priority": "normal"
                }
            })
        
        return len(tools_to_call) > 0, tools_to_call
    
    def format_tool_results_for_llm(self, tool_results: List[Dict[str, Any]]) -> str:
        """
        Format tool execution results for LLM consumption
        
        Args:
            tool_results: Results from tool execution
        
        Returns:
            Formatted string for LLM prompt
        """
        if not tool_results:
            return ""
        
        sections = []
        sections.append("===== 工具调用结果 =====")
        
        for i, result in enumerate(tool_results, 1):
            tool_name = result.get("tool_name")
            execution_result = result.get("result")
            
            sections.append(f"\n【工具 {i}: {tool_name}】")
            
            if execution_result.success:
                sections.append("状态: ✅ 成功")
                if execution_result.data:
                    # Format data nicely
                    data_str = json.dumps(execution_result.data, ensure_ascii=False, indent=2)
                    sections.append(f"数据:\n{data_str}")
            else:
                sections.append(f"状态: ❌ 失败")
                sections.append(f"错误: {execution_result.error_message}")
            
            sections.append(f"执行耗时: {execution_result.execution_time_ms:.2f}ms")
        
        sections.append("\n===== 请根据以上工具调用结果回答用户问题 =====")
        
        return "\n".join(sections)
    
    def get_available_tools_description(self) -> str:
        """
        Get description of all available tools for LLM prompt
        
        Returns:
            Tools description string
        """
        tools = self.registry.list_tools()
        
        lines = ["===== 可用工具列表 ====="]
        
        for tool in tools:
            lines.append(f"\n【{tool.name}】")
            lines.append(f"类型: {tool.tool_type.value}")
            lines.append(f"描述: {tool.description}")
            
            param_lines = []
            for param in tool.parameters:
                req = " [必填]" if param.required else " [可选]"
                param_lines.append(f"  - {param.name} ({param.type}){req}: {param.description}")
            
            if param_lines:
                lines.append("参数:")
                lines.extend(param_lines)
        
        lines.append("\n======================")
        
        return "\n".join(lines)


# Singleton instance
_agent_executor: Optional[AgentExecutor] = None


def get_agent_executor() -> AgentExecutor:
    """Get singleton AgentExecutor"""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = AgentExecutor()
    return _agent_executor
