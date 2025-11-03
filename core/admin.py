from django.contrib import admin
from .models import Categoria, Leitor, Livro, Emprestimo, Agendamento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado', 'modificado', 'ativo')


@admin.register(Leitor)
class LeitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'telefone', 'criado', 'modificado', 'ativo')
    search_fields = ('nome', 'email')
    list_filter = ('ativo',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'categoria', 'autor', 'status', 'criado', 'modificado', 'ativo')
    search_fields = ('nome', 'autor', 'codigo')
    list_filter = ('status', 'categoria')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'nome', 'autor', 'categoria')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('leitor', 'livro', 'devolucao', 'status', 'criado', 'modificado', 'ativo')


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('leitor', 'livro', 'data_retirada', 'status', 'criado', 'modificado', 'ativo')
    search_fields = ('leitor__nome', 'livro__nome')
    list_filter = ('status',)
