"""
Payment Gateway Integration Service
Handles payment verification, processing, and transaction management.
"""

from decimal import Decimal
from typing import Dict, Optional, Tuple
from django.utils import timezone
from django.conf import settings
from django.db import models
import logging

logger = logging.getLogger(__name__)


class PaymentGatewayService:
    """
    Base service for payment gateway integration.
    Supports BKash, Nagad, Rocket, and other payment methods.
    """
    
    # Mock gateway responses for testing
    MOCK_GATEWAYS = {
        'bkash': {
            'api_url': 'https://api.bkash.com/v1',
            'timeout': 30,
        },
        'nagad': {
            'api_url': 'https://api.nagad.com.bd/v1',
            'timeout': 30,
        },
        'rocket': {
            'api_url': 'https://api.rocket.com.bd',
            'timeout': 30,
        }
    }
    
    @staticmethod
    def verify_transaction(
        transaction_id: str,
        payment_method: str,
        customer_amount: Decimal,
        worker_number: str = None,
    ) -> Tuple[bool, Dict]:
        """
        Verify payment through gateway API.
        
        Args:
            transaction_id: Transaction ID from payment method
            payment_method: 'BKash', 'Nagad', 'Rocket', etc.
            customer_amount: Expected payment amount
            worker_number: Worker's payment method number
            
        Returns:
            Tuple of (is_valid, response_dict)
        """
        try:
            method_lower = payment_method.lower()
            
            if method_lower == 'bkash':
                return PaymentGatewayService._verify_bkash(
                    transaction_id, customer_amount, worker_number
                )
            elif method_lower == 'nagad':
                return PaymentGatewayService._verify_nagad(
                    transaction_id, customer_amount, worker_number
                )
            elif method_lower == 'rocket':
                return PaymentGatewayService._verify_rocket(
                    transaction_id, customer_amount, worker_number
                )
            elif method_lower == 'cash':
                # Manual verification for cash payments
                return PaymentGatewayService._verify_cash(transaction_id)
            else:
                return False, {'error': f'Unsupported payment method: {payment_method}'}
                
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return False, {'error': str(e)}
    
    @staticmethod
    def _verify_bkash(
        transaction_id: str,
        amount: Decimal,
        worker_number: str = None,
    ) -> Tuple[bool, Dict]:
        """Verify bKash transaction."""
        # In production, this would call bKash API
        # For now, this is a mock implementation
        response = {
            'gateway': 'bkash',
            'transaction_id': transaction_id,
            'amount': str(amount),
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'verified': True,
            'reference': f'BKP-{transaction_id}',
            'notes': 'bKash transaction verified successfully'
        }
        
        # Validation checks
        if not transaction_id or len(transaction_id) < 5:
            return False, {'error': 'Invalid transaction ID format', 'gateway': 'bkash'}
        
        if amount <= 0:
            return False, {'error': 'Invalid payment amount', 'gateway': 'bkash'}
        
        logger.info(f"bKash transaction verified: {transaction_id}")
        return True, response
    
    @staticmethod
    def _verify_nagad(
        transaction_id: str,
        amount: Decimal,
        worker_number: str = None,
    ) -> Tuple[bool, Dict]:
        """Verify Nagad transaction."""
        response = {
            'gateway': 'nagad',
            'transaction_id': transaction_id,
            'amount': str(amount),
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'verified': True,
            'reference': f'NAG-{transaction_id}',
            'notes': 'Nagad transaction verified successfully'
        }
        
        # Validation checks
        if not transaction_id or len(transaction_id) < 5:
            return False, {'error': 'Invalid transaction ID format', 'gateway': 'nagad'}
        
        if amount <= 0:
            return False, {'error': 'Invalid payment amount', 'gateway': 'nagad'}
        
        logger.info(f"Nagad transaction verified: {transaction_id}")
        return True, response
    
    @staticmethod
    def _verify_rocket(
        transaction_id: str,
        amount: Decimal,
        worker_number: str = None,
    ) -> Tuple[bool, Dict]:
        """Verify Rocket transaction."""
        response = {
            'gateway': 'rocket',
            'transaction_id': transaction_id,
            'amount': str(amount),
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'verified': True,
            'reference': f'RCK-{transaction_id}',
            'notes': 'Rocket transaction verified successfully'
        }
        
        # Validation checks
        if not transaction_id or len(transaction_id) < 5:
            return False, {'error': 'Invalid transaction ID format', 'gateway': 'rocket'}
        
        if amount <= 0:
            return False, {'error': 'Invalid payment amount', 'gateway': 'rocket'}
        
        logger.info(f"Rocket transaction verified: {transaction_id}")
        return True, response
    
    @staticmethod
    def _verify_cash(transaction_id: str) -> Tuple[bool, Dict]:
        """Verify cash payment (manual verification required)."""
        response = {
            'gateway': 'cash',
            'transaction_id': transaction_id,
            'status': 'pending',
            'timestamp': timezone.now().isoformat(),
            'verified': False,
            'notes': 'Cash payment requires manual admin verification'
        }
        
        # Cash payments need manual verification
        return False, response
    
    @staticmethod
    def validate_payment_number(payment_method: str, number: str) -> Tuple[bool, str]:
        """
        Validate payment method phone number.
        
        Args:
            payment_method: 'BKash', 'Nagad', 'Rocket'
            number: Phone number or account identifier
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not number:
            return False, f"{payment_method} number is required"
        
        # Remove any non-digits
        clean_number = ''.join(filter(str.isdigit, number))
        
        # Bangladesh numbers are 10-11 digits
        if len(clean_number) < 10 or len(clean_number) > 11:
            return False, f"{payment_method} number must be 10-11 digits"
        
        # Check if starts with valid Bangladesh prefix
        if not clean_number.startswith('1'):
            return False, f"{payment_method} number must be a valid Bangladesh number"
        
        return True, f"{payment_method} number is valid"
    
    @staticmethod
    def calculate_worker_payout(
        customer_amount: Decimal,
        commission_rate: Decimal = Decimal('10'),
    ) -> Dict[str, Decimal]:
        """
        Calculate payment split between platform and worker.
        
        Args:
            customer_amount: Total amount paid by customer
            commission_rate: Platform commission percentage (default 10%)
            
        Returns:
            Dict with commission and worker_amount
        """
        if customer_amount <= 0:
            raise ValueError("Customer amount must be positive")
        
        platform_commission = customer_amount * (commission_rate / Decimal('100'))
        worker_amount = customer_amount - platform_commission
        
        return {
            'customer_amount': customer_amount,
            'platform_commission': platform_commission,
            'worker_amount': worker_amount,
            'commission_rate': commission_rate,
        }


class PaymentTransactionLogger:
    """Log and track all payment transactions for audit trail."""
    
    @staticmethod
    def log_transaction(
        payment,
        action: str,
        status: str,
        notes: str = '',
        gateway_response: Dict = None,
    ):
        """
        Log payment transaction for audit purposes.
        
        Args:
            payment: Payment model instance
            action: 'created', 'verified', 'refunded', etc.
            status: Current status
            notes: Additional notes
            gateway_response: Response from payment gateway
        """
        from .models import Payment
        
        log_entry = {
            'payment_id': payment.id,
            'action': action,
            'status': status,
            'notes': notes,
            'timestamp': timezone.now().isoformat(),
            'gateway_response': gateway_response,
            'user': payment.job.customer.username if payment.job else 'Unknown',
            'amount': str(payment.customer_amount),
            'method': payment.payment_method,
        }
        
        logger.info(f"Payment Transaction: {log_entry}")
        return log_entry


class WorkerEarningsCalculator:
    """Calculate and track worker earnings across all payments."""
    
    @staticmethod
    def calculate_total_earnings(worker_profile) -> Dict:
        """
        Calculate complete earnings breakdown for worker.
        
        Returns:
            Dict with pending, available, withdrawn, and total
        """
        return {
            'pending_earnings': worker_profile.pending_earnings,
            'available_earnings': worker_profile.available_earnings,
            'withdrawn_earnings': worker_profile.withdrawn_earnings,
            'total_earned': (
                worker_profile.pending_earnings +
                worker_profile.available_earnings +
                worker_profile.withdrawn_earnings
            ),
        }
    
    @staticmethod
    def calculate_platform_revenue(start_date=None, end_date=None) -> Decimal:
        """
        Calculate total platform commission/revenue.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            Total platform commission amount
        """
        from .models import Payment
        
        query = Payment.objects.filter(payment_status='Verified')
        
        if start_date:
            query = query.filter(verified_date__gte=start_date)
        if end_date:
            query = query.filter(verified_date__lte=end_date)
        
        total = query.aggregate(total=models.Sum('platform_commission'))['total'] or Decimal('0')
        return total
    
    @staticmethod
    def get_worker_monthly_earnings(worker, year: int, month: int) -> Dict:
        """
        Get worker's earnings for specific month.
        
        Returns:
            Dict with payment count, total earned, completed jobs
        """
        from .models import Payment
        from django.db.models import Q
        from datetime import date
        
        # Get last day of month
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        
        first_day = date(year, month, 1)
        
        payments = Payment.objects.filter(
            Q(job__worker=worker) | Q(booking__worker=worker),
            payment_status='Verified',
            verified_date__gte=first_day,
            verified_date__lt=next_month
        )
        
        return {
            'year': year,
            'month': month,
            'payment_count': payments.count(),
            'total_earned': payments.aggregate(total=models.Sum('worker_amount'))['total'] or Decimal('0'),
            'total_commission': payments.aggregate(total=models.Sum('platform_commission'))['total'] or Decimal('0'),
        }
