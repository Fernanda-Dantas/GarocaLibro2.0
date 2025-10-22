from django.db import models
from django.utils import timezone
from django.forms import ValidationError
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal

# Classe Base
class Base(models.Model):
    criado = models.DateTimeField('Data de Criação', auto_now_add=True)
    modificado = models.DateTimeField('Data de Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

# Classe LeitorManager (Gerenciador de Leitores)
class LeitorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser fornecido')
        email = self.model.normalize_email(email)
        leitor = self.model(email=email, **extra_fields)
        leitor.set_password(password)
        leitor.save(using=self._db)
        return leitor

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Classe Leitor
class Leitor(Base, AbstractBaseUser, PermissionsMixin):
    nome = models.CharField('Nome', max_length=50)
    telefone = models.CharField('Telefone', max_length=15)
    email = models.EmailField('Email', max_length=50, unique=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField('Foto de Perfil', upload_to='perfil/', blank=True, null=True)

    # Campos financeiros
    balance = models.DecimalField(
        'Saldo',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    fee = models.DecimalField(
        'Taxa',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Campos de controle de acesso
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    objects = LeitorManager()

    def clean(self):
        """Validações personalizadas antes de salvar o objeto."""
        super().clean()
        if not self.telefone.isdigit():
            raise ValidationError("O telefone deve conter apenas números.")
        if len(self.telefone) < 10:
            raise ValidationError("O telefone deve ter pelo menos 10 dígitos.")

    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir validações."""
        self.full_clean()
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

# Classe Categoria
class Categoria(Base):
    nome = models.CharField('Nome', max_length=30)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome

# Classe Livro
class Livro(Base):
    STATUS_CHOICE = (
        (True, 'Disponível'),
        (False, 'Indisponível')
    )

    codigo = models.CharField('Código', max_length=15, unique=True)
    nome = models.CharField('Nome', max_length=100)
    autor = models.CharField('Autor', max_length=100, default='Desconhecido')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    status = models.BooleanField('Status', choices=STATUS_CHOICE, default=True)
    isbn = models.CharField('ISBN', max_length=13, unique=True, blank=True, null=True)
    ano_publicacao = models.PositiveIntegerField('Ano de Publicação', blank=True, null=True)

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def __str__(self):
        return f"{self.nome} ({self.codigo}) - {self.autor}"

    def is_available(self):
        """
        Verifica se o livro está disponível para empréstimo.
        Retorna False se o status for 'Indisponível' ou se houver um empréstimo ativo.
        """
        if not self.status:
            return False
        return not Emprestimo.objects.filter(livro=self, status='in_progress').exists()

# Classe Emprestimo
class Emprestimo(Base):
    STATUS_CHOICE = (
        ('in_progress', 'Em andamento'),
        ('completed', 'Finalizado')
    )

    issue_date = models.DateField('Data de Empréstimo')
    return_date = models.DateField('Data de Devolução', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICE, default='in_progress')
    leitor = models.ForeignKey(Leitor, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)

    MULTA_POR_DIA = 1.0  # Valor da multa por dia de atraso

    def calcular_multa(self):
        """
        Calcula a multa com base no atraso na devolução.
        """
        if not self.return_date or self.return_date <= self.issue_date:
            return 0  # Sem multa se não houver data de devolução ou se não houver atraso

        dias_atraso = (self.return_date - self.issue_date).days
        if dias_atraso > 0:
            return dias_atraso * self.MULTA_POR_DIA
        return 0

    def clean(self):
        """Validações personalizadas para empréstimos."""
        if self.return_date and self.return_date <= self.issue_date:
            raise ValidationError('A data de devolução deve ser posterior à data de empréstimo.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'

    def __str__(self):
        return f'{self.leitor} | {self.livro}'

# Classe Agendamento de Retirada
class Agendamento(Base):
    STATUS_CHOICE = (
        ('scheduled', 'Agendado'),
        ('completed', 'Finalizado')
    )

    leitor = models.ForeignKey(Leitor, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    data_retirada = models.DateTimeField('Data de Retirada', help_text="Escolha uma data e hora futuras")
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICE, default='scheduled')

    def clean(self):
        if self.data_retirada <= timezone.now():
            raise ValidationError('A data de retirada deve ser uma data futura.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Agendamento de Retirada'
        verbose_name_plural = 'Agendamentos de Retirada'

    def __str__(self):
        return f'{self.leitor.nome} | {self.livro.nome} | {self.data_retirada}'
