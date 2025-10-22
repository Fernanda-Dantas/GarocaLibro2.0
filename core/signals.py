from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Emprestimo, Livro

@receiver(post_save, sender=Emprestimo)
def atualizar_quantidade_livros_emprestimo(sender, instance, created, **kwargs):
    """
    Atualiza a quantidade de livros ao criar ou atualizar um empréstimo.
    """
    if created and instance.status == 'in_progress':
        livro = instance.livro
        livro.status = False  # Marca o livro como indisponível
        livro.save()

@receiver(post_delete, sender=Emprestimo)
def atualizar_quantidade_livros_devolucao(sender, instance, **kwargs):
    """
    Atualiza a quantidade de livros ao deletar um empréstimo (devolução).
    """
    if instance.status == 'in_progress':
        livro = instance.livro
        livro.status = True  # Marca o livro como disponível
        livro.save()