"""
Report Generation Service
Generate financial, payment, worker, customer, and job reports in Excel, CSV, and PDF formats.
"""

import csv
import io
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict

from django.db.models import Sum, Count, Avg, Q
from django.http import HttpResponse
from django.utils import timezone


class ReportGenerator:
    """Base class for generating reports in various formats."""
    
    @staticmethod
    def generate_csv_response(filename: str, headers: List[str], rows: List[List]) -> HttpResponse:
        """Generate CSV file response."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(rows)
        
        return response
    
    @staticmethod
    def get_excel_buffer(filename: str, sheet_name: str, headers: List[str], rows: List[List]) -> io.BytesIO:
        """
        Generate Excel file buffer.
        Requires: pip install openpyxl
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name
            
            # Add headers with styling
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
            
            # Add data rows
            for row_idx, row_data in enumerate(rows, 2):
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.alignment = Alignment(horizontal="left")
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
            
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return buffer
        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
    
    @staticmethod
    def generate_excel_response(filename: str, sheet_name: str, headers: List[str], rows: List[List]) -> HttpResponse:
        """Generate Excel file response."""
        buffer = ReportGenerator.get_excel_buffer(filename, sheet_name, headers, rows)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        return response
    
    @staticmethod
    def generate_pdf_response(filename: str, title: str, content_html: str) -> HttpResponse:
        """
        Generate PDF file response.
        Requires: pip install reportlab
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from html.parser import HTMLParser
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#366092'),
                spaceAfter=30,
                alignment=1  # center
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Add timestamp
            timestamp_style = ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=0  # left
            )
            story.append(Paragraph(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # Parse HTML content
            # This is a simplified version - in production, use more sophisticated HTML parsing
            story.append(Paragraph(content_html, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            response = HttpResponse(buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response
        except ImportError:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")


class PaymentReportGenerator:
    """Generate payment-related reports."""
    
    @staticmethod
    def get_payment_data(start_date=None, end_date=None, status='Verified'):
        """Fetch payment data for report."""
        from payments.models import Payment
        
        query = Payment.objects.filter(payment_status=status)
        
        if start_date:
            query = query.filter(payment_date__gte=start_date)
        if end_date:
            query = query.filter(payment_date__lte=end_date)
        
        return query.select_related('job__customer', 'job__worker', 'booking__customer', 'booking__worker')
    
    @staticmethod
    def generate_payment_report(format_type='csv', start_date=None, end_date=None):
        """Generate payment report."""
        payments = PaymentReportGenerator.get_payment_data(start_date, end_date)
        
        headers = [
            'Payment ID',
            'Transaction Date',
            'Customer Amount',
            'Platform Commission',
            'Worker Amount',
            'Payment Method',
            'Transaction ID',
            'Payment Status',
            'Customer',
            'Worker',
            'Job/Booking',
        ]
        
        rows = []
        for payment in payments:
            customer = payment.job.customer if payment.job else payment.booking.customer
            worker = payment.job.worker if payment.job else payment.booking.worker
            job_info = f"Job #{payment.job.pk}" if payment.job else f"Booking #{payment.booking.pk}"
            
            rows.append([
                payment.pk,
                payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                f"৳{payment.customer_amount}",
                f"৳{payment.platform_commission}",
                f"৳{payment.worker_amount}",
                payment.payment_method,
                payment.transaction_id or 'N/A',
                payment.payment_status,
                customer.get_full_name() if customer else 'N/A',
                worker.get_full_name() if worker else 'N/A',
                job_info,
            ])
        
        filename = f"payment_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format_type == 'excel':
            return ReportGenerator.generate_excel_response(
                filename, 'Payments', headers, rows
            )
        else:  # csv
            return ReportGenerator.generate_csv_response(filename, headers, rows)


class WorkerReportGenerator:
    """Generate worker and earnings reports."""
    
    @staticmethod
    def get_worker_data():
        """Fetch worker data for report."""
        from workers.models import WorkerProfile
        from reviews.models import Review
        from django.db.models import Avg
        
        return WorkerProfile.objects.annotate(
            avg_rating=Avg('user__reviews_received__rating'),
            job_count=Count('user__worker_jobs')
        ).select_related('user')
    
    @staticmethod
    def generate_worker_report(format_type='csv'):
        """Generate worker report with earnings."""
        workers = WorkerReportGenerator.get_worker_data()
        
        headers = [
            'Worker ID',
            'Name',
            'Email',
            'Phone',
            'Verification Status',
            'Completed Jobs',
            'Average Rating',
            'Pending Earnings',
            'Available Earnings',
            'Withdrawn Earnings',
            'Total Earnings',
            'bKash Number',
            'Nagad Number',
            'Payout Method',
        ]
        
        rows = []
        for worker in workers:
            earnings = worker.get_earnings_breakdown()
            
            rows.append([
                worker.user.pk,
                worker.user.get_full_name(),
                worker.user.email,
                worker.user.phone if hasattr(worker.user, 'phone') else 'N/A',
                worker.verification_status,
                worker.completed_jobs,
                f"{worker.average_rating:.2f}" if worker.average_rating else 'N/A',
                f"৳{earnings['pending']}",
                f"৳{earnings['available']}",
                f"৳{earnings['withdrawn']}",
                f"৳{earnings['total_earned']}",
                worker.bkash_number or 'N/A',
                worker.nagad_number or 'N/A',
                worker.payout_method or 'Not Set',
            ])
        
        filename = f"worker_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format_type == 'excel':
            return ReportGenerator.generate_excel_response(
                filename, 'Workers', headers, rows
            )
        else:  # csv
            return ReportGenerator.generate_csv_response(filename, headers, rows)


class JobReportGenerator:
    """Generate job and service reports."""
    
    @staticmethod
    def get_job_data(status=None):
        """Fetch job data for report."""
        from bookings.models import Job
        
        query = Job.objects.all()
        if status:
            query = query.filter(status=status)
        
        return query.select_related('customer', 'worker', 'service_request')
    
    @staticmethod
    def generate_job_report(format_type='csv', status=None):
        """Generate job report."""
        jobs = JobReportGenerator.get_job_data(status)
        
        headers = [
            'Job ID',
            'Title',
            'Customer',
            'Worker',
            'Status',
            'Scheduled Date',
            'Proposed Price',
            'Final Price',
            'Created Date',
            'Completed Date',
        ]
        
        rows = []
        for job in jobs:
            rows.append([
                job.pk,
                job.title,
                job.customer.get_full_name(),
                job.worker.get_full_name(),
                job.status,
                job.scheduled_date.strftime('%Y-%m-%d') if job.scheduled_date else 'N/A',
                f"৳{job.proposed_price}" if job.proposed_price else 'N/A',
                f"৳{job.final_price}" if job.final_price else 'N/A',
                job.created_at.strftime('%Y-%m-%d %H:%M'),
                job.updated_at.strftime('%Y-%m-%d %H:%M'),
            ])
        
        filename = f"job_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format_type == 'excel':
            return ReportGenerator.generate_excel_response(
                filename, 'Jobs', headers, rows
            )
        else:  # csv
            return ReportGenerator.generate_csv_response(filename, headers, rows)


class FinancialReportGenerator:
    """Generate comprehensive financial reports."""
    
    @staticmethod
    def generate_financial_summary(start_date=None, end_date=None):
        """Generate financial summary report."""
        from payments.models import Payment
        from bookings.models import Job
        
        # Default to current month
        if not start_date:
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = timezone.now()
        
        # Get verified payments in date range
        payments = Payment.objects.filter(
            payment_status='Verified',
            verified_date__gte=start_date,
            verified_date__lte=end_date
        )
        
        total_customer_amount = payments.aggregate(Sum('customer_amount'))['customer_amount__sum'] or Decimal('0')
        total_commission = payments.aggregate(Sum('platform_commission'))['platform_commission__sum'] or Decimal('0')
        total_worker_earnings = payments.aggregate(Sum('worker_amount'))['worker_amount__sum'] or Decimal('0')
        
        # Get job statistics
        completed_jobs = Job.objects.filter(
            status='COMPLETED',
            updated_at__gte=start_date,
            updated_at__lte=end_date
        ).count()
        
        cancelled_jobs = Job.objects.filter(
            status='CANCELLED',
            updated_at__gte=start_date,
            updated_at__lte=end_date
        ).count()
        
        return {
            'period_start': start_date,
            'period_end': end_date,
            'total_transactions': payments.count(),
            'total_customer_amount': total_customer_amount,
            'total_platform_commission': total_commission,
            'total_worker_earnings': total_worker_earnings,
            'completed_jobs': completed_jobs,
            'cancelled_jobs': cancelled_jobs,
            'average_transaction': total_customer_amount / payments.count() if payments.count() > 0 else Decimal('0'),
        }
    
    @staticmethod
    def generate_daily_revenue_report(days=30):
        """Generate daily revenue report for last N days."""
        from payments.models import Payment
        
        headers = ['Date', 'Transactions', 'Total Amount', 'Commission', 'Worker Earnings']
        rows = []
        
        for i in range(days):
            date = timezone.now().date() - timedelta(days=i)
            payments = Payment.objects.filter(
                payment_status='Verified',
                verified_date__date=date
            )
            
            total_amount = payments.aggregate(Sum('customer_amount'))['customer_amount__sum'] or Decimal('0')
            total_commission = payments.aggregate(Sum('platform_commission'))['platform_commission__sum'] or Decimal('0')
            total_earnings = payments.aggregate(Sum('worker_amount'))['worker_amount__sum'] or Decimal('0')
            
            if payments.count() > 0 or i < 7:  # Show recent days even if no transactions
                rows.append([
                    date.strftime('%Y-%m-%d'),
                    payments.count(),
                    f"৳{total_amount}",
                    f"৳{total_commission}",
                    f"৳{total_earnings}",
                ])
        
        filename = f"daily_revenue_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        return ReportGenerator.generate_csv_response(filename, headers, rows)
    
    @staticmethod
    def generate_commission_report(format_type='csv', start_date=None, end_date=None):
        """Generate commission breakdown report."""
        from payments.models import Payment
        
        payments = Payment.objects.filter(payment_status='Verified')
        
        if start_date:
            payments = payments.filter(verified_date__gte=start_date)
        if end_date:
            payments = payments.filter(verified_date__lte=end_date)
        
        headers = [
            'Date',
            'Transaction ID',
            'Customer Amount',
            'Commission Rate',
            'Platform Commission',
            'Worker Earnings',
            'Worker Name',
        ]
        
        rows = []
        for payment in payments:
            worker = payment.job.worker if payment.job else payment.booking.worker
            rows.append([
                payment.verified_date.strftime('%Y-%m-%d %H:%M') if payment.verified_date else 'N/A',
                payment.transaction_id or 'N/A',
                f"৳{payment.customer_amount}",
                f"{payment.commission_rate}%",
                f"৳{payment.platform_commission}",
                f"৳{payment.worker_amount}",
                worker.get_full_name() if worker else 'N/A',
            ])
        
        filename = f"commission_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format_type == 'excel':
            return ReportGenerator.generate_excel_response(
                filename, 'Commission', headers, rows
            )
        else:
            return ReportGenerator.generate_csv_response(filename, headers, rows)
