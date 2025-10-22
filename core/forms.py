from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Categoria, Leitor, Livro, Emprestimo, Agendamento
from django.utils import timezone

class CategoriaModelForm(forms.ModelForm):
    """Formulário para criar ou editar uma Categoria."""
    
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da Categoria'
            }),
        }

class LeitorModelForm(forms.ModelForm):
    """Formulário para criar ou editar um Leitor."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        }),
        required=True,
        label="Senha"
    )

    class Meta:
        model = Leitor
        fields = ['nome', 'telefone', 'email', 'password', 'foto_perfil', 'endereco']  # Added foto_perfil and endereco
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do Leitor'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefone do Leitor'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email do Leitor'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'  # Only accept image files
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço do Leitor'
            }),
        }

    def clean_email(self):
        """Valida o e-mail para garantir que não esteja em uso."""
        email = self.cleaned_data.get('email')
        if Leitor.objects.filter(email=email).exists():
            raise ValidationError("Este email já está cadastrado.")
        return email

    def save(self, commit=True):
        """Salva o Leitor com a senha criptografada."""
        leitor = super().save(commit=False)
        leitor.set_password(self.cleaned_data['password'])  # Criptografa a senha
        if commit:
            leitor.save()
        return leitor

class LivroModelForm(forms.ModelForm):
    """Formulário para criar ou editar um Livro."""
    
    class Meta:
        model = Livro
        fields = ['codigo', 'nome', 'categoria', 'autor', 'capa']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código do Livro'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do Livro'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'autor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Autor do Livro'
            }),
            'capa': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

class EmprestimoModelForm(forms.ModelForm):
    """Formulário para criar ou editar um Empréstimo."""
    
    class Meta:
        model = Emprestimo
        fields = ['leitor', 'livro', 'devolucao']
        widgets = {
            'leitor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'livro': forms.Select(attrs={
                'class': 'form-control'
            }),
            'devolucao': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Data e Hora de Devolução',
                'type': 'datetime-local'
            }),
        }

    def clean_devolucao(self):
        """Valida se a data de devolução é futura."""
        devolucao = self.cleaned_data.get('devolucao')
        if devolucao is None:
            return devolucao
        if devolucao <= timezone.now():
            raise ValidationError("A data de devolução deve ser futura.")
        return devolucao

class LoginForm(forms.Form):
    """Formulário de Login com validação de e-mail e senha."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autofocus': 'autofocus'  # Campo de email começa com foco
        }),
        error_messages={'invalid': 'Por favor, insira um email válido.'}  # Mensagem de erro personalizada
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        })
    )

    def clean(self):
        """Valida o login, tentando autenticar com o e-mail e senha fornecidos."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Credenciais inválidas. Verifique o email e a senha.")
        return cleaned_data

class AgendamentoForm(forms.ModelForm):
    """Formulário para criar ou editar um Agendamento de Retirada de Livro."""
    
    class Meta:
        model = Agendamento
        fields = ['livro', 'data_retirada']
        widgets = {
            'livro': forms.Select(attrs={'class': 'form-control'}),
            'data_retirada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
