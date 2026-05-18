"""
Bad Case Auto-Detection and Mining System

Features:
1. Explicit negative feedback detection (thumbs down)
2. Implicit negative signal detection
3. Automatic bad case tagging and review queue
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from .database import get_db_context
from .quality_models import Feedback, UnmatchedQuestion
from .models import ChatMessage, ChatSession


class BadCaseType(Enum):
    """Bad case types"""
    EXPLICIT_THUMBS_DOWN = "explicit_thumbs_down"
    HUMAN_TAKEOVER = "human_takeover"
    REPEATED_QUERY = "repeated_query"
    LOW_RETRIEVAL_SCORE = "low_retrieval_score"
    USER_ABANDON = "user_abandon"
    LONG_RESPONSE_TIME = "long_response_time"


class BadCaseSeverity(Enum):
    """Bad case severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BadCase:
    """Bad case data structure"""
    case_id: str
    session_id: UUID
    message_id: UUID
    user_id: UUID
    enterprise_id: UUID
    case_type: BadCaseType
    severity: BadCaseSeverity
    original_query: str
    ai_response: str
    reasons: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    status: str = "pending_review"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "session_id": str(self.session_id),
            "message_id": str(self.message_id),
            "user_id": str(self.user_id),
            "enterprise_id": str(self.enterprise_id),
            "case_type": self.case_type.value,
            "severity": self.severity.value,
            "original_query": self.original_query,
            "ai_response": self.ai_response,
            "reasons": self.reasons,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


