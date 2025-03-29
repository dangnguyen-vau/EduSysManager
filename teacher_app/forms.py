from django import forms
from blockchain_app.models import Transaction

class TeacherTransactionForm(forms.ModelForm):
    private_key = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nhập khóa riêng tư để ký giao dịch'
        }),
        required=True,
        help_text='Khóa riêng tư của bạn để ký điểm số. Khóa này không được lưu trữ.'
    )
    
    class Meta:
        model = Transaction
        fields = ['student', 'course', 'score']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
        }
