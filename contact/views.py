from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Contact
from django.core.paginator import Paginator
from .forms import ContactForm, RegisterForm, RegisterUpdateForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required




def index(request):
    contacts = Contact.objects.filter(show=True).order_by('-id')
    
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'contact/index.html', {'page_obj': page_obj, 'site_title': 'Contatos -'})



def contact(request, contact_id):
    single_contact = get_object_or_404(Contact, pk=contact_id, show=True)
    site_title = f'{single_contact.first_name} {single_contact.last_name} -'
    return render(request, 'contact/contact.html', {'contact': single_contact, 'site_title': site_title})


def search(request):
    search_value = request.GET.get('q', '').strip()
    
    
    if search_value == '':
        return redirect('contact:index')
    
    contacts = Contact.objects.filter(show=True).filter(Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value) |
                                                        Q(phone__icontains=search_value) | Q(email__icontains=search_value)).order_by('-id')
    
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'contact/index.html', {'page_obj': page_obj, 'site_title': 'Contatos -', 'search_value': search_value})


@login_required(login_url='contact:login')
def create(request):
    from_action = reverse('contact:create')
    
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        context = {'form': form, 'from_action': from_action}
        
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            messages.success(request, 'Criado com sucesso')
            return redirect('contact:update', contact_id=contact.pk)
        
        return render(request, 'contact/create.html', context)   
    
    context = {'form': ContactForm(), 'from_action': from_action}
    
    return render(request, 'contact/create.html', context)
   
   
@login_required(login_url='contact:login')
def update(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id, show=True, owner=request.user)
    from_action = reverse('contact:update', args=(contact_id,))
    
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        context = {'form': form, 'from_action': from_action}
        
        if form.is_valid():
            contact = form.save()
            return redirect('contact:update', contact_id=contact.pk)
        
        return render(request, 'contact/create.html', context)   
    
    context = {'form': ContactForm(instance=contact), 'from_action': from_action}
    
    return render(request, 'contact/create.html', context)


@login_required(login_url='contact:login')
def delete(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id, show=True, owner=request.user)
    
    confirmation = request.POST.get('confirmation', 'no')
    
    if confirmation == 'yes':
        contact.delete()
        return redirect('contact:index')
    
    return render(request, 'contact/contact.html', {'contact': contact, 'confirmation': confirmation })


def register(request):
    form = RegisterForm()
    
    
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Usúario registrado')
            return redirect('contact:index')
            
    return render(request, 'contact/register.html', {'form': form })


def login_view(request):
    
    form = AuthenticationForm(request)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request,'Logado com sucesso')
            return redirect ('contact:index')
        else:
            messages.error(request, 'Usúario ou senha inválido')
    
    return render(request, 'contact/login.html', {'form': form })


@login_required(login_url='contact:login')
def user_update(request):
    form = RegisterUpdateForm(instance=request.user)
    
    if request.method != 'POST':
        return render(request, 'contact/user-update.html', {'form': form})
    
    form = RegisterUpdateForm(data=request.POST, instance=request.user)
    
    if not form.is_valid():
        messages.error(request, 'Erro na alteração')
        return render(request, 'contact/user-update.html', {'form': form})
    
    form.save()
    messages.success(request, 'Alteração feita com sucesso')
    return redirect('contact:user_update')


@login_required(login_url='contact:login')
def logout_view(request):
    auth.logout(request)
    return redirect('contact:login')


