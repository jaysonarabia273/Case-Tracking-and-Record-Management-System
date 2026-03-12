from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.crypto import get_random_string

class Profile(models.Model):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('counselor', 'Counselor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    student_number = models.CharField(max_length=20, blank=True, null=True)
    counselor_id = models.CharField(max_length=20, blank=True, null=True)
    year_level = models.CharField(max_length=10, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    

class EmailVerification(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return f"OTP for {self.user.username} - Verified: {self.verified}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        from django.conf import settings
        from datetime import timedelta
        expiry_time = self.created_at + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        return timezone.now() > expiry_time

class Case(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    student = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='cases',
        limit_choices_to={'user_type': 'student'}
    )
    counselor = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='assigned_cases',
        limit_choices_to={'user_type': 'counselor'}
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    sessions = models.ManyToManyField('GuidanceSession', related_name='cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Case ID: {self.id} - {self.title}"

    @property
    def student_name(self):
        return self.student.user.get_full_name() or self.student.user.username

    

class Comment(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.case}"

class Appointment(models.Model):
    student = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='appointments',
        limit_choices_to={'user_type': 'student'}
    )
    counselor = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='appointments_assigned',
        limit_choices_to={'user_type': 'counselor'}
    )
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=(('scheduled', 'Scheduled'), ('completed', 'Completed'), ('canceled', 'Canceled')), default='scheduled')

    def __str__(self):
        return f"Appointment {self.id} for {self.student.user.username} with {self.counselor.user.username} on {self.appointment_date}"
    


class GuidanceSession(models.Model):
    # Editable, unique title for the session (counselor can change). We keep app-level uniqueness.
    title = models.CharField(max_length=255, blank=True, default='')
    REASON_CHOICES = (
        ('academic', 'Academic Concerns'),
        ('personal', 'Personal Issues'),
        ('career', 'Career Planning'),
        ('mental_health', 'Mental Health Support'),
        ('other', 'Other')
    )   
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    
    student = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='sessions',
        limit_choices_to={'user_type': 'student'}
    )
    student_number = models.CharField(max_length=20, default='N/A')
    student_name = models.CharField(max_length=255, default='Not Specified')
    student_email = models.EmailField(default='no-email@example.com')
    student_year = models.CharField(max_length=20, default='Not Specified')
    student_course = models.CharField(max_length=100, default='Not Specified')
    student_section = models.CharField(max_length=20, default='Not Specified')
    offense_type = models.CharField(max_length=100, blank=True, null=True)
    offense_details = models.TextField(blank=True, null=True)
    incident_date = models.DateField(blank=True, null=True)  
    incident_time = models.TimeField(blank=True, null=True)
    severity = models.CharField(max_length=20, blank=True, null=True)
    witnesses = models.CharField(max_length=255, blank=True, null=True)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    concern_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    
    preferred_counselor = models.ForeignKey(
        Profile, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='preferred_sessions',
        limit_choices_to={'user_type': 'counselor'}
    )
    assigned_counselor = models.ForeignKey(
        Profile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_sessions',
        limit_choices_to={'user_type': 'counselor'}
    )

    case = models.OneToOneField(
        Case, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='guidance_session'
    )
    
    # Multiple participants support (e.g., group sessions, parent involvement)
    participants = models.ManyToManyField(
        Profile,
        related_name='participated_sessions',
        blank=True,
        help_text='Additional participants in this session (parents, other students, etc.)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session for {self.student.user.username} on {self.get_status_display()}"


class CaseStatus(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    )
    
    case_number = models.CharField(max_length=10, unique=True)
    student = models.ForeignKey(
        User,  # or Profile if you prefer to use your Profile model
        on_delete=models.CASCADE,
        related_name='cases'
    )
    subject = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate a unique case number if not already set
        if not self.case_number:
            self.case_number = self.generate_case_number()
        super().save(*args, **kwargs)
    
    def generate_case_number(self):
        """Generate a unique case number with format CS-XXXXX"""
        while True:
            case_number = f"CS-{get_random_string(5, '0123456789')}"
            if not CaseStatus.objects.filter(case_number=case_number).exists():
                return case_number
    
    def __str__(self):
        return f"Case #{self.case_number} - {self.student.username}"



class CaseUpdate(models.Model):
    case = models.ForeignKey(
        Case, 
        on_delete=models.CASCADE,
        related_name='updates'
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='case_updates'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.case.case_number} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class StudentEvaluation(models.Model):
    OFFENSE_CHOICES = [
        ('tardiness', 'Tardiness'),
        ('absence', 'Unexcused Absence'),
        ('misconduct', 'Academic Misconduct'),
        ('disruption', 'Classroom Disruption'),
        ('bullying', 'Bullying/Harassment'),
        ('violation', 'Code of Conduct Violation'),
        ('substance', 'Substance-related Issue'),
        ('other', 'Other'),
    ]
    
    HEARING_CHOICES = [
        ('1st', '1st Hearing'),
        ('2nd', '2nd Hearing'),
        ('3rd', '3rd Hearing'),
        ('4th', '4th Hearing (Final)'),
    ]
    
    SEVERITY_CHOICES = [
        ('minor', 'Minor Offense'),
        ('major', 'Major Offense'), 
        ('severe', 'Severe Offense'),
    ]
    
    FOLLOWUP_CHOICES = [
        ('none', 'No Follow-up Needed'),
        ('monitoring', 'Behavioral Monitoring'),
        ('counseling', 'Additional Counseling'),
        ('parent', 'Parent Conference'),
        ('disciplinary', 'Disciplinary Action'),
    ]
    
    student = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='conducted_evaluations')
    evaluation_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    reason_for_session = models.CharField(max_length=20, choices=OFFENSE_CHOICES)
    hearing_frequency = models.CharField(max_length=3, choices=HEARING_CHOICES)
    detailed_assessment = models.TextField()
    severity_level = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    follow_up_required = models.CharField(max_length=15, choices=FOLLOWUP_CHOICES, default='none')
    
    is_draft = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evaluation - {self.student.user.get_full_name()} ({self.evaluation_date})"
    
    def get_hearing_number(self):
        hearing_map = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4}
        return hearing_map.get(self.hearing_frequency, 0)

