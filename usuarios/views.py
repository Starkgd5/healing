from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.shortcuts import get_object_or_404, redirect, render

from medico.models import DadosMedico, is_medico
from paciente.models import DadosPaciente
from usuarios.models import UserProfile


def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastro.html")
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get('confirmar_senha')
        users = User.objects.filter(username=username)
        if users.exists():
            messages.add_message(request, constants.ERROR,
                                 'Já existe um usuário com esse username')
            return redirect('/usuarios/cadastro')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR,
                                 'A senha deve ser igual a confirmar senha')
            return redirect('/usuarios/cadastro')
        if len(senha) < 6:
            messages.add_message(request, constants.ERROR,
                                 'A senha deve possuir pelo menos 6 caracteres')
            return redirect('/usuarios/cadastro')

        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=senha
            )
            return redirect('/usuarios/login')
        except ValueError:
            return redirect('/usuarios/cadastro')


def login_view(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get("senha")
        user = authenticate(request, username=username, password=senha)
        if user:
            login(request, user)
            try:
                profile = UserProfile.objects.filter(user=user)
            except UserProfile.DoesNotExist:
                profile = None

            if profile is None:
                return redirect('/usuarios/cadastro_profile')

            return redirect('/usuarios/selecionar_perfil')

        messages.add_message(request, messages.ERROR,
                             'Usuário ou senha incorretos')
        return redirect('/usuarios/login')


@login_required(login_url='/usuarios/login')
def sair(request):
    logout(request)
    return redirect('/usuarios/login')


@login_required(login_url='/usuarios/login')
def cadastro_profile(request):
    if request.method == "GET":
        return render(request, 'cadastro_profile.html')
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')

        if not all([nome, cep, rua, bairro, rg, foto]):
            messages.add_message(request, constants.WARNING,
                                 'Preencha todos os campos.')

        dados_perfil = UserProfile(
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            foto=foto,
            user=request.user
        )
        dados_perfil.save()

        messages.add_message(
            request,
            constants.SUCCESS, 'Cadastro de perfil realizado com sucesso.')
        profile_id = dados_perfil.id
        if profile_id:
            profile = get_object_or_404(UserProfile, id=profile_id)
            # enviar profile para a sessão do usuario
            request.session['profile_id'] = profile.id
        return redirect('/usuarios/escolher_tipo')


@login_required(login_url='/usuarios/login')
def escolher_tipo(request):
    if request.method == "GET":
        return render(request, 'escolher_tipo.html')
    elif request.method == "POST":
        medico = request.POST.get('medico')
        paciente = request.POST.get('paciente')

        if medico:
            return redirect('/medicos/cadastro_medico')
        elif paciente:
            return redirect('/pacientes/cadastro_paciente')


def selecionar_perfil(request):
    profiles = UserProfile.objects.filter(user=request.user)
    if request.method == "GET":
        context = {
            'profiles': profiles
        }
        return render(request, 'selecionar_perfil.html', context)
    elif request.method == "POST":
        profile_id = request.POST.get('profile')
        if profile_id:
            profile = get_object_or_404(UserProfile, id=profile_id)
            # enviar profile para a sessão do usuario
            request.session['profile_id'] = profile.id
            if is_medico(profile):
                return redirect('/medicos/consultas_medico')
            return redirect('/pacientes/home')


def perfil_list(request):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)
    profiles = UserProfile.objects.filter(
        user=request.user).prefetch_related(
            'dadosmedico__especialidade').values(
                'id',
                'dadosmedico__especialidade__especialidade',
                'nome', 'rua', 'numero', 'bairro').distinct()
    context = {
        'profiles': profiles,
        'is_medico': is_medico(profile),
    }
    return render(request, 'perfil_list.html', context)


def editar_perfil(request, profile_id):
    profile_id_r = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id_r)
    profile_edit = UserProfile.objects.get(id=profile_id)
    if request.method == "GET":
        context = {
            'profile': profile_edit,
            'is_medico': is_medico(profile),
        }
        return render(request, 'editar_perfil.html', context)
    elif request.method == "PUT":
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')

        if not all([nome, cep, rua, bairro, rg, foto]):
            messages.add_message(request, constants.WARNING,
                                 'Preencha todos os campos.')

        dados_perfil = UserProfile(
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            foto=foto,
            user=request.user
        )
        dados_perfil.save()

        messages.add_message(
            request,
            constants.SUCCESS, 'Edição de perfil realizada com sucesso.')
        return redirect('/usuarios/perfil_list')


def excluir_perfil(request, profile_id):
    profile_id_r = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id_r)
    profile_edit = UserProfile.objects.get(id=profile_id)
    if request.method == "GET":
        context = {
            'profile': profile_edit,
            'is_medico': is_medico(profile),
        }
        return render(request, 'excluir_perfil.html', context)
    elif request.method == "DELETE":
        # Exclui o perfil do usuário
        if profile_edit == profile:
            profile_edit.delete()
            messages.add_message(
                request,
                constants.SUCCESS, 'Perfil deletado com sucesso.')
            return redirect('/usuarios/login')
        profile_edit.delete()
        messages.add_message(
            request,
            constants.SUCCESS, 'Perfil deletado com sucesso.')
        return redirect('/usuarios/perfil_list')
