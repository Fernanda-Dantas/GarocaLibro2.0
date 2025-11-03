import logging
from datetime import datetime, date
from django.views.generic import TemplateView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import make_aware
from core.forms import LoginForm, LeitorModelForm, AgendamentoForm, LivroModelForm
from core.models import Emprestimo, Leitor, Livro, Agendamento
from django.views.decorators.http import require_POST

# Configura o logger
logger = logging.getLogger(__name__)

# ===========================================
# 🔹 HOME E APP PRINCIPAL
# ===========================================
def home_view(request):
    return render(request, 'home.html')


class AppGarocaView(TemplateView):
    template_name = 'appgaroca.html'


# ===========================================
# 🔹 CRUD: LEITOR
# ===========================================
class LeitorListView(TemplateView):
    template_name = 'leitor-list.html'


class LeitorCreateView(CreateView):
    model = Leitor
    form_class = LeitorModelForm
    template_name = 'leitor.html'
    success_url = reverse_lazy('leitor-list')


class LeitorUpdateView(UpdateView):
    model = Leitor
    form_class = LeitorModelForm
    template_name = 'leitor.html'
    success_url = reverse_lazy('leitor-list')


class LeitorDeleteView(DeleteView):
    model = Leitor
    template_name = 'leitor_confirm_delete.html'
    success_url = reverse_lazy('leitor-list')


# ===========================================
# 🔹 CRUD: LIVRO
# ===========================================
class LivroListView(TemplateView):
    template_name = 'livro-list.html'


class LivroCreateView(CreateView):
    model = Livro
    form_class = LivroModelForm
    template_name = 'livro.html'
    success_url = reverse_lazy('livro-list')


class LivroUpdateView(UpdateView):
    model = Livro
    form_class = LivroModelForm
    template_name = 'livro.html'
    success_url = reverse_lazy('livro-list')


class LivroDeleteView(DeleteView):
    model = Livro
    template_name = 'livro_confirm_delete.html'
    success_url = reverse_lazy('livro-list')


# ===========================================
# 🔹 LISTAGEM SIMPLES DE LIVROS (RESTAURADA)
# ===========================================
def livros_view(request):
    """
    Exibe uma lista simples de todos os livros disponíveis no sistema.
    Essa view é pública e pode ser usada para o leitor visualizar o catálogo.
    """
    livros = Livro.objects.all().order_by('nome')
    return render(request, 'livros.html', {'livros': livros})


# ===========================================
# 🔹 CRUD: EMPRÉSTIMO
# ===========================================
class EmprestimoListView(TemplateView):
    template_name = 'emprestimo-list.html'


class EmprestimoCreateView(CreateView):
    model = Emprestimo
    fields = ['livro', 'devolucao']
    template_name = 'emprestimo.html'
    success_url = reverse_lazy('emprestimo-list')

    def form_valid(self, form):
        devolucao = form.cleaned_data['devolucao']
        if isinstance(devolucao, date) and not isinstance(devolucao, datetime):
            form.instance.devolucao = make_aware(datetime.combine(devolucao, datetime.min.time()))
        return super().form_valid(form)


# ===========================================
# 🔹 AGENDAMENTOS / RESERVAS
# ===========================================
@login_required
def reservas_view(request):
    reservas = Emprestimo.objects.filter(leitor=request.user)
    return render(request, 'reservas.html', {'reservas': reservas})


@login_required
def agendar_retirada(request):
    livros_disponiveis = Livro.objects.filter(status=True)
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            livro = form.cleaned_data['livro']
            if livro.status:
                agendamento = form.save(commit=False)
                agendamento.leitor = request.user
                agendamento.save()
                livro.status = False
                livro.save()
                messages.success(request, f'Agendamento realizado com sucesso para o livro "{livro.nome}"!')
                return redirect('dashboard_leitor')
            else:
                form.add_error('livro', 'Este livro já foi reservado.')
    else:
        form = AgendamentoForm()
    return render(request, 'agendar_retirada.html', {'form': form, 'livros_list': livros_disponiveis})


def success(request):
    return render(request, 'success.html')

@login_required
@require_POST
def cancelar_agendamento(request, agendamento_id):
    try:
        agendamento = get_object_or_404(Agendamento, id=agendamento_id, leitor=request.user)
        if agendamento.status != 'scheduled':
            return JsonResponse({'error': 'Este agendamento não pode ser cancelado.'}, status=400)

        agendamento.status = 'cancelled'
        agendamento.save()

        # Libera o livro novamente
        agendamento.livro.status = True
        agendamento.livro.save()

        return JsonResponse({'success': True, 'message': 'Agendamento cancelado com sucesso!'})
    except Exception as e:
        logger.error(f"Erro ao cancelar agendamento: {str(e)}")
        return JsonResponse({'error': 'Erro ao cancelar o agendamento.'}, status=500)

