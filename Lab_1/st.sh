#!/bin/bash

# Flask Image Blender - Startup Script
# st.sh - запуск Flask приложения для смешивания изображений

set -e  # Завершить скрипт при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для цветного вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Заголовок
echo "=================================================="
echo "    Flask Image Blender - Startup Script"
echo "=================================================="
echo ""

# Проверка директории
if [ ! -f "some_app.py" ]; then
    print_error "Файл some_app.py не найден!"
    print_info "Запустите скрипт из папки flaskapp"
    exit 1
fi

# Проверка Python
print_info "Проверка установки Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 не установлен или не найден в PATH"
    print_info "Установите Python3: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
print_success "Найден: $PYTHON_VERSION"

# Проверка pip
print_info "Проверка установки pip..."
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 не найден, пытаемся использовать pip..."
    if ! command -v pip &> /dev/null; then
        print_error "pip не установлен"
        print_info "Установите pip: python3 -m ensurepip --upgrade"
        exit 1
    fi
    PIP_CMD=pip
else
    PIP_CMD=pip3
fi

print_success "Найден: $($PIP_CMD --version | head -n1)"

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    print_info "Создание виртуального окружения..."
    python3 -m venv venv
    print_success "Виртуальное окружение создано"
else
    print_info "Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
print_info "Активация виртуального окружения..."
source venv/bin/activate
print_success "Виртуальное окружение активировано"

# Обновление pip
print_info "Обновление pip..."
$PIP_CMD install --upgrade pip

# Установка зависимостей
print_info "Проверка файла requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    print_warning "Файл requirements.txt не найден, создаем стандартный..."
    cat > requirements.txt << EOF
Flask==2.3.3
Pillow==10.0.0
numpy==1.24.3
matplotlib==3.7.2
Werkzeug==2.3.7
EOF
    print_success "Создан requirements.txt"
fi

print_info "Установка зависимостей..."
$PIP_CMD install -r requirements.txt
print_success "Зависимости установлены"

# Проверка установленных пакетов
print_info "Проверка установленных пакетов..."
$PIP_CMD list | grep -E "(Flask|Pillow|numpy|matplotlib)"

# Создание необходимых директорий
print_info "Создание структуры директорий..."
mkdir -p static/uploads
mkdir -p static/css
mkdir -p static/js
mkdir -p tests

print_success "Директории созданы"

# Проверка шаблонов
print_info "Проверка файлов шаблонов..."
if [ ! -f "templates/net.html" ]; then
    print_warning "Файл templates/net.html не найден"
fi

if [ ! -f "templates/simple.html" ]; then
    print_warning "Файл templates/simple.html не найден"
fi

# Проверка основных модулей
print_info "Проверка основных модулей..."
if [ ! -f "net.py" ]; then
    print_error "Файл net.py не найден!"
    exit 1
fi

if [ ! -f "client.py" ]; then
    print_warning "Файл client.py не найден"
fi

# Запуск тестов (если есть)
if [ -d "tests" ] && [ -n "$(ls tests/*.py 2>/dev/null)" ]; then
    print_info "Запуск тестов..."
    if python -m pytest tests/ -v; then
        print_success "Тесты прошли успешно"
    else
        print_warning "Некоторые тесты не прошли, но продолжаем запуск"
    fi
else
    print_warning "Тесты не найдены, пропускаем"
fi

# Проверка порта
PORT=5000
print_info "Проверка доступности порта $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    print_warning "Порт $PORT уже занят"
    read -p "Хотите использовать другой порт? (y/n): " change_port
    if [ "$change_port" = "y" ]; then
        read -p "Введите номер порта: " PORT
    else
        print_info "Попытка освободить порт..."
        pkill -f "python.*some_app.py" || true
        sleep 2
    fi
fi

# Экспорт переменных окружения
export FLASK_APP=some_app.py
export FLASK_ENV=development
export PYTHONPATH=$(pwd)

print_info "Настройка переменных окружения..."
print_info "FLASK_APP: $FLASK_APP"
print_info "FLASK_ENV: $FLASK_ENV"

# Информация о запуске
echo ""
echo "=================================================="
print_success "Приложение готово к запуску!"
echo "=================================================="
echo ""
print_info "Доступные страницы:"
echo "  • Основная:      http://localhost:$PORT"
echo "  • Простая версия: http://localhost:$PORT"
echo "  • Расширенная:   http://localhost:$PORT/advanced"
echo ""
print_info "API endpoints:"
echo "  • Смешивание:    http://localhost:$PORT/api/blend"
echo "  • Новая CAPTCHA: http://localhost:$PORT/new-captcha"
echo ""
print_warning "Для остановки приложения нажмите Ctrl+C"
echo ""

# Запрос на запуск
read -p "Запустить приложение сейчас? (y/n): " start_app
if [ "$start_app" != "y" ]; then
    print_info "Запустите приложение later командой: python some_app.py"
    deactivate
    exit 0
fi

echo ""
print_info "Запуск Flask приложения..."
echo ""

# Запуск приложения
python some_app.py --host=0.0.0.0 --port=$PORT

# Деактивация виртуального окружения после завершения
deactivate
print_info "Виртуальное окружение деактивировано"
print_success "Приложение завершило работу"
