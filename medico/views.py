from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import redirect, render

from medico.models import DadosMedico, DatasAbertas, Especialidades, is_medico
from paciente.models import Consulta


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


@login_required
def cadastro_medico(request):
    if is_medico(request.user):
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
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        # TODO: Validar todos os campos

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            user=request.user,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta
        )
        dados_medico.save()

        messages.add_message(
            request,
            constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/medicos/abrir_horario')


@login_required
def abrir_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    if request.method == "GET":
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        context = {
            'dados_medicos': dados_medicos,
            'datas_abertas': datas_abertas,
            'is_medico': is_medico(request.user)
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
            user=request.user
        )

        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS,
                             'Horário cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')


@login_required
def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING,
                             'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    hoje = datetime.now().date()

    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(
        data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    print(consultas_hoje)
    consultas_restantes = Consulta.objects.exclude(
        id__in=consultas_hoje.values('id'))

    context = {
        'consultas_hoje': consultas_hoje,
        'consultas_restantes': consultas_restantes,
        'is_medico': is_medico(request.user)
    }

    return render(request, 'consultas_medico.html', context)
