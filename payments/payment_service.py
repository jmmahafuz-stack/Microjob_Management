"""
Payment Gateway Service for verifying transactions with bKash, Nagad, Rocket, etc.
This service handles payment verification through APIs or manual verification.
"""

import re
import json
from .models import CommissionSetting
from decimal import Decimal
from typing import Dict, Tuple, Optional
from datetime import datetime


class PaymentGatewayService:
    """Service for verifying payments through various gateways."""
    
    # Gateway configurations (can be set from Django settings)
    BKASH_API_URL = "https://api.bkash.com/v1/pay/verify"
    NAGAD_API_URL = "https://api.nagad.co.bd/verify"
    ROCKET_API_URL = "https://rocket.com.bd/api/verify"
    

    
    # Bangladesh phone number pattern (10-11 digits starting with 0)
    BD_PHONE_PATTERN = r'^01[0-9]{9}$'
    
    def __init__(self):
     """Initialize the payment gateway service."""
     self.commission_rate = CommissionSetting.get_rate()
    
    def verify_transaction(
        self, 
        payment_method: str, 
        transaction_id: str, 
        amount: Decimal, 
        phone_number: str = None
    ) -> Dict:
        """
        Verify a payment transaction with the appropriate gateway.
        
        Args:
            payment_method: 'BKash', 'Nagad', 'Rocket', or 'Cash'
            transaction_id: Transaction ID from payment provider
            amount: Amount in BDT
            phone_number: Phone number for mobile money verification
        
        Returns:
            Dict with keys: 'success', 'status', 'message', 'gateway_response'
            Example: {
                'success': True,
                'status': 'verified',
                'message': 'Payment verified successfully',
                'gateway_response': {...}
            }
        """
        payment_method = payment_method.lower()
        
        try:
            if payment_method == 'bkash':
                return self._verify_bkash(transaction_id, amount, phone_number)
            elif payment_method == 'nagad':
                return self._verify_nagad(transaction_id, amount, phone_number)
            elif payment_method == 'rocket':
                return self._verify_rocket(transaction_id, amount, phone_number)
            elif payment_method == 'cash':
                return self._verify_cash(transaction_id, amount)
            else:
                return {
                    'success': False,
                    'status': 'unsupported',
                    'message': f'Payment method {payment_method} not supported',
                    'gateway_response': {}
                }
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'message': f'Verification error: {str(e)}',
                'gateway_response': {'error': str(e)}
            }
    
    def _verify_bkash(
        self, 
        transaction_id: str, 
        amount: Decimal, 
        phone_number: str = None
    ) -> Dict:
        """
        Verify bKash transaction.
        
        In production, this would call bKash API.
        For now, returns mock verification.
        """
        # Validate transaction ID format (usually 10-12 digits)
        if not transaction_id or len(str(transaction_id)) < 6:
            return {
                'success': False,
                'status': 'invalid_txn',
                'message': 'Invalid bKash transaction ID format',
                'gateway_response': {'txn_id': transaction_id}
            }
        
        # Mock API response
        gateway_response = {
            'txn_id': transaction_id,
            'amount': float(amount),
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'payment_method': 'bkash',
            'phone': phone_number or 'N/A',
            'merchant_id': 'MERCHANT_001',
        }
        
        # In production, verify with real API
        # response = requests.post(self.BKASH_API_URL, json={...})
        
        return {
            'success': True,
            'status': 'verified',
            'message': f'bKash transaction {transaction_id} verified',
            'gateway_response': gateway_response
        }
    
    def _verify_nagad(
        self, 
        transaction_id: str, 
        amount: Decimal, 
        phone_number: str = None
    ) -> Dict:
        """
        Verify Nagad transaction.
        
        In production, this would call Nagad API.
        For now, returns mock verification.
        """
        # Validate transaction ID
        if not transaction_id or len(str(transaction_id)) < 6:
            return {
                'success': False,
                'status': 'invalid_txn',
                'message': 'Invalid Nagad transaction ID format',
                'gateway_response': {'txn_id': transaction_id}
            }
        
        # Mock API response
        gateway_response = {
            'txn_id': transaction_id,
            'amount': float(amount),
            'status': 'complete',
            'timestamp': datetime.now().isoformat(),
            'payment_method': 'nagad',
            'phone': phone_number or 'N/A',
            'merchant_code': 'MER123',
        }
        
        # In production, verify with real API
        # response = requests.post(self.NAGAD_API_URL, json={...})
        
        return {
            'success': True,
            'status': 'verified',
            'message': f'Nagad transaction {transaction_id} verified',
            'gateway_response': gateway_response
        }
    
    def _verify_rocket(
        self, 
        transaction_id: str, 
        amount: Decimal, 
        phone_number: str = None
    ) -> Dict:
        """
        Verify Rocket transaction.
        
        In production, this would call Rocket API.
        For now, returns mock verification.
        """
        # Validate transaction ID
        if not transaction_id or len(str(transaction_id)) < 6:
            return {
                'success': False,
                'status': 'invalid_txn',
                'message': 'Invalid Rocket transaction ID format',
                'gateway_response': {'txn_id': transaction_id}
            }
        
        # Mock API response
        gateway_response = {
            'txn_id': transaction_id,
            'amount': float(amount),
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'payment_method': 'rocket',
            'phone': phone_number or 'N/A',
        }
        
        # In production, verify with real API
        # response = requests.post(self.ROCKET_API_URL, json={...})
        
        return {
            'success': True,
            'status': 'verified',
            'message': f'Rocket transaction {transaction_id} verified',
            'gateway_response': gateway_response
        }
    
    def _verify_cash(
        self, 
        transaction_id: str, 
        amount: Decimal
    ) -> Dict:
        """
        Verify cash payment (manual entry, requires admin verification).
        """
        if not transaction_id:
            return {
                'success': False,
                'status': 'missing_ref',
                'message': 'Cash payment requires reference number',
                'gateway_response': {}
            }
        
        return {
            'success': True,
            'status': 'pending_admin',
            'message': f'Cash payment {transaction_id} pending admin verification',
            'gateway_response': {
                'ref_number': transaction_id,
                'amount': float(amount),
                'status': 'awaiting_admin',
                'timestamp': datetime.now().isoformat(),
                'payment_method': 'cash',
            }
        }
    
    def validate_payment_number(
        self, 
        phone_number: str, 
        payment_method: str
    ) -> Tuple[bool, str]:
        """
        Validate a payment phone number for the given method.
        
        Args:
            phone_number: Phone number to validate
            payment_method: 'bkash', 'nagad', or 'rocket'
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone_number:
            return False, f"Please provide a {payment_method} number"
        
        # Bangladesh phone numbers should start with 01 and be 10-11 digits
        if not re.match(self.BD_PHONE_PATTERN, str(phone_number)):
            return False, f"Invalid {payment_method} number. Use format: 01XXXXXXXXX"
        
        return True, ""
    
    def calculate_worker_payout(
        self, 
        customer_amount: Decimal, 
        commission_rate: int = None
    ) -> Dict:
        """
        Calculate platform commission and worker earnings.
        
        Args:
            customer_amount: Total amount customer pays
            commission_rate: Commission percentage (default 10%)
        
        Returns:
            Dict with 'platform_commission' and 'worker_amount'
            Example: {
                'customer_amount': 2000,
                'commission_rate': 10,
                'platform_commission': 200,
                'worker_amount': 1800,
                'currency': 'BDT'
            }
        """
        if commission_rate is None:
         commission_rate = CommissionSetting.get_rate()
        
        customer_amt = Decimal(str(customer_amount))
        commission_pct = Decimal(str(commission_rate))
        
        platform_commission = (customer_amt * commission_pct) / Decimal('100')
        worker_amount = customer_amt - platform_commission
        
        return {
            'customer_amount': float(customer_amt),
            'commission_rate': commission_rate,
            'platform_commission': float(platform_commission),
            'worker_amount': float(worker_amount),
            'currency': 'BDT'
        }
    
    def log_verification(
        self, 
        payment_id: int, 
        verification_result: Dict
    ) -> None:
        """
        Log payment verification for audit trail.
        
        Args:
            payment_id: Payment model ID
            verification_result: Result from verify_transaction()
        """
        from payments.models import Payment
        from django.utils import timezone
        
        try:
            payment = Payment.objects.get(pk=payment_id)
            payment.gateway_response = verification_result.get('gateway_response', {})
            payment.gateway_status = verification_result.get('status', 'unknown')
            
            if verification_result.get('success'):
                payment.payment_status = 'Verified'
                payment.worker_payout_status = 'Available'
                payment.verified_date = timezone.now()
            else:
                payment.payment_status = 'Pending'
            
            payment.save()
        except Payment.DoesNotExist:
            pass


# Global service instance
payment_service = PaymentGatewayService()
