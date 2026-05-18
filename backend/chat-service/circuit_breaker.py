"""
Circuit Breaker and Rate Limiter for External LLM API

Features:
1. Token bucket rate limiting
2. Circuit breaker pattern for LLM API calls
3. Fallback responses when circuit is open
"""
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import asyncio
import time

from .redis_client import redis_manager


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class CircuitOpen(Exception):
    """Exception raised when circuit is open"""
    pass


@dataclass
class FallbackResponse:
    """Fallback response for degraded service"""
    message: str
    suggested_action: str
    can_human_takeover: bool = True
    
    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "suggested_action": self.suggested_action,
            "can_human_takeover": self.can_human_takeover
        }


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter
    
    Features:
    - Configurable rate and capacity
    - Redis-based for distributed deployment
    - Sliding window support
    """
    
    def __init__(
        self,
        rate: int = 60,
        capacity: int = 100,
        window: int = 60
    ):
        """
        Initialize rate limiter
        
        Args:
            rate: Tokens per window (requests per minute)
            capacity: Maximum tokens in bucket
            window: Time window in seconds
        """
        self.rate = rate
        self.capacity = capacity
        self.window = window
        self.redis = redis_manager
    
    async def acquire(self, key: str) -> bool:
        """
        Acquire a token
        
        Args:
            key: Rate limit key (e.g., user_id, enterprise_id)
        
        Returns:
            True if token acquired, False if rate limited
        
        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        redis_key = f"ratelimit:{key}"
        
        try:
            await self.redis.connect()
            
            # Get current count
            current = await self.redis.get(redis_key)
            count = int(current.decode('utf-8')) if current else 0
            
            if count >= self.rate:
                raise RateLimitExceeded(f"Rate limit exceeded: {self.rate} requests per {self.window}s")
            
            # Increment counter
            if count == 0:
                await self.redis.set(redis_key, 1, ex=self.window)
            else:
                await self.redis.incr(redis_key)
            
            return True
            
        except RateLimitExceeded:
            raise
        except Exception as e:
            # On Redis error, allow request (fail open)
            print(f"Rate limiter error: {e}")
            return True
    
    async def check_limit(self, key: str) -> dict:
        """
        Check rate limit without consuming
        
        Args:
            key: Rate limit key
        
        Returns:
            Dict with limit info
        """
        redis_key = f"ratelimit:{key}"
        
        try:
            await self.redis.connect()
            current = await self.redis.get(redis_key)
            count = int(current.decode('utf-8')) if current else 0
            
            return {
                "remaining": max(0, self.rate - count),
                "limit": self.rate,
                "reset_in": self.window
            }
        except Exception as e:
            return {
                "remaining": self.rate,
                "limit": self.rate,
                "reset_in": self.window,
                "error": str(e)
            }


class CircuitBreaker:
    """
    Circuit breaker for external service calls
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service failing, requests rejected immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before trying half-open
            half_open_max_calls: Max calls in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._last_state_change = datetime.utcnow()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout passed
            if self._last_failure_time:
                elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self._last_state_change = datetime.utcnow()
        
        return self._state
    
    def record_success(self) -> None:
        """Record a successful call"""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._last_state_change = datetime.utcnow()
        else:
            self._failure_count = 0
    
    def record_failure(self) -> None:
        """Record a failed call"""
        self._failure_count += 1
        self._last_failure_time = datetime.utcnow()
        
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._last_state_change = datetime.utcnow()
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._last_state_change = datetime.utcnow()
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.half_open_max_calls
        else:
            return False
    
    def get_status(self) -> dict:
        """Get circuit breaker status"""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "last_state_change": self._last_state_change.isoformat(),
            "recovery_timeout": self.recovery_timeout
        }


class LLMCircuitBreaker:
    """
    Circuit breaker specifically for LLM API calls
    """
    
    # Default fallback responses
    DEFAULT_FALLBACKS = [
        FallbackResponse(
            message="抱歉，我现在遇到了一些技术问题，无法立即回答您的问题。",
            suggested_action="您可以稍后再试，或者选择转人工客服获取帮助。",
            can_human_takeover=True
        ),
        FallbackResponse(
            message="系统繁忙，请稍等片刻。",
            suggested_action="如果问题紧急，请联系人工客服。",
            can_human_takeover=True
        ),
    ]
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        self.fallbacks = self.DEFAULT_FALLBACKS
        self._fallback_index = 0
    
    def get_fallback(self) -> FallbackResponse:
        """Get next fallback response"""
        fallback = self.fallbacks[self._fallback_index]
        self._fallback_index = (self._fallback_index + 1) % len(self.fallbacks)
        return fallback
    
    async def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result or fallback response
        
        Raises:
            CircuitOpen: If circuit is open and fallback not returned
        """
        if not self.circuit_breaker.can_execute():
            # Return fallback response
            fallback = self.get_fallback()
            return fallback
        
        try:
            result = await func(*args, **kwargs)
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            
            # Check if circuit is now open
            if self.circuit_breaker.state == CircuitState.OPEN:
                fallback = self.get_fallback()
                return fallback
            
            raise


# Singleton instances
_llm_rate_limiter: Optional[TokenBucketRateLimiter] = None
_llm_circuit_breaker: Optional[LLMCircuitBreaker] = None


def get_llm_rate_limiter() -> TokenBucketRateLimiter:
    """Get singleton instance of LLM rate limiter"""
    global _llm_rate_limiter
    if _llm_rate_limiter is None:
        _llm_rate_limiter = TokenBucketRateLimiter(rate=60, capacity=100, window=60)
    return _llm_rate_limiter


def get_llm_circuit_breaker() -> LLMCircuitBreaker:
    """Get singleton instance of LLM circuit breaker"""
    global _llm_circuit_breaker
    if _llm_circuit_breaker is None:
        _llm_circuit_breaker = LLMCircuitBreaker(failure_threshold=5, recovery_timeout=60)
    return _llm_circuit_breaker
