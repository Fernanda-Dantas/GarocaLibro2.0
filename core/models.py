from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal

# ============================================================
# 🔹 CLASSE BASE (GENÉRICA)
# ============================================================
class Base(models.Model):
    criado = models.DateTimeField('Data de Criação', auto_now_add=True)
    modificado = models.DateTimeField('Data de Atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True


# ============================================================
# 🔹 GERENCIADOR DE LEITORES
# ============================================================
class LeitorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser informado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# ============================================================
# 🔹 LEITOR
# ============================================================
class Leitor(Base, AbstractBaseUser, PermissionsMixin):
    nome = models.CharField('Nome', max_length=50)
    telefone = models.CharField('Telefone', max_length=15)
    email = models.EmailField('Email', max_length=50, unique=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True, null=True)
    foto_perfil = models.ImageField('Foto de Perfil', upload_to='perfil/', blank=True, null=True)

    # Campos financeiros
    balance = models.DecimalField('Saldo', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fee = models.DecimalField('Taxa', max_digits=5, decimal_places=2, default=Decimal('0.00'))

    # Controle de acesso
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    objects = LeitorManager()

    def clean(self):
        super().clean()
        if not self.telefone.isdigit():
            raise ValidationError("O telefone deve conter apenas números.")
        if len(self.telefone) < 10:
            raise ValidationError("O telefone deve ter pelo menos 10 dígitos.")

    def __str__(self):
        return self.nome

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


# ============================================================
# 🔹 CATEGORIA DE LIVRO
# ============================================================
class Categoria(Base):
    nome = models.CharField('Nome', max_length=30)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


# ============================================================
# 🔹 LIVRO
# ============================================================
class Livro(Base):
    STATUS_CHOICE = (
        (True, 'Disponível'),
        (False, 'Indisponível'),
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
        return self.nome

    def is_available(self):
        return bool(self.status)


# ============================================================
# 🔹 EMPRÉSTIMO
# ============================================================
class Emprestimo(Base):
    STATUS_CHOICE = (
        ('in_progress', 'Em andamento'),
        ('completed', 'Finalizado'),
    )

    issue_date = models.DateField('Data de Empréstimo', default=timezone.localdate)
    devolucao = models.DateField('Data de Devolução', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICE, default='in_progress')
    leitor = models.ForeignKey(Leitor, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)

    MULTA_POR_DIA = 1.0  # Valor da multa por dia de atraso

    def calcular_multa(self):
        if not self.devolucao:
            return 0
        dias_atraso = (self.devolucao - self.issue_date).days
        return max(0, dias_atraso) * self.MULTA_POR_DIA

    def clean(self):
        if self.devolucao and self.devolucao <= self.issue_date:
            raise ValidationError('A data de devolução deve ser posterior à data de empréstimo.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'

    def __str__(self):
        return f'{self.livro} — {self.leitor}'


# ============================================================
# 🔹 AGENDAMENTO DE RETIRADA
# ============================================================
class Agendamento(Base):
    STATUS_CHOICE = (
        ('scheduled', 'Agendado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    )

    leitor = models.ForeignKey('Leitor', on_delete=models.CASCADE)
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
    data_agendada = models.DateField('Data Agendada', default=timezone.localdate)
    data_retirada = models.DateTimeField('Data de Retirada', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICE, default='scheduled')

    def clean(self):
        # Ignora validação se o agendamento foi cancelado
        if self.status == 'cancelled':
            return

        data_hoje = timezone.localdate()

        if self.data_agendada and self.data_agendada <= data_hoje:
            raise ValidationError('A data agendada deve ser posterior à data de hoje.')

        if self.data_retirada and self.data_retirada.date() < self.data_agendada:
            raise ValidationError('A retirada deve ocorrer após a data agendada.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Agendamento de Retirada'
        verbose_name_plural = 'Agendamentos de Retirada'
        ordering = ['-data_agendada']

    def __str__(self):
        return f'{self.leitor.nome} | {self.livro.nome} | {self.data_agendada.strftime("%d/%m/%Y")}'
