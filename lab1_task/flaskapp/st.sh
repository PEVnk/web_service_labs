#!/bin/bash

echo "Starting Flask Image Denoising Application..."

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

# Запускаем приложение
echo "Starting Flask server..."
python some_app.py