class EvaluationReport(models.Model):
    title = models.CharField(max_length=200)
    generated_by = models.ForeignKey('Profile', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    date_range_start = models.DateField()
    date_range_end = models.DateField()
    report_data = models.JSONField()  
    
    def __str__(self):
        return f"Report: {self.title} ({self.generated_at.strftime('%Y-%m-%d')})"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('session_request', 'Session Request'),
        ('session_approved', 'Session Approved'),
        ('session_scheduled', 'Session Scheduled'),
        ('session_completed', 'Session Completed'),
        ('session_cancelled', 'Session Cancelled'),
        ('case_created', 'Case Created'),
        ('case_updated', 'Case Updated'),
        ('case_assigned', 'Case Assigned'),
        ('case_resolved', 'Case Resolved'),
        ('comment_added', 'Comment Added'),
        ('reminder', 'Reminder'),
    )
    
    recipient = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.user.username}"


# ============================================================================
# HEARING MANAGEMENT MODELS
# ============================================================================

class Hearing(models.Model):
    """
    Formal hearing model for disciplinary cases, appeals, and resolution meetings.
    Unlike informal sessions, hearings are structured proceedings with official outcomes.
    """
    
    HEARING_TYPES = [
        ('disciplinary', 'Disciplinary Hearing'),
        ('appeal', 'Appeal Hearing'),
        ('resolution', 'Resolution Meeting'),
        ('investigation', 'Investigation Hearing'),
        ('review', 'Case Review Hearing'),
    ]
    
    HEARING_STATUS = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    
    VERDICT_CHOICES = [
        ('pending', 'Pending'),
        ('guilty', 'Guilty/Responsible'),
        ('not_guilty', 'Not Guilty/Not Responsible'),
        ('dismissed', 'Dismissed'),
        ('referred', 'Referred to Another Body'),
    ]
    
    MODE_CHOICES = [
        ('in_person', 'In-Person'),
        ('online', 'Online/Virtual'),
        ('hybrid', 'Hybrid'),
    ]
    
    # Basic Information
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='hearings',
        help_text='The case this hearing is associated with'
    )
    hearing_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique identifier (e.g., H-2024-001)'
    )
    title = models.CharField(max_length=200)
    hearing_type = models.CharField(max_length=20, choices=HEARING_TYPES)
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    estimated_duration = models.IntegerField(
        help_text='Duration in minutes',
        default=60
    )
    location = models.CharField(max_length=200)
    mode = models.CharField(max_length=15, choices=MODE_CHOICES, default='in_person')
    meeting_link = models.URLField(blank=True, null=True, help_text='Link for online hearings')
    
    # Participants
    presiding_officer = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='hearings_presided',
        help_text='Person conducting the hearing'
    )
    panel_members = models.ManyToManyField(
        Profile,
        related_name='hearings_panel',
        blank=True,
        help_text='Panel members/committee'
    )
    respondent = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='hearings_respondent',
        help_text='Student or person being heard'
    )
    complainant = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        related_name='hearings_complainant',
        null=True,
        blank=True,
        help_text='Person filing complaint (optional)'
    )
    witnesses = models.ManyToManyField(
        Profile,
        related_name='hearings_witness',
        blank=True,
        help_text='Witnesses to be called'
    )
    advisors = models.ManyToManyField(
        Profile,
        related_name='hearings_advisor',
        blank=True,
        help_text='Advisors (parents, guardians, support persons)'
    )
    
    # Documentation
    agenda = models.TextField(help_text='Hearing agenda/outline')
    charges = models.TextField(
        blank=True,
        help_text='Formal charges or allegations'
    )
    
    # Status and Results
    status = models.CharField(max_length=20, choices=HEARING_STATUS, default='scheduled')
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, default='pending')
    decision = models.TextField(
        blank=True,
        help_text='Formal decision and reasoning'
    )
    sanctions = models.JSONField(
        default=list,
        blank=True,
        help_text='List of sanctions/consequences imposed'
    )
    minutes = models.TextField(
        blank=True,
        help_text='Official minutes of the hearing'
    )
    minutes_finalized = models.BooleanField(default=False)
    
    # Appeal
    appeal_deadline = models.DateField(null=True, blank=True)
    appeal_filed = models.BooleanField(default=False)
    appeal_notes = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='hearings_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['hearing_number']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.hearing_number}: {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.hearing_number:
            # Auto-generate hearing number
            from datetime import datetime
            year = datetime.now().year
            last_hearing = Hearing.objects.filter(
                hearing_number__startswith=f'H-{year}-'
            ).order_by('-hearing_number').first()
            
            if last_hearing:
                last_num = int(last_hearing.hearing_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.hearing_number = f'H-{year}-{new_num:03d}'
        
        super().save(*args, **kwargs)
    
    def get_all_participants(self):
        """Get all participants as a list with their roles"""
        participants = []
        
        participants.append({
            'profile': self.presiding_officer,
            'role': 'Presiding Officer'
        })
        
        for member in self.panel_members.all():
            participants.append({'profile': member, 'role': 'Panel Member'})
        
        participants.append({
            'profile': self.respondent,
            'role': 'Respondent'
        })
        
        if self.complainant:
            participants.append({
                'profile': self.complainant,
                'role': 'Complainant'
            })
        
        for witness in self.witnesses.all():
            participants.append({'profile': witness, 'role': 'Witness'})
        
        for advisor in self.advisors.all():
            participants.append({'profile': advisor, 'role': 'Advisor'})
        
        return participants


class HearingEvidence(models.Model):
    """Evidence and documentation submitted for a hearing"""
    
    EVIDENCE_TYPES = [
        ('document', 'Document'),
        ('photo', 'Photo/Image'),
        ('video', 'Video'),
        ('audio', 'Audio Recording'),
        ('testimony', 'Written Testimony'),
        ('other', 'Other'),
    ]
    
    hearing = models.ForeignKey(
        Hearing,
        on_delete=models.CASCADE,
        related_name='evidence'
    )
    submitted_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evidence_submitted'
    )
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='hearings/evidence/%Y/%m/')
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = 'Hearing evidence'
    
    def __str__(self):
        return f"{self.title} ({self.hearing.hearing_number})"