class BadCaseDetector:
    """
    Bad case detector
    
    Detects bad cases from multiple signals:
    1. Explicit negative feedback (thumbs down)
    2. Human takeover after AI response
    3. Repeated similar queries
    4. Low retrieval scores
    5. User abandonment patterns
    """
    
    REPEATED_QUERY_THRESHOLD = 3
    REPEATED_QUERY_TIME_WINDOW = 300  # 5 minutes
    LOW_SCORE_THRESHOLD = 0.3
    RESPONSE_TIME_THRESHOLD = 30  # 30 seconds
    
    def __init__(self):
        self.recent_queries: Dict[str, List[Dict]] = {}
    
    def detect_from_explicit_feedback(
        self,
        message_id: UUID,
        feedback: Feedback,
        ai_response: str
    ) -> Optional[BadCase]:
        """
        Create bad case from explicit thumbs down feedback
        
        Args:
            message_id: Message ID
            feedback: Feedback object
            ai_response: The AI response content
            session: Chat session
        
        Returns:
            BadCase or None
        """
        # Get message details from database
        from .database import get_db_context
        with get_db_context() as db:
            message = db.query(ChatMessage).filter(
                ChatMessage.id == message_id
            ).first()
            
            if not message:
                return None
            
            session = db.query(ChatSession).filter(
                ChatSession.id == message.session_id
            ).first()
            
            if not session:
                return None
        
        severity = BadCaseSeverity.MEDIUM
        if feedback.reason:
            severity = BadCaseSeverity.HIGH
        
        return BadCase(
            case_id=f"case_{message_id}_{int(datetime.utcnow().timestamp())}",
            session_id=message.session_id,
            message_id=message_id,
            user_id=session.user_id,
            enterprise_id=session.enterprise_id,
            case_type=BadCaseType.EXPLICIT_THUMBS_DOWN,
            severity=severity,
            original_query=message.content,
            ai_response=ai_response,
            reasons=[f"用户点踩: {feedback.reason}" if feedback.reason else "用户点踩"],
            metadata={"feedback_id": str(feedback.id)},
            created_at=datetime.utcnow()
        )
    
    def detect_from_human_takeover(
        self,
        session_id: UUID,
        user_id: UUID,
        enterprise_id: UUID,
        ai_response: str,
        takeover_reason: str
    ) -> BadCase:
        """
        Create bad case from human takeover event
        
        Args:
            session_id: Session ID
            user_id: User ID
            enterprise_id: Enterprise ID
            ai_response: The AI response before takeover
            takeover_reason: Reason for takeover
        
        Returns:
            BadCase
        """
        # Get the last user message
        from .database import get_db_context
        with get_db_context() as db:
            last_message = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id,
                ChatMessage.role == "user"
            ).order_by(ChatMessage.created_at.desc()).first()
            
            user_query = last_message.content if last_message else ""
            message_id = last_message.id if last_message else None
        
        return BadCase(
            case_id=f"case_human_{session_id}_{int(datetime.utcnow().timestamp())}",
            session_id=session_id,
            message_id=message_id or UUID("00000000-0000-0000-0000-000000000000"),
            user_id=user_id,
            enterprise_id=enterprise_id,
            case_type=BadCaseType.HUMAN_TAKEOVER,
            severity=BadCaseSeverity.HIGH,
            original_query=user_query,
            ai_response=ai_response,
            reasons=[f"转人工: {takeover_reason}"],
            metadata={"takeover_reason": takeover_reason},
            created_at=datetime.utcnow()
        )
    
    def detect_from_repeated_query(
        self,
        session_id: UUID,
        user_id: UUID,
        enterprise_id: UUID,
        query: str,
        previous_responses: List[str]
    ) -> Optional[BadCase]:
        """
        Detect repeated similar queries indicating dissatisfaction
        
        Args:
            session_id: Session ID
            user_id: User ID
            enterprise_id: Enterprise ID
            query: Current user query
            previous_responses: Previous AI responses
        
        Returns:
            BadCase or None if not repeated enough
        """
        query_key = f"{user_id}:{query[:50].lower()}"
        
        if query_key not in self.recent_queries:
            self.recent_queries[query_key] = []
        
        self.recent_queries[query_key].append({
            "session_id": str(session_id),
            "timestamp": datetime.utcnow(),
            "query": query
        })
        
        # Count recent queries (within time window)
        recent = [
            q for q in self.recent_queries[query_key]
            if (datetime.utcnow() - q["timestamp"]).total_seconds() < self.REPEATED_QUERY_TIME_WINDOW
        ]
        
        self.recent_queries[query_key] = recent
        
        if len(recent) >= self.REPEATED_QUERY_THRESHOLD:
            return BadCase(
                case_id=f"case_repeat_{session_id}_{int(datetime.utcnow().timestamp())}",
                session_id=session_id,
                message_id=UUID("00000000-0000-0000-0000-000000000000"),
                user_id=user_id,
                enterprise_id=enterprise_id,
                case_type=BadCaseType.REPEATED_QUERY,
                severity=BadCaseSeverity.MEDIUM,
                original_query=query,
                ai_response=" | ".join(previous_responses[:3]),
                reasons=[f"用户重复提问 {len(recent)} 次，疑似回答不满意"],
                metadata={"repeat_count": len(recent)},
                created_at=datetime.utcnow()
            )
        
        return None
    
    def detect_from_low_score(
        self,
        session_id: UUID,
        user_id: UUID,
        enterprise_id: UUID,
        query: str,
        ai_response: str,
        retrieval_score: float
    ) -> Optional[BadCase]:
        """
        Detect bad case from low retrieval score
        
        Args:
            session_id: Session ID
            user_id: User ID
            enterprise_id: Enterprise ID
            query: User query
            ai_response: AI response
            retrieval_score: Retrieval confidence score
        
        Returns:
            BadCase or None
        """
        if retrieval_score >= self.LOW_SCORE_THRESHOLD:
            return None
        
        # Determine severity based on score
        if retrieval_score < 0.1:
            severity = BadCaseSeverity.HIGH
        elif retrieval_score < 0.2:
            severity = BadCaseSeverity.MEDIUM
        else:
            severity = BadCaseSeverity.LOW
        
        return BadCase(
            case_id=f"case_score_{session_id}_{int(datetime.utcnow().timestamp())}",
            session_id=session_id,
            message_id=UUID("00000000-0000-0000-0000-000000000000"),
            user_id=user_id,
            enterprise_id=enterprise_id,
            case_type=BadCaseType.LOW_RETRIEVAL_SCORE,
            severity=severity,
            original_query=query,
            ai_response=ai_response,
            reasons=[f"检索得分过低: {retrieval_score:.2f}"],
            metadata={"retrieval_score": retrieval_score},
            created_at=datetime.utcnow()
        )


