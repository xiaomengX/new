from django import forms
class LoginForm(forms.Form):
    username=forms.CharField(label="用户名",max_length=128,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username",'autofocus': ''}))
    password=forms.CharField(label="密码",max_length=20,widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': "Password"}))
class RegisterForm(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Username'}))
    password = forms.CharField(label="密码", max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'password'}))
    confirmPassword = forms.CharField(label="确认密码", max_length=20, widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'confirmPassword'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control','placeholder':'email'}))
    sex=forms.ChoiceField(label='性别',choices=gender)
    # sex = forms.IntegerField(initial=2,widget=forms.RadioSelect(choices=gender,))
class ForgotForm(forms.Form):
    email=forms.EmailField(label="邮箱",widget=forms.TextInput(attrs={'class': 'form-control','placeholder':"Enter email address" ,'autofocus':"autofocus"}))
    # password=forms.CharField(label="密码",max_length=20,widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': "Password"}))
