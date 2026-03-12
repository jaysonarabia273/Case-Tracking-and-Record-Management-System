from django import forms
from django.contrib.auth.models import User
from .models import Comment, Appointment, Case
from django import forms
from .models import GuidanceSession
from .models import StudentEvaluation, Profile

class UserSignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    student_number = forms.CharField(max_length=20, required=True, help_text="Your student ID number")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def clean_student_number(self):
        student_number = self.cleaned_data.get('student_number')
        # Check if student number already exists
        if Profile.objects.filter(student_number=student_number).exists():
            raise forms.ValidationError("This student number is already registered.")
        return student_number

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'description', 'status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your comment here...'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date']




class GuidanceSessionForm(forms.ModelForm):
    class Meta:
        model = GuidanceSession
        fields = ['reason',  'preferred_counselor', 'concern_description']
        widgets = {
            'concern_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please provide a brief description of what you\'d like to discuss...'}),
        }











class StudentEvaluationForm(forms.ModelForm):
    class Meta:
        model = StudentEvaluation
        fields = [
            'student', 'evaluation_date', 'reason_for_session', 
            'hearing_frequency', 'detailed_assessment', 'severity_level', 
            'follow_up_required'
        ]
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'evaluation_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'required': True
            }),
            'reason_for_session': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'hearing_frequency': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'detailed_assessment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Provide detailed information about the incident, student\'s behavior, and recommended actions...',
                'required': True,
                'rows': 5
            }),
            'severity_level': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'follow_up_required': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show students in the dropdown
        self.fields['student'].queryset = Profile.objects.filter(user_type='student').order_by('user__first_name', 'user__last_name')
        
        # Set empty labels for better UX
        self.fields['student'].empty_label = "Select Student"
        self.fields['reason_for_session'].empty_label = "Select Offense Type"
        self.fields['hearing_frequency'].empty_label = "Select Hearing"
        self.fields['severity_level'].empty_label = "Select Severity"