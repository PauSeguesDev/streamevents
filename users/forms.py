# Imports de Django per forms
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# Imports del meu model CustomUser
from .models import CustomUser

# Import per validacions amb expressions regulars
import re

# Formularis personalitzats per a la gestió d'usuaris

# Formulari de creació d'usuari
class CustomUserCreationForm(forms.ModelForm):
    """
    Formulari per a la creació d'un nou usuari personalitzat.
    """
    password1 = forms.CharField(
        label='Contrasenya',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contrasenya',
            }),
        help_text='La contrasenya ha de tenir almenys 8 caràcters, incloure una majúscula, una minúscula, un número i un caràcter espècial.'
    )
    password2 = forms.CharField(
        label='Contrasenya',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirma la Contrasenya',
            }),
        help_text='Introdueix la mateixa contrasenya per a verificació.'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean_usuarme(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Aquest nom d'usuari ja està en ús. Si us plau, tria'n un altre.")
        
        allowed_symbols = "@.+-_"
        for ch in username:
            if not (ch.isalnum() or ch in allowed_symbols):
                raise ValidationError(
                    "El nom d'usuari només pot contenir lletres, números i @/./+/-/_"
                )
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Aquest correu electrònic ja està en ús. Si us plau, utilitza'n un altre.")
        return email
    
    def clean(self):
        """
        Comprovem que les contrasenyes coincideixen i compleixen els requisits de seguretat.
        """
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')

        if pw1 and pw2 and pw1 != pw2:
            self.add_error('password2', 'Les contrasenyes no coincideixen.')

        if pw1:
            try:
                validate_password(pw1)
            except ValidationError as e:
                self.add_error('password1', e)

        return cleaned_data

    def save(self, commit=True):
        """
        Desa l'usuari amb la contrasenya encriptada.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# Formulari d'actualització d'usuari
class CustomUserUpdateForm(forms.ModelForm):
    """
    Formulari per editar perfils d'usuaris existents
    """
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Escriu una mica sobre tu...',
                'rows': 4,
            }),
        label='Biografia'
    )    
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(),
        label='Avatar',
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'display_name', 'bio', 'avatar']
        
# Formulari d'autenticació d'usuari
class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulari per a login dels usuaris.
    """
    username = forms.CharField(label="Nom d'usuari o correu electrònic")
    
    def clean(self):
        usuarme_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if usuarme_or_email and password:
            user = authenticate(self.request, username=usuarme_or_email, password=password)
            
            if user is None:
                try: 
                    user_obj = CustomUser.objects.get(email=usuarme_or_email)
                    user = authenticate(self.request, username=user_obj.username, password=password)
                    
                except CustomUser.DoesNotExist:
                    user = None
                
            if user is None:
                raise ValidationError(
                    "Nom d'usuari/correu electrònic o contrasenya incorrectes."
                )
                
            self.confirm_login_allowed(user)
            self.user_cache = user
            
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)
    

# Formulari de restabliment de contrasenya
class CustomPasswordResetForm(forms.Form):
    """
    Formulari per a restablir la contrasenya d'un usuari.
    """
    old_password = forms.CharField(
        label='Contrasenya Actual',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contrasenya Actual',
            })
    )
    
    new_password1 = forms.CharField(
        label='Contrasenya Nova',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Contrasenya Nova',
            }),
        help_text='La contrasenya ha de tenir almenys 8 caràcters, incloure una majúscula, una minúscula, un número i un caràcter espècial.'
    )
    new_password2 = forms.CharField(
        label='Contrasenya Nova',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirma la Contrasenya Nova',
            }),
        help_text='Introdueix la mateixa contrasenya per a verificació.'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user 
        
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']
    
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if old_password and new_password1 and new_password2:
            if not self.user.check_password(old_password):
                raise ValidationError("Contrasenya actual incorrecta.")
            
            if new_password1 != new_password2:
                raise ValidationError("Les contrasenyes no coincideixen.")
            
            try:
                validate_password(new_password1)
            except ValidationError as e:
                self.add_error('new_password1', e)
        
        return cleaned_data    
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user