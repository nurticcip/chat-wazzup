// Сразу выполняющаяся функция для гарантированной инициализации темы
(function() {
    // Инициализируем тему, не дожидаясь загрузки DOM
    initializeThemeEarly();

    // Настройка обработчиков событий после загрузки DOM
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Theme: DOM загружен, настраиваем обработчики');
        setupThemeToggle();
    });

    // Функция инициализации темы, которая выполняется сразу
    function initializeThemeEarly() {
        // Проверяем, сохранена ли тема в localStorage
        const isDarkTheme = localStorage.getItem('darkTheme') === 'true';
        console.log('Theme: Инициализация темы, isDarkTheme =', isDarkTheme);
        
        // Немедленно применяем тему к body
        if (isDarkTheme) {
            document.body.classList.add('dark-theme');
            console.log('Theme: Применена темная тема');
        } else {
            document.body.classList.remove('dark-theme');
            console.log('Theme: Применена светлая тема');
        }
    }

    // Функция настройки переключателя темы
    function setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        
        if (!themeToggle) {
            console.error('Theme: Элемент #theme-toggle не найден');
            return;
        }
        
        const themeIcon = themeToggle.querySelector('img');
        
        if (!themeIcon) {
            console.error('Theme: Иконка темы не найдена внутри #theme-toggle');
            return;
        }

        // Обновляем иконку при инициализации
        updateThemeIcon(themeIcon);
        
        // Добавляем обработчик события для переключения темы
        themeToggle.addEventListener('click', function() {
            console.log('Theme: Клик по переключателю темы');
            toggleTheme();
            updateThemeIcon(themeIcon);
            
            // Оповещаем другие iframe о смене темы
            if (window.parent && window !== window.parent) {
                window.parent.postMessage('themeChanged', '*');
            }
        });
    }

    // Функция переключения темы
    function toggleTheme() {
        const isDarkTheme = document.body.classList.contains('dark-theme');
        console.log('Theme: Переключение темы, текущая isDarkTheme =', isDarkTheme);
        
        if (isDarkTheme) {
            document.body.classList.remove('dark-theme');
            localStorage.setItem('darkTheme', 'false');
            console.log('Theme: Переключено на светлую тему');
        } else {
            document.body.classList.add('dark-theme');
            localStorage.setItem('darkTheme', 'true');
            console.log('Theme: Переключено на темную тему');
        }
    }

    // Функция обновления иконки темы
    function updateThemeIcon(iconElement) {
        if (!iconElement) return;
        
        const isDarkTheme = document.body.classList.contains('dark-theme');
        console.log('Theme: Обновление иконки, isDarkTheme =', isDarkTheme);
        
        try {
            // Получаем базовый URL из текущего src
            let sunUrl = '/static/images/sun.png';
            let moonUrl = '/static/images/moon.png';
            
            // Если в src есть Flask URL, извлекаем базовую часть
            if (iconElement.src.includes('static/images/')) {
                const baseUrl = iconElement.src.substring(0, iconElement.src.lastIndexOf('/') + 1);
                sunUrl = baseUrl + 'sun.png';
                moonUrl = baseUrl + 'moon.png';
            }
            
            // Устанавливаем соответствующую иконку
            if (isDarkTheme) {
                iconElement.src = sunUrl;
                iconElement.alt = 'Light Mode';
                console.log('Theme: Иконка изменена на Солнце (Light Mode)');
            } else {
                iconElement.src = moonUrl;
                iconElement.alt = 'Dark Mode';
                console.log('Theme: Иконка изменена на Луну (Dark Mode)');
            }
        } catch (error) {
            console.error('Theme: Ошибка при обновлении иконки', error);
        }
    }

    // Экспортируем функции для использования в других скриптах
    window.themeUtils = {
        toggleTheme: toggleTheme,
        isDarkTheme: function() {
            return document.body.classList.contains('dark-theme');
        }
    };
})();
