#!/bin/bash

echo "Starting Flask Image Blending Application with Google reCAPTCHA..."

# Проверяем установлен ли Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "Activating virtual environment..."
source venv/bin/activate

# Устанавливаем зависимости
echo "Installing dependencies..."
pip install -r requirements.txt

# Проверяем наличие ключей reCAPTCHA
if grep -q "YOUR_RECAPTCHA" some_app.py; then
    echo "⚠️  WARNING: Please update the reCAPTCHA keys in some_app.py before deployment!"
    echo "   - Get your keys from: https://www.google.com/recaptcha/admin"
    echo "   - Update RECAPTCHA_SITE_KEY and RECAPTCHA_SECRET_KEY"
fi

# Запускаем приложение
echo "Starting Flask server..."
python some_app.py
