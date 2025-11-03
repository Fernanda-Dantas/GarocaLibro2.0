from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views  # 🔹 Importa o módulo completo (boa prática)

urlpatterns = [
    # ======================
    # 🔹 ROTAS PRINCIPAIS
    # ======================
    path('', views.home_view, name='home'),
    path('appgaroca/', views.AppGarocaView.as_view(), name='appgaroca'),

    # ======================
    # 🔹 CRUD DE LEITORES
    # ======================
    path('leitores/', views.LeitorListView.as_view(), name='leitor-list'),
    path('leitor/add/', views.LeitorCreateView.as_view(), name='leitor-create'),
    path('leitor/edit/<int:pk>/', views.LeitorUpdateView.as_view(), name='leitor-update'),
    path('leitor/delete/<int:pk>/', views.LeitorDeleteView.as_view(), name='leitor-delete'),

    # ======================
    # 🔹 CRUD DE LIVROS
    # ======================
    path('livros/', views.LivroListView.as_view(), name='livro-list'),
    path('livro/add/', views.LivroCreateView.as_view(), name='livro-create'),
    path('livro/edit/<int:pk>/', views.LivroUpdateView.as_view(), name='livro-update'),
    path('livro/delete/<int:pk>/', views.LivroDeleteView.as_view(), name='livro-delete'),

    # ======================
    # 🔹 EMPRÉSTIMOS
    # ======================
    path('emprestimos/', views.EmprestimoListView.as_view(), name='emprestimo-list'),
    path('emprestimo/add/', views.EmprestimoCreateView.as_view(), name='emprestimo-create'),

    # ======================
    # 🔹 PERFIL E AUTENTICAÇÃO
    # ======================
    path('perfil/', views.perfil_view, name='perfil'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # ======================
    # 🔹 AGENDAMENTO E DEVOLUÇÃO
    # ======================
    path('agendar-retirada/', views.agendar_retirada, name='agendar_retirada'),
    path('api/devolver-livro/<int:emprestimo_id>/', views.api_devolver_livro, name='api_devolver_livro'),
    path('devolver-livro/', views.devolver_livro_view, name='devolver_livro'),

    # ======================
    # 🔹 PÁGINAS ADICIONAIS
    # ======================
    path('livros/view/', views.livros_view, name='livros-view'),

    # ======================
    # 🔹 NOVAS TELAS DO LEITOR
    # ======================
    path('dashboard/', views.dashboard_leitor, name='dashboard_leitor'),
    path('meus-emprestimos/', views.meus_emprestimos, name='meus_emprestimos'),
    path('perfil/editar/', views.editar_perfil_ajax, name='editar_perfil_ajax'),
    path('agendamento/<int:agendamento_id>/cancelar/', views.cancelar_agendamento, name='cancelar_agendamento'),

]

# ======================
# 🔹 MÍDIA EM MODO DEBUG
# ======================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
