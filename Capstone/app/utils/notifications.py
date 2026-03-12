"""
Comprehensive Notification System Utilities
Handles all notification creation and management for the case tracking system
"""

from django.urls import reverse
from app.models import Notification, Profile


class NotificationManager:
    """
    Centralized notification management system
    """
    
    # Notification type configurations with templates
    NOTIFICATION_CONFIGS = {
        # Session Notifications
        'session_requested': {
            'type': 'session_request',
            'title': 'New Session Request',
            'message_template': '{student} has requested a guidance session for {reason}',
            'icon': 'calendar-plus',
            'color': 'blue',
            'priority': 'high'
        },
        'session_approved': {
            'type': 'session_approved',
            'title': 'Session Request Approved',
            'message_template': 'Your session request has been approved by {counselor}',
            'icon': 'check-circle',
            'color': 'green',
            'priority': 'high'
        },
        'session_rejected': {
            'type': 'session_cancelled',
            'title': 'Session Request Rejected',
            'message_template': 'Your session request was rejected. Reason: {reason}',
            'icon': 'times-circle',
            'color': 'red',
            'priority': 'high'
        },
        'session_scheduled': {
            'type': 'session_scheduled',
            'title': 'Session Scheduled',
            'message_template': 'Your session has been scheduled for {date} at {time}',
            'icon': 'calendar-check',
            'color': 'green',
            'priority': 'high'
        },
        'session_rescheduled': {
            'type': 'session_scheduled',
            'title': 'Session Rescheduled',
            'message_template': 'Your session has been rescheduled to {date} at {time}',
            'icon': 'calendar-alt',
            'color': 'orange',
            'priority': 'high'
        },
        'session_completed': {
            'type': 'session_completed',
            'title': 'Session Completed',
            'message_template': 'Your session with {counselor} has been marked as completed',
            'icon': 'check-double',
            'color': 'green',
            'priority': 'medium'
        },
        'session_cancelled': {
            'type': 'session_cancelled',
            'title': 'Session Cancelled',
            'message_template': 'Your scheduled session has been cancelled. {reason}',
            'icon': 'ban',
            'color': 'red',
            'priority': 'high'
        },
        'session_reminder': {
            'type': 'reminder',
            'title': 'Upcoming Session Reminder',
            'message_template': 'Reminder: You have a session scheduled for {date} at {time}',
            'icon': 'clock',
            'color': 'blue',
            'priority': 'medium'
        },
        
        # Case Notifications
        'case_created': {
            'type': 'case_created',
            'title': 'New Case Created',
            'message_template': 'A new case has been created for {student}: {title}',
            'icon': 'folder-plus',
            'color': 'blue',
            'priority': 'high'
        },
        'case_assigned': {
            'type': 'case_assigned',
            'title': 'Case Assigned to You',
            'message_template': 'You have been assigned to case: {title}',
            'icon': 'user-tag',
            'color': 'green',
            'priority': 'high'
        },
        'case_updated': {
            'type': 'case_updated',
            'title': 'Case Updated',
            'message_template': 'Case "{title}" has been updated by {updater}',
            'icon': 'edit',
            'color': 'orange',
            'priority': 'medium'
        },
        'case_status_changed': {
            'type': 'case_updated',
            'title': 'Case Status Changed',
            'message_template': 'Case "{title}" status changed to: {status}',
            'icon': 'exchange-alt',
            'color': 'blue',
            'priority': 'high'
        },
        'case_resolved': {
            'type': 'case_resolved',
            'title': 'Case Resolved',
            'message_template': 'Your case "{title}" has been resolved',
            'icon': 'check-circle',
            'color': 'green',
            'priority': 'high'
        },
        'case_comment_added': {
            'type': 'comment_added',
            'title': 'New Comment on Case',
            'message_template': '{commenter} added a comment to case: {title}',
            'icon': 'comment',
            'color': 'blue',
            'priority': 'medium'
        },
        
        # Student Actions
        'student_registered': {
            'type': 'session_request',
            'title': 'New Student Registered',
            'message_template': '{student} has registered and may need guidance',
            'icon': 'user-plus',
            'color': 'green',
            'priority': 'low'
        },
        
        # Report/Document Notifications
        'report_generated': {
            'type': 'case_updated',
            'title': 'Report Generated',
            'message_template': 'A new report has been generated: {report_type}',
            'icon': 'file-alt',
            'color': 'blue',
            'priority': 'medium'
        },
        
        # Urgent/Important
        'urgent_attention': {
            'type': 'reminder',
            'title': 'Urgent: Action Required',
            'message_template': '{message}',
            'icon': 'exclamation-triangle',
            'color': 'red',
            'priority': 'urgent'
        }
    }
    
    @staticmethod
    def create_notification(notification_key, recipient, sender=None, link=None, **kwargs):
        """
        Create a notification with proper formatting
        
        Args:
            notification_key: Key from NOTIFICATION_CONFIGS
            recipient: Profile object who will receive the notification
            sender: Profile object who triggered the notification (optional)
            link: URL link for the notification (optional)
            **kwargs: Additional parameters for message template formatting
        
        Returns:
            Notification object
        """
        if notification_key not in NotificationManager.NOTIFICATION_CONFIGS:
            raise ValueError(f"Invalid notification key: {notification_key}")
        
        config = NotificationManager.NOTIFICATION_CONFIGS[notification_key]
        
        # Format the message with provided kwargs
        message = config['message_template'].format(**kwargs)
        
        # Create the notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=config['type'],
            title=config['title'],
            message=message,
            link=link
        )
        
        return notification
    
    @staticmethod
    def notify_session_requested(session, counselor):
        """Notify counselor when a student requests a session"""
        return NotificationManager.create_notification(
            'session_requested',
            recipient=counselor,
            sender=session.student,
            link=reverse('counselor_session_detail', args=[session.id]),
            student=session.student.user.get_full_name(),
            reason=session.get_reason_display()
        )
    
    @staticmethod
    def notify_session_approved(session):
        """Notify student when their session is approved"""
        return NotificationManager.create_notification(
            'session_approved',
            recipient=session.student,
            sender=session.assigned_counselor,
            link=reverse('session_detail_view', args=[session.id]),
            counselor=session.assigned_counselor.user.get_full_name()
        )
    
    @staticmethod
    def notify_session_rejected(session, reason="No reason provided"):
        """Notify student when their session is rejected"""
        return NotificationManager.create_notification(
            'session_rejected',
            recipient=session.student,
            sender=session.assigned_counselor,
            link=reverse('session_detail_view', args=[session.id]),
            reason=reason
        )
    
    @staticmethod
    def notify_session_scheduled(session):
        """Notify student when session is scheduled"""
        return NotificationManager.create_notification(
            'session_scheduled',
            recipient=session.student,
            sender=session.assigned_counselor,
            link=reverse('session_detail_view', args=[session.id]),
            date=session.scheduled_date.strftime('%B %d, %Y'),
            time=session.scheduled_time.strftime('%I:%M %p')
        )
    
    @staticmethod
    def notify_session_rescheduled(session):
        """Notify student when session is rescheduled"""
        return NotificationManager.create_notification(
            'session_rescheduled',
            recipient=session.student,
            sender=session.assigned_counselor,
            link=reverse('session_detail_view', args=[session.id]),
            date=session.scheduled_date.strftime('%B %d, %Y'),
            time=session.scheduled_time.strftime('%I:%M %p')
        )
    
    @staticmethod
    def notify_session_completed(session):
        """Notify student when session is completed"""
        return NotificationManager.create_notification(
            'session_completed',
            recipient=session.student,
            sender=session.assigned_counselor,
            link=reverse('session_detail_view', args=[session.id]),
            counselor=session.assigned_counselor.user.get_full_name()
        )
    
    @staticmethod
    def notify_session_cancelled(session, reason="No reason provided"):
        """Notify student when session is cancelled"""
        return NotificationManager.create_notification(
            'session_cancelled',
            recipient=session.student,
            sender=session.assigned_counselor,
            link=reverse('session_detail_view', args=[session.id]),
            reason=reason
        )
    
    @staticmethod
    def notify_case_created(case, notify_counselor=True):
        """Notify counselor when a new case is created"""
        if notify_counselor and case.counselor:
            return NotificationManager.create_notification(
                'case_created',
                recipient=case.counselor,
                sender=case.student,
                link=reverse('counselor_case_detail', args=[case.id]),
                student=case.student.user.get_full_name(),
                title=case.title
            )
    
    @staticmethod
    def notify_case_assigned(case):
        """Notify counselor when assigned to a case"""
        return NotificationManager.create_notification(
            'case_assigned',
            recipient=case.counselor,
            link=reverse('counselor_case_detail', args=[case.id]),
            title=case.title
        )
    
    @staticmethod
    def notify_case_updated(case, updated_by):
        """Notify student when their case is updated"""
        return NotificationManager.create_notification(
            'case_updated',
            recipient=case.student,
            sender=updated_by,
            link=reverse('case_detail_view', args=[case.id]),
            title=case.title,
            updater=updated_by.user.get_full_name()
        )
    
    @staticmethod
    def notify_case_status_changed(case, new_status):
        """Notify student when case status changes"""
        return NotificationManager.create_notification(
            'case_status_changed',
            recipient=case.student,
            sender=case.counselor,
            link=reverse('case_detail_view', args=[case.id]),
            title=case.title,
            status=case.get_status_display()
        )
    
    @staticmethod
    def notify_case_resolved(case):
        """Notify student when their case is resolved"""
        return NotificationManager.create_notification(
            'case_resolved',
            recipient=case.student,
            sender=case.counselor,
            link=reverse('case_detail_view', args=[case.id]),
            title=case.title
        )
    
    @staticmethod
    def notify_case_comment(case, commenter, notify_recipient):
        """Notify about new comment on case"""
        return NotificationManager.create_notification(
            'case_comment_added',
            recipient=notify_recipient,
            sender=commenter,
            link=reverse('case_detail_view', args=[case.id]),
            commenter=commenter.user.get_full_name(),
            title=case.title
        )
    
    @staticmethod
    def notify_urgent(recipient, message, sender=None, link=None):
        """Send urgent notification"""
        return NotificationManager.create_notification(
            'urgent_attention',
            recipient=recipient,
            sender=sender,
            link=link,
            message=message
        )
    
    @staticmethod
    def get_unread_count(user_profile):
        """Get count of unread notifications for a user"""
        return Notification.objects.filter(
            recipient=user_profile,
            is_read=False
        ).count()
    
    @staticmethod
    def get_recent_notifications(user_profile, limit=5):
        """Get recent notifications for a user"""
        return Notification.objects.filter(
            recipient=user_profile
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a single notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_read(user_profile):
        """Mark all notifications as read for a user"""
        return Notification.objects.filter(
            recipient=user_profile,
            is_read=False
        ).update(is_read=True)

    # ========================================================================
    # HEARING NOTIFICATIONS
    # ========================================================================
    
    @staticmethod
    def notify_hearing_scheduled(hearing, participant, role):
        """Notify participant about scheduled hearing"""
        messages = {
            'presiding_officer': f'You have been assigned as presiding officer for hearing {hearing.hearing_number}',
            'panel_member': f'You have been invited to join the hearing panel for {hearing.title}',
            'respondent': f'A hearing has been scheduled regarding your case: {hearing.title}',
            'complainant': f'A hearing has been scheduled for your complaint: {hearing.title}',
            'witness': f'You have been called as a witness for hearing {hearing.hearing_number}',
            'advisor': f'You have been invited as an advisor for hearing {hearing.hearing_number}',
        }
        
        return NotificationManager.create_notification(
            'session_scheduled',  # Reuse session_scheduled type
            recipient=participant,
            sender=hearing.created_by,
            link=f'/counselor/hearing/{hearing.id}/',
            date=hearing.scheduled_date.strftime('%B %d, %Y'),
            time=hearing.scheduled_time.strftime('%I:%M %p')
        )
    
    @staticmethod
    def notify_hearing_rescheduled(hearing, participants_list):
        """Notify all participants about rescheduled hearing"""
        notifications = []
        for participant in participants_list:
            notif = NotificationManager.create_notification(
                'session_rescheduled',
                recipient=participant,
                sender=hearing.presiding_officer,
                link=f'/counselor/hearing/{hearing.id}/',
                date=hearing.scheduled_date.strftime('%B %d, %Y'),
                time=hearing.scheduled_time.strftime('%I:%M %p')
            )
            notifications.append(notif)
        return notifications
    
    @staticmethod
    def notify_hearing_cancelled(hearing, participants_list, reason=""):
        """Notify all participants about cancelled hearing"""
        notifications = []
        for participant in participants_list:
            notif = NotificationManager.create_notification(
                'session_cancelled',
                recipient=participant,
                sender=hearing.presiding_officer,
                link=f'/counselor/hearing/{hearing.id}/',
                reason=reason or "No reason provided"
            )
            notifications.append(notif)
        return notifications
    
    @staticmethod
    def notify_hearing_reminder(hearing, participant, hours_before):
        """Send reminder before hearing"""
        return NotificationManager.create_notification(
            'session_reminder',
            recipient=participant,
            sender=hearing.presiding_officer,
            link=f'/counselor/hearing/{hearing.id}/',
            date=hearing.scheduled_date.strftime('%B %d, %Y'),
            time=hearing.scheduled_time.strftime('%I:%M %p')
        )
    
    @staticmethod
    def notify_hearing_evidence_uploaded(hearing, uploader, relevant_parties):
        """Notify relevant parties when new evidence is uploaded"""
        notifications = []
        for party in relevant_parties:
            if party != uploader:  # Don't notify the uploader
                notif = NotificationManager.create_notification(
                    'case_comment_added',  # Reuse comment notification
                    recipient=party,
                    sender=uploader,
                    link=f'/counselor/hearing/{hearing.id}/',
                    commenter=uploader.user.get_full_name(),
                    title=f'Evidence uploaded for {hearing.hearing_number}'
                )
                notifications.append(notif)
        return notifications
    
    @staticmethod
    def notify_hearing_decision_posted(hearing):
        """Notify respondent and relevant parties about decision"""
        notifications = []
        
        # Notify respondent
        notif = NotificationManager.create_notification(
            'case_resolved',  # Reuse case resolved notification
            recipient=hearing.respondent,
            sender=hearing.presiding_officer,
            link=f'/counselor/hearing/{hearing.id}/',
            title=f'Decision posted for {hearing.hearing_number}'
        )
        notifications.append(notif)
        
        # Notify complainant if exists
        if hearing.complainant:
            notif = NotificationManager.create_notification(
                'case_updated',
                recipient=hearing.complainant,
                sender=hearing.presiding_officer,
                link=f'/counselor/hearing/{hearing.id}/',
                title=hearing.title,
                updater=hearing.presiding_officer.user.get_full_name()
            )
            notifications.append(notif)
        
        return notifications
    
    @staticmethod
    def notify_hearing_appeal_filed(hearing, panel_members):
        """Notify panel members when appeal is filed"""
        notifications = []
        for member in panel_members:
            notif = NotificationManager.create_notification(
                'urgent_attention',
                recipient=member,
                sender=hearing.respondent,
                link=f'/counselor/hearing/{hearing.id}/',
                message=f'An appeal has been filed for hearing {hearing.hearing_number}'
            )
            notifications.append(notif)
        return notifications
