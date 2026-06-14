"""User authentication routes with JWT implementation

This module implements:
- User registration (signup)
- User login with JWT token generation
- Token validation and user extraction
- Password hashing with bcrypt
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    decode_token,
)
from app.models.user import (
    UserDB,
    UserCreateSchema,
    UserLoginSchema,
    UserResponseSchema,
    TokenSchema,
    TokenDataSchema,
)
from app.database import get_db

router = APIRouter()


# ==================== Helper Functions ====================


def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """Retrieve user by email address"""
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[UserDB]:
    """Retrieve user by username"""
    return db.query(UserDB).filter(UserDB.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[UserDB]:
    """Retrieve user by ID"""
    return db.query(UserDB).filter(UserDB.id == user_id).first()


# ==================== Dependency Functions ====================


async def get_current_user(
    token: str = None, db: Session = Depends(get_db)
) -> UserDB:
    """
    Dependency to extract and validate current authenticated user from JWT token.
    
    Used to protect endpoints that require authentication.
    
    Example usage in route:
    ```python
    @router.get("/me")
    async def get_profile(current_user: UserDB = Depends(get_current_user)):
        return current_user
    ```
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode JWT token
    token_data = decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = token_data.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


# ==================== Authentication Routes ====================


@router.post("/signup", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db),
):
    """
    User registration endpoint.
    
    Creates a new user account with email and password.
    Returns JWT access token on successful registration.
    
    Args:
        user_data: Registration data (email, username, password)
        db: Database session
        
    Returns:
        TokenSchema with access token and user data
        
    Raises:
        HTTPException 400: Email or username already registered
        HTTPException 400: Invalid input data
        
    Example:
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/signup \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "user@example.com",
        "username": "john_doe",
        "password": "secure_password_123"
      }'
    ```
    
    Response:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "john_doe",
        "is_active": true,
        "is_verified": false,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
      }
    }
    ```
    """
    # Check if email already exists
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_username = get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create new user in database
    new_user = UserDB(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
        }
    )

    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseSchema.from_orm(new_user),
    )


@router.post("/login", response_model=TokenSchema)
async def login(
    credentials: UserLoginSchema,
    db: Session = Depends(get_db),
):
    """
    User login endpoint.
    
    Authenticates user with email and password.
    Returns JWT access token on successful authentication.
    
    Args:
        credentials: Login credentials (email, password)
        db: Database session
        
    Returns:
        TokenSchema with access token and user data
        
    Raises:
        HTTPException 401: Invalid email or password
        HTTPException 403: User account is inactive
        
    Example:
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "user@example.com",
        "password": "secure_password_123"
      }'
    ```
    
    Response:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "john_doe",
        "is_active": true,
        "is_verified": true,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
      }
    }
    ```
    """
    # Find user by email
    user = get_user_by_email(db, credentials.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseSchema.from_orm(user),
    )


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_profile(
    current_user: UserDB = Depends(get_current_user),
):
    """
    Get current authenticated user profile.
    
    Protected endpoint - requires valid JWT token in Authorization header.
    
    Args:
        current_user: Current authenticated user (extracted from token)
        
    Returns:
        UserResponseSchema with user data
        
    Raises:
        HTTPException 401: Invalid or missing authentication token
        HTTPException 403: User account is inactive
        
    Example:
    ```bash
    curl -X GET http://localhost:8000/api/v1/auth/me \\
      -H "Authorization: Bearer <access_token>"
    ```
    
    Response:
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "username": "john_doe",
      "is_active": true,
      "is_verified": true,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
    ```
    """
    return UserResponseSchema.from_orm(current_user)


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    current_user: UserDB = Depends(get_current_user),
):
    """
    Refresh JWT access token.
    
    Protected endpoint - provides a new access token without re-authenticating.
    Useful for extending session without requiring user to log in again.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        TokenSchema with new access token
        
    Raises:
        HTTPException 401: Invalid or missing authentication token
        
    Example:
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/refresh \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    new_access_token = create_access_token(
        data={
            "user_id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenSchema(
        access_token=new_access_token,
        token_type="bearer",
        user=UserResponseSchema.from_orm(current_user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: UserDB = Depends(get_current_user),
):
    """
    Logout endpoint.
    
    In a stateless JWT system, logout is typically handled on the client side
    by removing the token from local storage. This endpoint serves as a
    placeholder for applications that may need server-side logout tracking
    (e.g., token blacklisting).
    
    Protected endpoint - requires valid JWT token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        HTTP 204 No Content on success
        
    Example:
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/logout \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    # TODO: Implement token blacklisting if needed
    # For now, logout is handled client-side by removing token
    return None
