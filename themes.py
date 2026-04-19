from kivy.properties import DictProperty, ListProperty
from kivy.app import App
from kivy.clock import Clock

class ThemeManager:
    """Менеджер тем приложения"""
    
    themes = {
        'light': {
            # Основные цвета
            'primary': (0.2, 0.6, 0.8, 1),      # Основной акцентный цвет
            'primary_dark': (0.15, 0.5, 0.7, 1),
            'secondary': (0.8, 0.4, 0.2, 1),    # Вторичный цвет
            'success': (0.2, 0.7, 0.3, 1),      # Успех/Доход
            'danger': (0.8, 0.2, 0.2, 1),       # Опасность/Расход
            'warning': (0.9, 0.6, 0.1, 1),      # Предупреждение
            
            # Фоновые цвета
            'background': (0.95, 0.95, 0.97, 1),
            'surface': (1, 1, 1, 1),
            'surface_secondary': (0.98, 0.98, 0.99, 1),
            'card': (1, 1, 1, 1),
            'dialog': (1, 1, 1, 1),
            
            # Текст
            'text_primary': (0.1, 0.1, 0.13, 1),
            'text_secondary': (0.5, 0.5, 0.55, 1),
            'text_disabled': (0.7, 0.7, 0.75, 1),
            'text_on_primary': (1, 1, 1, 1),
            
            # Навигация
            'nav_background': (0.98, 0.98, 0.99, 1),
            'nav_active': (0.2, 0.6, 0.8, 1),
            'nav_inactive': (0.3, 0.3, 0.35, 1),
            
            # Разделители
            'divider': (0.85, 0.85, 0.9, 1),
            'border': (0.8, 0.8, 0.85, 1),
            
            # Кнопки
            'button_normal': (0.95, 0.95, 0.97, 1),
            'button_pressed': (0.85, 0.85, 0.9, 1),
        },
        
        'dark': {
            # Основные цвета
            'primary': (0.3, 0.7, 0.9, 1),
            'primary_dark': (0.25, 0.6, 0.8, 1),
            'secondary': (0.9, 0.5, 0.3, 1),
            'success': (0.3, 0.8, 0.4, 1),
            'danger': (0.9, 0.3, 0.3, 1),
            'warning': (0.95, 0.65, 0.15, 1),
            
            # Фоновые цвета
            'background': (0.08, 0.08, 0.1, 1),
            'surface': (0.12, 0.12, 0.15, 1),
            'surface_secondary': (0.1, 0.1, 0.12, 1),
            'card': (0.14, 0.14, 0.17, 1),
            'dialog': (0.16, 0.16, 0.19, 1),
            
            # Текст
            'text_primary': (0.95, 0.95, 0.97, 1),
            'text_secondary': (0.65, 0.65, 0.7, 1),
            'text_disabled': (0.4, 0.4, 0.45, 1),
            'text_on_primary': (1, 1, 1, 1),
            
            # Навигация
            'nav_background': (0.1, 0.1, 0.12, 1),
            'nav_active': (0.3, 0.7, 0.9, 1),
            'nav_inactive': (0.4, 0.4, 0.45, 1),
            
            # Разделители
            'divider': (0.2, 0.2, 0.25, 1),
            'border': (0.18, 0.18, 0.22, 1),
            
            # Кнопки
            'button_normal': (0.18, 0.18, 0.22, 1),
            'button_pressed': (0.25, 0.25, 0.3, 1),
        }
    }
    
    def __init__(self):
        self.current_theme = 'light'  # По умолчанию светлая тема
        self._observers = []
        
        # Загружаем сохраненную тему
        try:
            with open('theme_setting.txt', 'r') as f:
                saved_theme = f.read().strip()
                if saved_theme in self.themes:
                    self.current_theme = saved_theme
        except FileNotFoundError:
            pass
    
    def get_color(self, color_name):
        """Получить цвет из текущей темы"""
        return self.themes[self.current_theme].get(color_name, (0.5, 0.5, 0.5, 1))
    
    def get_all_colors(self):
        """Получить все цвета текущей темы"""
        return self.themes[self.current_theme]
    
    def register_observer(self, callback):
        """Регистрация наблюдателя за изменениями темы"""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def unregister_observer(self, callback):
        """Отписка наблюдателя"""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def notify_observers(self):
        """Уведомление всех наблюдателей об изменении темы"""
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                print(f"Error notifying observer: {e}")
    
    def switch_theme(self, theme_name):
        """Переключить тему"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            # Сохраняем выбор пользователя
            with open('theme_setting.txt', 'w') as f:
                f.write(theme_name)
            
            # Уведомляем наблюдателей
            Clock.schedule_once(lambda dt: self.notify_observers(), 0)
            
            return True
        return False
    
    def get_current_theme(self):
        return self.current_theme

# Глобальный экземпляр менеджера тем
theme_manager = ThemeManager()