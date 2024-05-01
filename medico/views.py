import calendar
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import redirect, render

from medico.models import (DadosMedico, DatasAbertas, Documento,
                           Especialidades, is_medico)
from paciente.models import Consulta
from usuarios.models import UserProfile


# Função para realizar a pesquisa de médicos
def search_doctor(name):
    # URL da página de pesquisa de médicos
    url = "https://portal.cfm.org.br/busca-medicos/"

    # Parâmetros da pesquisa
    params = {
        "search": name
    }

    # Enviar requisição GET para a página de pesquisa
    response = requests.get(url, params=params)

    # Verificar se a requisição foi bem sucedida
    if response.status_code == 200:
        # Parsing do HTML da página
        soup = BeautifulSoup(response.text, 'html.parser')

        # Aqui você pode implementar a lógica para extrair os dados do médico da página e preencher o formulário de cadastro

        # Exemplo: Extrair o nome do primeiro médico encontrado
        first_doctor = soup.find("div", class_="doctor-card")
        if first_doctor:
            doctor_name = first_doctor.find("h2").text
            print("Nome do médico encontrado:", doctor_name)
        else:
            print("Nenhum médico encontrado.")

    else:
        print("Falha ao realizar a requisição.")


# Exemplo de uso da função
search_doctor("João da Silva")


@login_required(login_url='/usuarios/login')
def cadastro_medico(request):
    profile = UserProfile.objects.get(user=request.user)
    if is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Você já está cadastrado como médico.')
        return redirect('/medicos/abrir_horario')

    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        context = {
            'especialidades': especialidades,
            'is_medico': is_medico(request.user)
        }
        return render(
            request,
            'cadastro_medico.html', context)
    elif request.method == "POST":
        crm = request.POST.get('crm')
        cim = request.FILES.get('cim')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        if not all([crm, cim, especialidade, valor_consulta]):
            messages.add_message(request, constants.WARNING,
                                 'Preencha todos os campos.')

        dados_medico = DadosMedico(
            crm=crm,
            cedula_identidade_medica=cim,
            profile=profile,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta
        )
        dados_medico.save()

        messages.add_message(
            request,
            constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')


@login_required(login_url='/usuarios/login')
def abrir_horario(request):

    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(profile=profile)
        datas_abertas = DatasAbertas.objects.filter(profile=profile)
        context = {
            'dados_medicos': dados_medicos,
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(profile)
        }
        return render(
            request, 'abrir_horario.html', context)
    elif request.method == "POST":
        data = request.POST.get('data')

        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")

        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING,
                                 'A data deve ser maior ou igual a data atual.')
            return redirect('/medicos/abrir_horario')

        horario_abrir = DatasAbertas(
            data=data,
            profile=profile
        )

        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS,
                             'Horário cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')


@login_required(login_url='/usuarios/login')
def consultas_medico(request):
    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    hoje = datetime.now().date()

    consultas = Consulta.objects.filter(
        data_aberta__profile=profile
    )

    especialidade = request.GET.get('especialidade')
    data = request.GET.get('data')

    if data:
        consultas = consultas.filter(
            data_aberta__data__gte=data)

    if especialidade:
        consultas = consultas.filter(
            data_aberta__user__userprofile__dadosmedico__especialidade__id=especialidade)

    consultas_hoje = consultas.filter(
        data_aberta__data__gte=hoje).filter(
        data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = consultas.exclude(
        id__in=consultas_hoje.values('id'))
    especialidades = Especialidades.objects.all()

    context = {
        'consultas_hoje': consultas_hoje,
        'consultas_restantes': consultas_restantes,
        'is_medico': is_medico(profile),
        'especialidades': especialidades
    }

    return render(request, 'consultas_medico.html', context)


@login_required(login_url='/usuarios/login')
def consulta_area_medico(request, id_consulta):
    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        context = {
            'consulta': consulta,
            'is_medico': is_medico(profile),
            'documentos': documentos,
        }
        return render(request, 'consulta_area_medico.html', context)
    elif request.method == "POST":
        # Inicializa a consulta + link da chamada
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        if request.user != consulta.data_aberta.user:
            messages.add_message(request, constants.ERROR,
                                 'Essa consulta não é sua.')
            return redirect('/medicos/consultas_medico')

        if consulta.status == 'C':
            messages.add_message(
                request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta.status == "F":
            messages.add_message(
                request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

        consulta.link = link
        consulta.status = 'I'
        consulta.save()

        messages.add_message(request, constants.SUCCESS,
                             'Consulta inicializada com sucesso.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required(login_url='/usuarios/login')
def finalizar_consulta(request, id_consulta):
    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR,
                             'Essa consulta não é sua.')
        return redirect('/medicos/consultas_medico')
    consulta.status = 'F'
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required(login_url='/usuarios/login')
def add_documento(request, id_consulta):
    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    consulta = Consulta.objects.get(id=id_consulta)

    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR,
                             'Essa consulta não é sua.')
        return redirect('/medicos/consultas_medico')

    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.WARNING,
                             'Adicione o documento.')
        return redirect('/medicos/abrir_horario')

    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento

    )

    documento.save()

    messages.add_message(request, constants.SUCCESS,
                         'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required(login_url='/usuarios/login')
def cancelar_consulta(request, id_consulta):
    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR,
                             'Essa consulta não é sua.')
        return redirect('/medicos/consultas_medico')
    consulta.status = 'C'
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')


@login_required(login_url='/usuarios/login')
def dashboard_medico(request):
    profile = UserProfile.objects.get(user=request.user)
    if not is_medico(profile):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    # Consultas finalizadas do médico logado
    consultas = Consulta.objects.filter(
        data_aberta__profile=profile,
        status='F',
    )

    consultas_por_mes = defaultdict(int)
    for consulta in consultas:
        mes = consulta.data_aberta.data.month
        consultas_por_mes[mes] += 1

    meses = [calendar.month_name[i] for i in range(1, 13)]
    consultas_por_mes_data = {
        'labels': meses,
        'data': [consultas_por_mes[i] for i in range(1, 13)]
    }

    context = {
        'is_medico': is_medico(profile),
        'consultas_por_mes_data': consultas_por_mes_data,
    }
    return render(request, 'dashboard_medico.html', context)
