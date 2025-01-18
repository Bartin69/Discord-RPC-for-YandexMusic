:: Установка кодировки для поддержки кириллицы
chcp 65001 >nul

@echo off
:: Проверка и включение поддержки ANSI-цветов
reg query "HKCU\Console" /v VirtualTerminalLevel >nul 2>&1
if %errorlevel% neq 0 (
    echo Включение поддержки ANSI-цветов...
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul
    echo Перезапустите консоль и запустите скрипт снова.
    pause
    exit /b
)

:: Установка кодировки для поддержки кириллицы
chcp 65001 >nul

:: Очистка экрана
cls

:: Заголовок
echo.
echo ╔════════════════════════════════════════════╗
echo ║ [36mСборка Yandex Music RPC в .exe[0m            ║
echo ╚════════════════════════════════════════════╝
echo.

:: Проверка Python
echo [33m[*] Проверка установки Python...[0m
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m[ОШИБКА] Python не установлен или не добавлен в PATH.[0m
    pause
    exit /b
)
echo [32m[УСПЕХ] Python установлен.[0m
echo.

:: Проверка pip
echo [33m[*] Проверка установки pip...[0m
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m[ОШИБКА] pip не установлен. Установка pip...[0m
    curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py >nul
    if %errorlevel% neq 0 (
        echo [31m[ОШИБКА] Не удалось установить pip.[0m
        pause
        exit /b
    )
    del get-pip.py
    echo [32m[УСПЕХ] pip установлен.[0m
)
echo [32m[УСПЕХ] pip установлен.[0m
echo.

:: Установка зависимостей
echo [33m[*] Проверка и установка зависимостей...[0m
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt >nul
if %errorlevel% neq 0 (
    echo [31m[ОШИБКА] Не удалось установить зависимости.[0m
    pause
    exit /b
)
echo [32m[УСПЕХ] Зависимости установлены.[0m
echo.

:: Сборка .exe
echo [33m[*] Запуск сборки .exe...[0m
python build_exe.py >nul
if %errorlevel% neq 0 (
    echo [31m[ОШИБКА] Ошибка при сборке .exe.[0m
    pause
    exit /b
)
echo [32m[УСПЕХ] Сборка завершена успешно![0m
echo.

:: Удаление временных папок
echo [33m[*] Удаление временных папок...[0m
if exist build (
    rmdir /s /q build
    echo [32m[УСПЕХ] Папка 'build' удалена.[0m
)
if exist __pycache__ (
    rmdir /s /q __pycache__
    echo [32m[УСПЕХ] Папка '__pycache__' удалена.[0m
)
echo.

:: Перемещение .exe в корень проекта
echo [33m[*] Перемещение .exe в корень проекта...[0m
if exist dist\main.exe (
    move /y dist\main.exe . >nul
    echo [32m[УСПЕХ] Файл 'main.exe' перемещен в корень проекта.[0m
    rmdir /s /q dist
    echo [32m[УСПЕХ] Папка 'dist' удалена.[0m
) else (
    echo [31m[ОШИБКА] Файл 'main.exe' не найден в папке 'dist'.[0m
)
echo.

:: Итог
echo ╔════════════════════════════════════════════╗
echo ║ [36mИсполняемый файл находится в корне проекта.[0m ║
echo ╚════════════════════════════════════════════╝
echo.
pause