from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomAuthenticationForm, CustomPasswordResetForm
from .models import CustomUser

# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            messages.success(request, "El teu compte s'ha creat correctament!")
            
            return redirect('home')

        else: 
            messages.error(request, 'Hi ha errors en el formulari. Si us plau, revisa-ho i torna-ho a intentar.')
    
    else: 
        form = CustomUserCreationForm()
    
    return render(request, "registration/register.html", {
        'form': form,
        'title': 'Crear un compte nou'
    })

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            messages.success(request, "Has iniciat sessió correctament!")
            
            return redirect('home')
        
        else:
            messages.error(request, 'Nom d\'usuari o contrasenya incorrectes. Si us plau, torna-ho a intentar.')
            
    else:
        form = CustomAuthenticationForm()
        
    return render(request, "registration/login.html", {
        'form': form,
        'title': 'Iniciar sessió'
    }) 

def logout_view(request):
    logout(request)
    messages.info(request, "Has tancat la sessió correctament.")
    return redirect("home")

@login_required
def profile_view(request):
    user = request.user
    return render(request, "users/profile.html", {
        'profile_user': user,
        'title': 'El meu perfil'
    })

@login_required
def edit_profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "El teu perfil s'ha actualitzat correctament!")
            return redirect('users:public_profile', username=request.user.username)
        
        else:
            messages.error(request, 'Hi ha errors en el formulari. Si us plau, revisa-ho i torna-ho a intentar.')
    else:
        form = CustomUserUpdateForm(instance=user)
        
    return render(request, "users/edit_profile.html", {
        'form': form,
        'title': 'Editar perfil'
    })

@login_required
def public_profile_view(request, username):
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        messages.error(request, "L'usuari sol·licitat no existeix.")
        return redirect('home')
    
    return render(request, "users/public_profile.html", {
        'profile_user': user,
        'title': f'Perfil de {user.username}'
    })
    
@login_required
def change_password_view(request):
    user = request.user

    if request.method == 'POST':
        form = CustomPasswordResetForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Has canviat la contrasenya correctament!")
            return redirect('home')
        else:
            messages.error(request, 'Hi ha errors en el formulari. Si us plau, revisa-ho i torna-ho a intentar.')
    else:
        form = CustomPasswordResetForm(user=user)

    return render(request, "registration/password_reset.html", {
        'form': form,
        'title': 'Canviar contrasenya'
    })