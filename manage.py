#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import dotenv  # 👈 para carregar variáveis de ambiente do .env


def main():
    """Run administrative tasks."""
    # ==============================
    # 🔄 Carregar variáveis do .env
    # ==============================
    # O .env deve estar na raiz do projeto (mesmo nível de manage.py)
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    # ==============================
    # ⚙️ Configurar módulo principal do Django
    # ==============================
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_manager.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. "
            "Certifique-se de que ele está instalado e disponível no seu ambiente virtual."
        ) from exc

    # ==============================
    # ▶️ Executar comandos Django
    # ==============================
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