class BadCaseRepository:
    """
    Repository for storing and retrieving bad cases
    """
    
    BAD_CASE_PREFIX = "badcase:"
    
    def __init__(self):
        self.redis = None  # Will be initialized on first use
    
    async def save_bad_case(self, bad_case: BadCase) -> bool:
        """
        Save bad case to storage
        
        Args:
            bad_case: BadCase object
        
        Returns:
            True if saved successfully
        """
        if not self.redis:
            from .redis_client import redis_manager
            self.redis = redis_manager
            await self.redis.connect()
        
        key = f"{self.BAD_CASE_PREFIX}{bad_case.case_id}"
        await self.redis.set(
            key,
            json.dumps(bad_case.to_dict()),
            ex=86400 * 30  # 30 days retention
        )
        
        # Add to enterprise's bad case list
        list_key = f"{self.BAD_CASE_PREFIX}list:{bad_case.enterprise_id}"
        await self.redis.lpush(list_key, bad_case.case_id)
        
        return True
    
    async def get_bad_cases_by_enterprise(
        self,
        enterprise_id: UUID,
        status: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get bad cases for an enterprise
        
        Args:
            enterprise_id: Enterprise ID
            status: Optional status filter
            limit: Maximum number of results
        
        Returns:
            List of bad case dicts
        """
        if not self.redis:
            from .redis_client import redis_manager
            self.redis = redis_manager
            await self.redis.connect()
        
        list_key = f"{self.BAD_CASE_PREFIX}list:{enterprise_id}"
        case_ids = await self.redis.lrange(list_key, 0, limit - 1)
        
        cases = []
        for case_id in case_ids:
            case_id_str = case_id.decode('utf-8') if isinstance(case_id, bytes) else case_id
            key = f"{self.BAD_CASE_PREFIX}{case_id_str}"
            case_data = await self.redis.get(key)
            
            if case_data:
                case = json.loads(case_data.decode('utf-8'))
                if status is None or case.get("status") == status:
                    cases.append(case)
        
        return cases
    
    async def get_bad_case_stats(self, enterprise_id: UUID) -> Dict[str, Any]:
        """
        Get bad case statistics for an enterprise
        
        Args:
            enterprise_id: Enterprise ID
        
        Returns:
            Statistics dict
        """
        cases = await self.get_bad_cases_by_enterprise(enterprise_id, limit=1000)
        
        if not cases:
            return {
                "total": 0,
                "pending_review": 0,
                "reviewed": 0,
                "by_type": {},
                "by_severity": {}
            }
        
        stats = {
            "total": len(cases),
            "pending_review": len([c for c in cases if c.get("status") == "pending_review"]),
            "reviewed": len([c for c in cases if c.get("status") == "reviewed"]),
            "by_type": {},
            "by_severity": {}
        }
        
        for case in cases:
            case_type = case.get("case_type", "unknown")
            severity = case.get("severity", "unknown")
            
            stats["by_type"][case_type] = stats["by_type"].get(case_type, 0) + 1
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        return stats


# Singleton instances
_bad_case_detector: Optional[BadCaseDetector] = None
_bad_case_repository: Optional[BadCaseRepository] = None


def get_bad_case_detector() -> BadCaseDetector:
    """Get singleton instance of BadCaseDetector"""
    global _bad_case_detector
    if _bad_case_detector is None:
        _bad_case_detector = BadCaseDetector()
    return _bad_case_detector


def get_bad_case_repository() -> BadCaseRepository:
    """Get singleton instance of BadCaseRepository"""
    global _bad_case_repository
    if _bad_case_repository is None:
        _bad_case_repository = BadCaseRepository()
    return _bad_case_repository
