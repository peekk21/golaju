from django import forms
from .models import User

class UserInitForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['age', 'sex'] # '__all__'
        widgets = {
            'age': forms.RadioSelect(),
            'sex': forms.RadioSelect(),  # 라디오 버튼 필드에 required=True 추가
        }

    def __init__(self, *args, **kwargs):
        super(UserInitForm, self).__init__(*args, **kwargs)
        self.fields['age'].required = True
        self.fields['sex'].required = True
        
        '''
class SigninForm(forms.Form):
    아이디 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '10자 이내'}), max_length=10, required=True)
    닉네임 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '8자 이내 (선택사항)'}), max_length=8, required=False)
    비밀번호 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '20자 이내'}), max_length=20, required=True)
    비밀번호_확인 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '비밀번호 재입력'}), max_length=20, required=True)
'''

class SigninForm(forms.Form):
    아이디 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '10자 이내', 'style': 'width: 50%; height: 100%; transform: translate(25%, 60%); font-size: 28px; border: none; outline: none; background: transparent; color: #1B0900; font-family: "Pretendard";'}),
        max_length=10,
        required=True,
        error_messages={'required': '아이디를 입력하세요.'}
    )
    닉네임 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '8자 이내', 'style': 'width: 50%; height: 100%; transform: translate(25%, 60%); font-size: 28px; border: none; outline: none; background: transparent; color: #1B0900; font-family: "Pretendard";'}),
        max_length=8,
        required=False
    )
    비밀번호 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '20자 이내', 'style': 'width: 50%; height: 100%; transform: translate(25%, 60%); font-size: 28px; border: none; outline: none; background: transparent; color: #1B0900; font-family: "Pretendard";'}),
        max_length=20,
        required=True,
        error_messages={'required': '비밀번호를 입력하세요.'}
    )
    비밀번호_확인 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '비밀번호 재입력', 'style': 'width: 50%; height: 100%; transform: translate(25%, 60%); font-size: 28px; border: none; outline: none; background: transparent; color: #1B0900; font-family: "Pretendard";'}),
        max_length=20,
        required=True,
        error_messages={'required': '비밀번호 확인을 입력하세요.'}
    )


    def clean_아이디(self):
        input_id = self.cleaned_data['아이디']
        
        if User.objects.filter(login_id=input_id).exists():
            self.add_error(None, forms.ValidationError('이미 사용 중인 아이디입니다.'))
        return input_id
    
    def clean_닉네임(self):
        input_username = self.cleaned_data['닉네임']
        
        if not input_username:
            return None
        
        if User.objects.filter(username=input_username).exists():
            self.add_error(None, forms.ValidationError('이미 사용 중인 닉네임입니다.'))
        return input_username


    