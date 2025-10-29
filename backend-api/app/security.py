#!/usr/bin/env python3
"""
Comprehensive security layer for SecuRizz
"""

import time
import hashlib
import hmac
import jwt
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import os
from collections import defaultdict, deque

class SecurityManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True
        )
        
        # Rate limiting
        self.rate_limits = defaultdict(lambda: deque())
        self.max_requests_per_minute = 60
        self.max_requests_per_hour = 1000
        
        # Input validation patterns
        self.validation_patterns = {
            "contract_hash": r"^[a-fA-F0-9]{64}$",
            "ipfs_cid": r"^Qm[1-9A-HJ-NP-Za-km-z]{44}$",
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "wallet_address": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"
        }
        
        # JWT settings
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = "HS256"
        self.jwt_expiry = timedelta(hours=24)
        
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'"
        }

    def validate_input(self, data: Dict[str, Any], required_fields: List[str] = None) -> bool:
        """Validate input data for security"""
        try:
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        raise ValueError(f"Missing required field: {field}")
            
            # Validate each field
            for field, value in data.items():
                if not self._validate_field(field, value):
                    raise ValueError(f"Invalid field: {field}")
            
            # Check for malicious patterns
            if self._detect_malicious_content(data):
                raise ValueError("Malicious content detected")
            
            return True
            
        except Exception as e:
            print(f"❌ Input validation failed: {str(e)}")
            return False

    def _validate_field(self, field: str, value: Any) -> bool:
        """Validate individual field"""
        if field in self.validation_patterns:
            pattern = self.validation_patterns[field]
            if not re.match(pattern, str(value)):
                return False
        
        # Check for SQL injection patterns
        if isinstance(value, str):
            sql_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                r"(\b(UNION|OR|AND)\b)",
                r"(--|\#|\/\*|\*\/)",
                r"(\b(script|javascript|vbscript)\b)",
                r"(\<script|\<iframe|\<object|\<embed)",
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    return False
        
        # Check for XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, str(value), re.IGNORECASE):
                return False
        
        return True

    def _detect_malicious_content(self, data: Dict[str, Any]) -> bool:
        """Detect malicious content in data"""
        malicious_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\(",
            r"file_get_contents\s*\(",
            r"fopen\s*\(",
            r"fwrite\s*\(",
        ]
        
        for key, value in data.items():
            if isinstance(value, str):
                for pattern in malicious_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        return False

    def rate_limit(self, identifier: str) -> bool:
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Clean old entries
        while self.rate_limits[identifier] and self.rate_limits[identifier][0] < current_time - 60:
            self.rate_limits[identifier].popleft()
        
        # Check minute limit
        if len(self.rate_limits[identifier]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limits[identifier].append(current_time)
        
        # Check hour limit (simplified)
        hour_requests = sum(1 for t in self.rate_limits[identifier] if t > current_time - 3600)
        if hour_requests >= self.max_requests_per_hour:
            return False
        
        return True

    def create_jwt_token(self, user_id: str, permissions: List[str] = None) -> str:
        """Create JWT token for authentication"""
        payload = {
            "user_id": user_id,
            "permissions": permissions or [],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.jwt_expiry
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + password_hash.hex()

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt = bytes.fromhex(stored_hash[:64])
            password_hash = bytes.fromhex(stored_hash[64:])
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return hmac.compare_digest(password_hash, new_hash)
        except:
            return False

    def generate_csrf_token(self, user_id: str) -> str:
        """Generate CSRF token"""
        timestamp = str(int(time.time()))
        data = f"{user_id}:{timestamp}"
        token = hmac.new(
            self.jwt_secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return token

    def verify_csrf_token(self, token: str, user_id: str) -> bool:
        """Verify CSRF token"""
        try:
            # Extract timestamp from token
            timestamp = int(token.split(':')[1])
            current_time = int(time.time())
            
            # Check if token is not too old (1 hour)
            if current_time - timestamp > 3600:
                return False
            
            # Verify token
            data = f"{user_id}:{timestamp}"
            expected_token = hmac.new(
                self.jwt_secret.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(token, expected_token)
        except:
            return False

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "details": details
        }
        
        # Store in Redis for real-time monitoring
        self.redis_client.lpush("security_events", json.dumps(event))
        
        # Keep only last 1000 events
        self.redis_client.ltrim("security_events", 0, 999)

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers"""
        return self.security_headers

    def audit_trail(self, user_id: str, action: str, details: Dict[str, Any]):
        """Create audit trail entry"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details,
            "ip_address": "unknown",  # Would be extracted from request
            "user_agent": "unknown"   # Would be extracted from request
        }
        
        # Store audit trail
        self.redis_client.lpush("audit_trail", json.dumps(audit_entry))
        self.redis_client.ltrim("audit_trail", 0, 9999)  # Keep last 10k entries

    def detect_anomalies(self, user_id: str, action: str) -> bool:
        """Detect anomalous behavior"""
        try:
            # Get recent actions for user
            recent_actions = self.redis_client.lrange(f"user_actions:{user_id}", 0, 99)
            
            # Analyze patterns
            action_counts = defaultdict(int)
            for action_data in recent_actions:
                data = json.loads(action_data)
                action_counts[data["action"]] += 1
            
            # Check for suspicious patterns
            if action_counts[action] > 50:  # Same action 50+ times
                return True
            
            # Check for rapid requests
            current_time = time.time()
            recent_timestamps = [
                float(json.loads(action_data)["timestamp"])
                for action_data in recent_actions[-10:]  # Last 10 actions
            ]
            
            if len(recent_timestamps) >= 10:
                time_diff = current_time - recent_timestamps[0]
                if time_diff < 60:  # 10 actions in less than 1 minute
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Anomaly detection failed: {str(e)}")
            return False

# Security decorators
def require_auth(func):
    """Require authentication decorator"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract token from request
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        token = auth_header.split(" ")[1]
        security_manager = SecurityManager()
        
        try:
            payload = security_manager.verify_jwt_token(token)
            kwargs['user_id'] = payload['user_id']
            kwargs['permissions'] = payload.get('permissions', [])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        return await func(*args, **kwargs)
    return wrapper

def rate_limit_check(identifier_field: str = "user_id"):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            
            # Get identifier for rate limiting
            identifier = kwargs.get(identifier_field, "anonymous")
            
            if not security_manager.rate_limit(identifier):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(required_fields: List[str] = None):
    """Input validation decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            
            # Get request data
            request_data = kwargs.get('request_data', {})
            
            if not security_manager.validate_input(request_data, required_fields):
                raise HTTPException(status_code=400, detail="Invalid input data")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Global security manager instance
security_manager = SecurityManager()
