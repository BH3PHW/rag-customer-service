"""
Tool Definitions and Registration System

Features:
1. Function Calling tool definitions
2. Tool registration mechanism
3. Tool execution engine
4. Parameter validation and type checking
"""
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, ValidationError
import json
import inspect


class ToolType(Enum):
    """Tool types"""
    DATA_QUERY = "data_query"        # Data query tools
    BUSINESS_ACTION = "business_action"  # Business operation tools
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"  # Knowledge retrieval
    UTILITY = "utility"             # Utility tools


@dataclass
class ParameterDefinition:
    """Parameter definition for a tool"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: List[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "type": self.type,
            "description": self.description,
        }
        if self.enum:
            result["enum"] = self.enum
        if self.default is not None:
            result["default"] = self.default
        return result


@dataclass
class ToolDefinition:
    """Complete tool definition"""
    name: str
    description: str
    tool_type: ToolType
    parameters: List[ParameterDefinition]
    handler: Callable
    requires_auth: bool = True
    enterprise_scoped: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format"""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_dict()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tool_type": self.tool_type.value,
            "requires_auth": self.requires_auth,
            "enterprise_scoped": self.enterprise_scoped,
            "parameters": [p.__dict__ for p in self.parameters]
        }


@dataclass
class ToolExecutionResult:
    """Result of tool execution"""
    success: bool
    data: Any = None
    error_message: str = None
    execution_time_ms: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error_message": self.error_message,
            "execution_time_ms": round(self.execution_time_ms, 2)
        }


class ToolRegistry:
    """
    Central registry for all available tools
    
    Features:
    - Tool registration and discovery
    - Tool lookup by name/type
    - Tool metadata management
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._tools_by_type: Dict[ToolType, List[ToolDefinition]] = {}
    
    def register(self, tool: ToolDefinition) -> None:
        """
        Register a new tool
        
        Args:
            tool: ToolDefinition to register
        """
        self._tools[tool.name] = tool
        
        if tool.tool_type not in self._tools_by_type:
            self._tools_by_type[tool.tool_type] = []
        
        self._tools_by_type[tool.tool_type].append(tool)
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """
        Get tool by name
        
        Args:
            name: Tool name
        
        Returns:
            ToolDefinition or None if not found
        """
        return self._tools.get(name)
    
    def list_tools(self, tool_type: Optional[ToolType] = None) -> List[ToolDefinition]:
        """
        List registered tools
        
        Args:
            tool_type: Optional filter by tool type
        
        Returns:
            List of ToolDefinition objects
        """
        if tool_type:
            return self._tools_by_type.get(tool_type, [])
        return list(self._tools.values())
    
    def get_openai_format_tools(self, tool_type: Optional[ToolType] = None) -> List[Dict[str, Any]]:
        """
        Get tools in OpenAI function calling format
        
        Args:
            tool_type: Optional filter by tool type
        
        Returns:
            List of tool definitions in OpenAI format
        """
        tools = self.list_tools(tool_type)
        return [t.to_openai_format() for t in tools]
    
    def exists(self, name: str) -> bool:
        """Check if tool exists"""
        return name in self._tools


class ToolExecutor:
    """
    Tool execution engine
    
    Handles:
    - Parameter validation
    - Tool invocation
    - Result handling
    - Error recovery
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    async def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        enterprise_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ToolExecutionResult:
        """
        Execute a tool
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            enterprise_id: Enterprise context
            user_id: User context
        
        Returns:
            ToolExecutionResult
        """
        import time
        start_time = time.time()
        
        try:
            # Get tool definition
            tool = self.registry.get(tool_name)
            if not tool:
                return ToolExecutionResult(
                    success=False,
                    error_message=f"Tool '{tool_name}' not found"
                )
            
            # Validate enterprise scope if required
            if tool.enterprise_scoped and not enterprise_id:
                return ToolExecutionResult(
                    success=False,
                    error_message="Enterprise context required for this tool"
                )
            
            # Validate and prepare arguments
            validated_args = self._validate_arguments(tool, arguments)
            
            # Add context args
            if tool.enterprise_scoped:
                validated_args["enterprise_id"] = enterprise_id
            if tool.requires_auth:
                validated_args["user_id"] = user_id
            
            # Execute handler
            if inspect.iscoroutinefunction(tool.handler):
                result = await tool.handler(**validated_args)
            else:
                result = tool.handler(**validated_args)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolExecutionResult(
                success=True,
                data=result,
                execution_time_ms=execution_time
            )
            
        except ValidationError as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolExecutionResult(
                success=False,
                error_message=f"Parameter validation failed: {str(e)}",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolExecutionResult(
                success=False,
                error_message=f"Tool execution failed: {str(e)}",
                execution_time_ms=execution_time
            )
    
    def _validate_arguments(
        self,
        tool: ToolDefinition,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and prepare arguments
        
        Args:
            tool: Tool definition
            arguments: Raw arguments
        
        Returns:
            Validated arguments
        """
        validated = {}
        
        for param in tool.parameters:
            if param.name in arguments:
                validated[param.name] = arguments[param.name]
            elif param.required:
                raise ValueError(f"Required parameter '{param.name}' missing")
            elif param.default is not None:
                validated[param.name] = param.default
        
        return validated


# Singleton instances
_tool_registry: Optional[ToolRegistry] = None
_tool_executor: Optional[ToolExecutor] = None


def get_tool_registry() -> ToolRegistry:
    """Get singleton ToolRegistry"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def get_tool_executor() -> ToolExecutor:
    """Get singleton ToolExecutor"""
    global _tool_executor
    registry = get_tool_registry()
    if _tool_executor is None:
        _tool_executor = ToolExecutor(registry)
    return _tool_executor
