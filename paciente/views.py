from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import get_object_or_404, redirect, render

from medico.models import (DadosMedico, DatasAbertas, Documento,
                           Especialidades, is_medico)
from paciente.models import Consulta, DadosPaciente
from usuarios.models import UserProfile


@login_required(login_url='/usuarios/login')
def home(request):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)
    if request.method == "GET":
        medicos = DadosMedico.objects.all()
        especialidades = Especialidades.objects.all()

        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')

        if medico_filtrar:
            medicos = medicos.filter(profile__nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(
                especialidade_id__in=especialidades_filtrar)

        context = {
            'medicos': medicos,
            'especialidades': especialidades,
            'is_medico': is_medico(profile)
        }
        return render(request, 'home.html', context)


@login_required(login_url='/usuarios/login')
def escolher_horario(request, id_dados_medicos):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)
    if request.method == "GET":
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(
            profile=medico.profile).filter(
                data__gte=datetime.now()).filter(
                    agendado=False).order_by('data')
        context = {
            'medico': medico,
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(profile)
        }
        return render(request, 'escolher_horario.html', context)


@login_required(login_url='/usuarios/login')
def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        profile_id = request.session.get('profile_id')
        profile = UserProfile.objects.get(id=profile_id)
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)

        horario_agendado = Consulta(
            paciente=profile,
            data_aberta=data_aberta
        )

        horario_agendado.save()

        data_aberta.agendado = True
        data_aberta.save()

        messages.add_message(request, constants.SUCCESS,
                             'Horário agendado com sucesso.')

        return redirect('/pacientes/minhas_consultas/')


@login_required(login_url='/usuarios/login')
def minhas_consultas(request):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)
    especialidade = request.GET.get('especialidade')
    data = request.GET.get('data')
    consultas = Consulta.objects.filter(paciente=profile).filter(
        data_aberta__data__gte=datetime.now())

    if data:
        consultas = consultas.filter(data_aberta__data__gte=data)

    if especialidade:
        consultas = consultas.filter(
            data_aberta__profile__dadosmedico__especialidade__id=especialidade)

    especialidades = Especialidades.objects.all()

    context = {
        'minhas_consultas': consultas,
        'is_medico': is_medico(profile),
        'especialidades': especialidades
    }
    return render(request, 'minhas_consultas.html', context)


@login_required(login_url='/usuarios/login')
def consulta_paciente(request, id_consulta):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)
    consulta = get_object_or_404(Consulta, id=id_consulta)

    # Verifica se o usuário autenticado é o paciente associado à consulta
    if profile != consulta.paciente:
        messages.add_message(request, constants.ERROR,
                             'Essa consulta não é sua.')
        return redirect('/pacientes/home')

    documentos = Documento.objects.filter(consulta=consulta)

    # Acessa o perfil do médico associado à consulta
    dado_medico = DadosMedico.objects.get(
        profile=consulta.data_aberta.profile)

    context = {
        'consulta': consulta,
        'dado_medico': dado_medico,
        'is_medico': is_medico(profile),
        'documentos': documentos
    }
    return render(request, 'consulta.html', context)


@login_required(login_url='/usuarios/login')
def cancelar_consulta(request, id_consulta):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)
    consulta = Consulta.objects.get(id=id_consulta)
    if profile != consulta.paciente:
        messages.add_message(request, constants.ERROR,
                             'Essa consulta não é sua.')
        return redirect('/pacientes/home')
    consulta.status = 'C'
    consulta.save()
    return redirect(f'/pacientes/consulta/{id_consulta}')


@login_required(login_url='/usuarios/login')
def cadastro_paciente(request):
    profile_id = request.session.get('profile_id')
    profile = UserProfile.objects.get(id=profile_id)

    if request.method == "GET":
        context = {
            'is_medico': is_medico(profile)
        }
        return render(
            request,
            'cadastro_paciente.html', context)
    elif request.method == "POST":
        cpf = request.POST.get('cpf')
        cns = request.POST.get('cns')
        birth_date = request.POST.get('birth_date')
        mother_name = request.POST.get('mother_name')

        if not all([cpf, cns, birth_date, mother_name]):
            messages.add_message(request, constants.WARNING,
                                 'Preencha todos os campos.')

        dados_paciente = DadosPaciente(
            cpf=cpf,
            cns=cns,
            profile=profile,
            mother_name=mother_name,
            birth_date=birth_date,
        )
        dados_paciente.save()

        messages.add_message(
            request,
            constants.SUCCESS, 'Cadastro paciente realizado com sucesso.')

        return redirect('/pacientes/home')