class HearingMinutes(models.Model):
    """Official minutes/notes from hearing proceedings"""
    
    hearing = models.ForeignKey(
        Hearing,
        on_delete=models.CASCADE,
        related_name='minutes_entries'
    )
    recorded_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = 'Hearing minutes'
    
    def __str__(self):
        return f"Minutes for {self.hearing.hearing_number} at {self.timestamp}"


class HearingAttendance(models.Model):
    """Track attendance and participation in hearings"""
    
    ROLE_CHOICES = [
        ('presiding_officer', 'Presiding Officer'),
        ('panel_member', 'Panel Member'),
        ('respondent', 'Respondent'),
        ('complainant', 'Complainant'),
        ('witness', 'Witness'),
        ('advisor', 'Advisor'),
        ('observer', 'Observer'),
    ]
    
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('confirmed', 'Confirmed'),
        ('attended', 'Attended'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
    ]
    
    hearing = models.ForeignKey(
        Hearing,
        on_delete=models.CASCADE,
        related_name='attendance'
    )
    participant = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    
    arrived_at = models.DateTimeField(null=True, blank=True)
    departed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['hearing', 'participant', 'role']
        ordering = ['role', 'participant']
    
    def __str__(self):
        return f"{self.participant.user.get_full_name()} - {self.get_role_display()} ({self.hearing.hearing_number})"