# ===========================================
# 🔹 LOGIN / CADASTRO / PERFIL
# ===========================================
def register(request):
    if request.method == 'POST':
        form = LeitorModelForm(request.POST)
        if form.is_valid():
            leitor = form.save(commit=False)
            leitor.telefone = 'Desconhecido'
            leitor.set_password(form.cleaned_data['password'])
            leitor.save()
            login(request, leitor)
            return redirect('home')
    else:
        form = LeitorModelForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_leitor')
        else:
            messages.error(request, "Credenciais inválidas.")

    response = render(request, 'login.html', {'form': form})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
    return response


@login_required
def perfil_view(request):
    try:
        leitor = get_object_or_404(Leitor, email=request.user.email)
        return render(request, 'perfil.html', {'leitor': leitor})
    except Exception as e:
        logger.error(f"Erro ao carregar o perfil: {str(e)}")
        return render(request, 'erro.html', {'mensagem': 'Erro ao carregar o perfil.'})


@login_required
def editar_perfil_view(request):
    leitor = get_object_or_404(Leitor, email=request.user.email)
    if request.method == 'POST':
        form = LeitorModelForm(request.POST, request.FILES, instance=leitor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = LeitorModelForm(instance=leitor)
    return render(request, 'editar_perfil.html', {'form': form})


@login_required
def editar_perfil_ajax(request):
    leitor = request.user
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        foto = request.FILES.get("foto_perfil")

        if nome:
            leitor.nome = nome
        if telefone:
            leitor.telefone = telefone
        if foto:
            leitor.foto_perfil = foto

        leitor.save()
        return JsonResponse({
            "success": True,
            "foto_perfil": leitor.foto_perfil.url if leitor.foto_perfil else "https://garoca1.s3.us-east-2.amazonaws.com/media/default-profile.png"
        })
    return JsonResponse({"success": False}, status=400)


# ===========================================
# 🔹 DASHBOARD DO LEITOR
# ===========================================
@login_required
def dashboard_leitor(request):
    leitor = request.user

    emprestimos = Emprestimo.objects.filter(leitor=leitor).order_by('-criado')
    agendamentos = Agendamento.objects.filter(leitor=leitor).order_by('-criado')

    context = {
        'leitor': leitor,
        'emprestimos': emprestimos,
        'agendamentos': agendamentos,
    }
    return render(request, 'leitor_dashboard/dashboard.html', context)


# ===========================================
# 🔹 DEVOLUÇÃO DE LIVROS
# ===========================================
@login_required
def api_devolver_livro(request, emprestimo_id):
    try:
        emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id, leitor=request.user)
        if emprestimo.status != 'in_progress':
            return JsonResponse({'error': 'Este empréstimo já foi finalizado.'}, status=400)

        emprestimo.status = 'completed'
        emprestimo.save()

        livro = emprestimo.livro
        livro.status = True
        livro.save()

        return JsonResponse({'message': 'Livro devolvido com sucesso!'})
    except Exception as e:
        logger.error(f"Erro ao processar devolução do livro: {str(e)}")
        return JsonResponse({'error': 'Erro ao processar a devolução.'}, status=500)


@login_required
def devolver_livro_view(request):
    if request.method == 'POST':
        codigo_livro = request.POST.get('codigo_livro')
        try:
            livro = get_object_or_404(Livro, codigo=codigo_livro)
            emprestimo = get_object_or_404(Emprestimo, livro=livro, status='in_progress')
            emprestimo.status = 'completed'
            emprestimo.save()
            livro.status = True
            livro.save()
            messages.success(request, f'Livro "{livro.nome}" devolvido com sucesso!')
            return redirect('devolver_livro')
        except Livro.DoesNotExist:
            messages.error(request, 'Código do livro não encontrado.')
        except Emprestimo.DoesNotExist:
            messages.error(request, 'Este livro não está emprestado.')
        except Exception as e:
            logger.error(f"Erro ao processar devolução: {str(e)}")
            messages.error(request, 'Erro ao processar devolução.')
    return render(request, 'devolver_livro.html')
# ===========================================
# 🔹 MEUS EMPRÉSTIMOS (PARA O LEITOR LOGADO)
# ===========================================
@login_required
def meus_emprestimos(request):
    """
    Exibe todos os empréstimos feitos pelo leitor logado.
    Mostra tanto os ativos quanto os finalizados.
    """
    emprestimos = Emprestimo.objects.filter(leitor=request.user).order_by('-criado')
    return render(request, 'leitor_dashboard/meus_emprestimos.html', {'emprestimos': emprestimos})

