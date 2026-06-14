"""User model and related schemas for authentication"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, DateTime, Integer, String, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserDB(Base):
    """User database model
    
    Stores user account information for authentication and authorization.
    Passwords are hashed using bcrypt before storage.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ==================== Request/Response Schemas ====================


class UserCreateSchema(BaseModel):
    """Schema for user registration request
    
    Validates user input during account creation.
    Password must be at least 8 characters.
    """

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 chars)")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")


class UserLoginSchema(BaseModel):
    """Schema for user login request
    
    Simple email/password authentication.
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponseSchema(BaseModel):
    """Schema for user response in API responses
    
    Excludes sensitive information like password hashes.
    """

    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailSchema(BaseModel):
    """Detailed user schema for profile endpoints"""

    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    """Schema for updating user profile information"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


# ==================== JWT & Authentication Schemas ====================


class TokenSchema(BaseModel):
    """JWT Token response schema
    
    Returned after successful login/registration.
    Contains JWT access token for authenticated requests.
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    user: UserResponseSchema = Field(..., description="Authenticated user data")


class TokenDataSchema(BaseModel):
    """JWT Token payload data
    
    Decoded from JWT token claims.
    Used internally for authentication.
    """

    user_id: int
    email: str
    username: str


class RefreshTokenSchema(BaseModel):
    """Refresh token request schema
    
    Used to obtain a new access token without re-entering credentials.
    """

    refresh_token: str = Field(..., description="Refresh token")


class PasswordChangeSchema(BaseModel):
    """Schema for password change request"""

    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")
    confirm_password: str = Field(..., description="Confirm new password")

    def validate_passwords(self):
        """Ensure new passwords match"""
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match")
        if self.new_password == self.old_password:
            raise ValueError("New password must be different from old password")


class PasswordResetSchema(BaseModel):
    """Schema for password reset request"""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirmSchema(BaseModel):
    """Schema for confirming password reset"""

    reset_token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")
