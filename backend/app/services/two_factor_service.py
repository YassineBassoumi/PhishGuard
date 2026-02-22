"""
Two-Factor Authentication Service
Handles TOTP generation, verification, and QR code creation
"""

import pyotp
import qrcode
import io
import base64
import json
import secrets
from typing import Tuple, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_models import User


class TwoFactorService:
    """Service for handling two-factor authentication"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a random base32 secret for TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_backup_codes(count: int = 8) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            # Format as XXXX-XXXX
            formatted_code = f"{code[:4]}-{code[4:]}"
            codes.append(formatted_code)
        return codes
    
    @staticmethod
    def get_totp_uri(secret: str, username: str, issuer: str = "PhishGuard") -> str:
        """Generate TOTP URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)
    
    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """Verify a TOTP token"""
        totp = pyotp.TOTP(secret)
        # Allow 1 time step before and after for clock skew
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def verify_backup_code(user: User, code: str) -> bool:
        """Verify and consume a backup code"""
        if not user.backup_codes:
            return False
        
        try:
            backup_codes = json.loads(user.backup_codes)
        except json.JSONDecodeError:
            return False
        
        # Normalize the code (remove spaces, hyphens, uppercase)
        normalized_code = code.replace(' ', '').replace('-', '').upper()
        
        # Check if code exists
        for stored_code in backup_codes:
            normalized_stored = stored_code.replace(' ', '').replace('-', '').upper()
            if normalized_code == normalized_stored:
                # Remove the used code
                backup_codes.remove(stored_code)
                user.backup_codes = json.dumps(backup_codes)
                return True
        
        return False
    
    @staticmethod
    async def setup_2fa(user: User) -> Tuple[str, str, List[str]]:
        """
        Setup 2FA for a user
        Returns: (secret, qr_code_data_uri, backup_codes)
        """
        # Generate secret
        secret = TwoFactorService.generate_secret()
        
        # Generate QR code
        uri = TwoFactorService.get_totp_uri(secret, user.username)
        qr_code = TwoFactorService.generate_qr_code(uri)
        
        # Generate backup codes
        backup_codes = TwoFactorService.generate_backup_codes()
        
        # Store secret (but don't enable 2FA yet - user must verify first)
        user.two_factor_secret = secret
        user.backup_codes = json.dumps(backup_codes)
        
        return secret, qr_code, backup_codes
    
    @staticmethod
    async def enable_2fa(user: User, token: str) -> bool:
        """
        Enable 2FA after verifying the initial token
        Returns: True if successful, False otherwise
        """
        if not user.two_factor_secret:
            return False
        
        # Verify the token
        if not TwoFactorService.verify_totp(user.two_factor_secret, token):
            return False
        
        # Enable 2FA
        user.two_factor_enabled = True
        return True
    
    @staticmethod
    async def disable_2fa(user: User, password: str, auth_service) -> bool:
        """
        Disable 2FA (requires password verification)
        Returns: True if successful, False otherwise
        """
        # Verify password
        if not auth_service.verify_password(password, user.hashed_password):
            return False
        
        # Disable 2FA and clear secrets
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.backup_codes = None
        
        return True
    
    @staticmethod
    def get_remaining_backup_codes(user: User) -> int:
        """Get count of remaining backup codes"""
        if not user.backup_codes:
            return 0
        
        try:
            backup_codes = json.loads(user.backup_codes)
            return len(backup_codes)
        except json.JSONDecodeError:
            return 0
    
    @staticmethod
    async def regenerate_backup_codes(user: User) -> List[str]:
        """Regenerate backup codes"""
        backup_codes = TwoFactorService.generate_backup_codes()
        user.backup_codes = json.dumps(backup_codes)
        return backup_codes


# Singleton instance
two_factor_service = TwoFactorService()
