"""
Context Window Management with Intelligent Compression

Features:
1. Conversation state management with Redis
2. Context summarization for long conversations
3. Smart context window management
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import json

from .redis_client import redis_manager


class ConversationContext:
    """Conversation context data structure"""
    
    def __init__(
        self,
        session_id: UUID,
        messages: List[Dict[str, Any]] = None,
        summary: str = None,
        last_update: datetime = None
    ):
        self.session_id = session_id
        self.messages = messages or []
        self.summary = summary
        self.last_update = last_update or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": str(self.session_id),
            "messages": self.messages,
            "summary": self.summary,
            "last_update": self.last_update.isoformat(),
            "message_count": len(self.messages)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        return cls(
            session_id=UUID(data["session_id"]),
            messages=data.get("messages", []),
            summary=data.get("summary"),
            last_update=datetime.fromisoformat(data["last_update"])
        )


class ContextSummarizer:
    """
    Summarizer for conversation history
    
    Uses lightweight processing to summarize old conversation turns
    """
    
    MAX_CHARS_PER_SUMMARY = 500
    SUMMARY_TEMPLATE = "会话摘要: {summary}\n\n"
    
    def __init__(self):
        self.summary_prompt = """请简要总结以下对话的核心内容和关键信息:

{conversation}

请用简洁的语言概括对话的主要话题、用户需求和已讨论的关键点。"""
    
    async def summarize(
        self,
        messages: List[Dict[str, Any]],
        keep_recent_turns: int = 3
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Summarize conversation history
        
        Args:
            messages: List of message dicts
            keep_recent_turns: Number of recent turns to keep unchanged
        
        Returns:
            Tuple of (summary, remaining_messages)
        """
        if len(messages) <= keep_recent_turns * 2:
            return "", messages
        
        # Separate messages
        recent_messages = messages[-(keep_recent_turns * 2):]
        old_messages = messages[:-(keep_recent_turns * 2)]
        
        # Build conversation text for summarization
        conversation_text = self._format_conversation(old_messages)
        
        # Generate summary (in production, this would call a small LLM)
        summary = await self._generate_summary(conversation_text)
        
        return summary, recent_messages
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format messages for summarization prompt"""
        lines = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                lines.append(f"用户: {content}")
            else:
                lines.append(f"助手: {content[:200]}...")
        return "\n".join(lines)
    
    async def _generate_summary(self, conversation_text: str) -> str:
        """
        Generate summary using lightweight method
        
        In production, this would call a small/fast LLM.
        For now, we extract key entities and topics.
        """
        if not conversation_text.strip():
            return ""
        
        # Simple extractive summarization
        # Extract key topics mentioned
        keywords = []
        topic_indicators = ["关于", "问题", "咨询", "询问", "查询", "订单", "产品", "退款", "投诉"]
        
        for indicator in topic_indicators:
            if indicator in conversation_text:
                keywords.append(indicator)
        
        # Get first and last exchanges
        lines = conversation_text.split("\n")
        summary_parts = []
        
        if lines:
            summary_parts.append(f"首轮: {lines[0]}")
        if len(lines) > 2:
            summary_parts.append(f"末轮: {lines[-1]}")
        
        if keywords:
            summary_parts.append(f"涉及话题: {', '.join(set(keywords))}")
        
        summary = f"对话涉及{len(lines)//2}轮交流。" + "。".join(summary_parts)
        
        if len(summary) > self.MAX_CHARS_PER_SUMMARY:
            summary = summary[:self.MAX_CHARS_PER_SUMMARY] + "..."
        
        return summary


class ContextWindowManager:
    """
    Context window manager with Redis persistence
    
    Features:
    1. Stateless conversation storage in Redis
    2. Automatic summarization for long conversations
    3. Session lifecycle management
    """
    
    # Redis key prefixes
    CONTEXT_PREFIX = "ctx:"
    SUMMARY_PREFIX = "sum:"
    
    # Settings
    MAX_MESSAGES = 20
    SUMMARIZE_THRESHOLD = 15
    KEEP_RECENT_TURNS = 3
    SESSION_TTL = 86400  # 24 hours
    
    def __init__(self):
        self.redis = redis_manager
        self.summarizer = ContextSummarizer()
    
    async def get_context(self, session_id: UUID) -> ConversationContext:
        """
        Get conversation context from Redis
        
        Args:
            session_id: Session ID
        
        Returns:
            ConversationContext object
        """
        context_key = f"{self.CONTEXT_PREFIX}{session_id}"
        summary_key = f"{self.SUMMARY_PREFIX}{session_id}"
        
        # Try to get from Redis
        context_data = await self.redis.get(context_key)
        summary = await self.redis.get(summary_key)
        
        if context_data:
            context_dict = json.loads(context_data.decode('utf-8'))
            messages = context_dict.get("messages", [])
        else:
            messages = []
        
        return ConversationContext(
            session_id=session_id,
            messages=messages,
            summary=summary.decode('utf-8') if summary else None
        )
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        metadata: Dict = None
    ) -> ConversationContext:
        """
        Add a message to the conversation context
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata
        
        Returns:
            Updated ConversationContext
        """
        context = await self.get_context(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        
        context.messages.append(message)
        
        # Check if summarization is needed
        if len(context.messages) >= self.SUMMARIZE_THRESHOLD:
            summary, remaining = await self.summarizer.summarize(
                context.messages,
                keep_recent_turns=self.KEEP_RECENT_TURNS
            )
            context.summary = summary
            context.messages = remaining
        
        # Save to Redis
        await self._save_context(context)
        
        return context
    
    async def get_messages_for_llm(
        self,
        session_id: UUID,
        max_turns: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get messages formatted for LLM context
        
        Args:
            session_id: Session ID
            max_turns: Maximum number of turns to return
        
        Returns:
            List of messages suitable for LLM
        """
        context = await self.get_context(session_id)
        
        messages = []
        
        # Add summary if exists
        if context.summary:
            messages.append({
                "role": "system",
                "content": f"【会话历史摘要】\n{context.summary}\n\n以下是对话细节:"
            })
        
        # Add recent messages
        recent_messages = context.messages[-max_turns:]
        messages.extend(recent_messages)
        
        return messages
    
    async def clear_context(self, session_id: UUID) -> bool:
        """
        Clear conversation context
        
        Args:
            session_id: Session ID
        
        Returns:
            True if cleared
        """
        context_key = f"{self.CONTEXT_PREFIX}{session_id}"
        summary_key = f"{self.SUMMARY_PREFIX}{session_id}"
        
        await self.redis.delete(context_key, summary_key)
        return True
    
    async def extend_session_ttl(self, session_id: UUID) -> bool:
        """
        Extend session TTL
        
        Args:
            session_id: Session ID
        
        Returns:
            True if extended
        """
        context_key = f"{self.CONTEXT_PREFIX}{session_id}"
        await self.redis.expire(context_key, self.SESSION_TTL)
        return True
    
    async def _save_context(self, context: ConversationContext) -> None:
        """Save context to Redis"""
        context_key = f"{self.CONTEXT_PREFIX}{context.session_id}"
        summary_key = f"{self.SUMMARY_PREFIX}{context.session_id}"
        
        # Save messages
        context_data = {
            "session_id": str(context.session_id),
            "messages": context.messages[-self.MAX_MESSAGES:],
            "last_update": context.last_update.isoformat()
        }
        await self.redis.set(
            context_key,
            json.dumps(context_data),
            ex=self.SESSION_TTL
        )
        
        # Save summary if exists
        if context.summary:
            await self.redis.set(
                summary_key,
                context.summary,
                ex=self.SESSION_TTL
            )
    
    async def get_session_info(self, session_id: UUID) -> Dict[str, Any]:
        """
        Get session information
        
        Args:
            session_id: Session ID
        
        Returns:
            Session info dict
        """
        context = await self.get_context(session_id)
        
        return {
            "session_id": str(session_id),
            "message_count": len(context.messages),
            "has_summary": context.summary is not None,
            "last_update": context.last_update.isoformat()
        }


# Singleton instance
_context_manager: Optional[ContextWindowManager] = None


def get_context_manager() -> ContextWindowManager:
    """Get singleton instance of ContextWindowManager"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextWindowManager()
    return _context_manager
