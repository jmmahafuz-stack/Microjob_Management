"""
Utility functions for managing notifications and approval workflows.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Notification


class NotificationManager:
    """Helper class to create and manage notifications"""
    
    @staticmethod
    def notify_worker_approved(user):
        """Notify worker that their account has been approved"""
        Notification.create_notification(
            user=user,
            title='Worker Account Approved ✅',
            message='Congratulations! Your worker account has been approved by the admin. '
                    'You can now start accepting jobs.',
            notification_type='WORKER_APPROVED'
        )
        # Send email
        NotificationManager.send_email(
            user=user,
            subject='Your Worker Account Has Been Approved',
            template_name='notifications/email/worker_approved.html',
            context={'user': user}
        )
    
    @staticmethod
    def notify_worker_rejected(user, reason=''):
        """Notify worker that their account application was rejected"""
        message = 'Your worker account application has been rejected.'
        if reason:
            message += f' Reason: {reason}'
        
        Notification.create_notification(
            user=user,
            title='Worker Account Rejected ❌',
            message=message,
            notification_type='WORKER_REJECTED'
        )
        # Send email
        NotificationManager.send_email(
            user=user,
            subject='Your Worker Account Application Was Rejected',
            template_name='notifications/email/worker_rejected.html',
            context={'user': user, 'reason': reason}
        )
    
    @staticmethod
    def notify_worker_unavailable(customer, worker, job):
        """Notify customer that worker is unavailable at requested time"""
        Notification.create_notification(
            user=customer,
            title=f'Worker Unavailable at Requested Time',
            message=f'Worker {worker.get_full_name()} is not available at the requested date and time. '
                    f'Please select a different worker or adjust your schedule.',
            notification_type='JOB_WORKER_UNAVAILABLE',
            job=job,
            related_user=worker
        )
    
    @staticmethod
    def notify_job_conflict(worker, new_job):
        """Notify worker about a job time conflict"""
        Notification.create_notification(
            user=worker,
            title='Job Time Conflict Detected',
            message=f'The job "{new_job.title}" on {new_job.scheduled_date} conflicts with '
                    f'an already scheduled job. Please check your schedule.',
            notification_type='JOB_CONFLICT',
            job=new_job
        )
    
    @staticmethod
    def notify_job_completed(customer, worker, job):
        """Notify customer that a job has been completed"""
        Notification.create_notification(
            user=customer,
            title='Job Completed ✅',
            message=f'Your job "{job.title}" has been completed by {worker.get_full_name()}. '
                    f'Please review and provide payment.',
            notification_type='JOB_COMPLETED',
            job=job,
            related_user=worker
        )
    
    @staticmethod
    def notify_payment_received(worker, payment):
        """Notify worker that payment has been received"""
        Notification.create_notification(
            user=worker,
            title='Payment Received ✅',
            message=f'You have received payment of {payment.amount} for job "{payment.job.title}". '
                    f'The amount has been credited to your account.',
            notification_type='PAYMENT_VERIFIED',
            payment=payment
        )
    
    @staticmethod
    def notify_worker_applied(customer, application):
        """Notify customer that a worker has applied for their job request"""
        worker = application.worker
        Notification.create_notification(
            user=customer,
            title='New Worker Application',
            message=f'Worker {worker.get_full_name()} has applied for your job request "{application.service_request.title}" '
                    f'with a proposed price of {application.proposed_price}.',
            notification_type='WORKER_APPLIED',
            related_user=worker
        )
    
    @staticmethod
    def notify_application_accepted(worker, application):
        """Notify worker that their application has been accepted"""
        Notification.create_notification(
            user=worker,
            title='Application Accepted ✅',
            message=f'Your application for the job "{application.service_request.title}" has been accepted! '
                    f'Please contact the customer to arrange the details.',
            notification_type='APPLICATION_ACCEPTED'
        )
    
    @staticmethod
    def notify_application_rejected(worker, application, reason=''):
        """Notify worker that their application was rejected"""
        message = f'Your application for the job "{application.service_request.title}" was not accepted.'
        if reason:
            message += f' {reason}'
        
        Notification.create_notification(
            user=worker,
            title='Application Not Accepted',
            message=message,
            notification_type='APPLICATION_REJECTED'
        )
    
    @staticmethod
    def send_email(user, subject, template_name, context):
        """Send notification email to user"""
        try:
            # Check if user has email notifications enabled
            if not user.receive_notifications:
                return False
            
            # Render email template
            html_message = render_to_string(template_name, context)
            
            # Send email
            send_mail(
                subject=subject,
                message='',  # Plain text version
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True
            )
            return True
        except Exception as e:
            print(f"Error sending email to {user.email}: {str(e)}")
            return False
