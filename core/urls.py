from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import (
    AppGarocaView,
    LeitorListView,
    LeitorCreateView,
    LeitorUpdateView,
    LeitorDeleteView,
    LivroListView,
    LivroCreateView,
    LivroUpdateView,
    LivroDeleteView,
    EmprestimoListView,
    EmprestimoCreateView,
    livros_view,
    login_view,
    perfil_view,
    register,
    agendar_retirada,
    home_view,  # Mantém home_view
    api_devolver_livro,
    devolver_livro_view,
)

urlpatterns = [
    path('', home_view, name='home'),  # A URL principal agora está correta
    path('appgaroca/', AppGarocaView.as_view(), name='appgaroca'),
    path('leitores/', LeitorListView.as_view(), name='leitor-list'),
    path('leitor/add/', LeitorCreateView.as_view(), name='leitor-create'),
    path('leitor/edit/<int:pk>/', LeitorUpdateView.as_view(), name='leitor-update'),
    path('leitor/delete/<int:pk>/', LeitorDeleteView.as_view(), name='leitor-delete'),
    path('livros/', LivroListView.as_view(), name='livro-list'),
    path('livro/add/', LivroCreateView.as_view(), name='livro-create'),
    path('livro/edit/<int:pk>/', LivroUpdateView.as_view(), name='livro-update'),
    path('livro/delete/<int:pk>/', LivroDeleteView.as_view(), name='livro-delete'),
    path('emprestimos/', EmprestimoListView.as_view(), name='emprestimo-list'),
    path('emprestimo/add/', EmprestimoCreateView.as_view(), name='emprestimo-create'),
    path('livros/view/', livros_view, name='livros-view'),
    path('perfil/', perfil_view, name='perfil'),
    path('meu_perfil/', perfil_view, name='meu_perfil'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('agendar-retirada/', agendar_retirada, name='agendar_retirada'),
    path('api/devolver-livro/<int:emprestimo_id>/', api_devolver_livro, name='api_devolver_livro'),
    path('devolver-livro/', devolver_livro_view, name='devolver_livro'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
