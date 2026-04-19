from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from database import Database
from themes import theme_manager

class AccountItem(BoxLayout):
    def __init__(self, name, balance, currency, icon, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 70
        self.padding = [15, 10]
        self.spacing = 10
        
        icon_label = Label(text=icon, font_size=28, size_hint_x=0.15)
        info = Label(text=f"{name}\n[color=666666]{balance:,.0f} {currency}[/color]", 
                     markup=True, font_size=16, halign='left', size_hint_x=0.7)
        
        self.add_widget(icon_label)
        self.add_widget(info)

class DebtItem(BoxLayout):
    def __init__(self, name, amount, debt_type, date, description, debt_id, **kwargs):
        super().__init__(**kwargs)
        self.debt_id = debt_id
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = [15, 5]
        self.spacing = 10
        
        is_i_owe = debt_type == 'i_owe'
        sign = '-' if is_i_owe else '+'
        color = (0.8, 0.2, 0.2, 1) if is_i_owe else (0.2, 0.7, 0.2, 1)
        
        info = BoxLayout(orientation='vertical', size_hint_x=0.7)
        info.add_widget(Label(text=name, font_size=16, halign='left', size_hint_y=0.5))
        info.add_widget(Label(text=f"{date} | {description[:20]}", font_size=12, 
                             color=(0.5,0.5,0.5,1), halign='left', size_hint_y=0.5))
        
        amount_label = Label(text=f"{sign}{amount:,.0f} ₽", color=color, size_hint_x=0.2)
        
        delete_btn = Button(text='X', size_hint_x=0.1, background_color=(0.5,0,0,1))
        delete_btn.bind(on_press=self.delete_debt)
        
        self.add_widget(info)
        self.add_widget(amount_label)
        self.add_widget(delete_btn)
    
    def delete_debt(self, instance):
        app = App.get_running_app()
        accounts_screen = app.root.get_screen('accounts')
        accounts_screen.delete_debt(self, self.debt_id)

class OperationItem(BoxLayout):
    def __init__(self, trans_id, date, trans_type, category, amount, description, **kwargs):
        super().__init__(**kwargs)
        self.trans_id = trans_id
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 55
        self.padding = [15, 5]
        self.spacing = 10
        
        is_income = trans_type == 'income'
        sign = '+' if is_income else '-'
        color = (0.2, 0.7, 0.2, 1) if is_income else (0.8, 0.2, 0.2, 1)
        
        info = BoxLayout(orientation='vertical', size_hint_x=0.7)
        info.add_widget(Label(text=category, font_size=15, halign='left', size_hint_y=0.5))
        info.add_widget(Label(text=description[:25] if description else '', font_size=12, 
                             color=(0.5,0.5,0.5,1), halign='left', size_hint_y=0.5))
        
        amount_label = Label(text=f"{sign}{amount:,.0f} ₽", color=color, size_hint_x=0.2)
        
        delete_btn = Button(text='X', size_hint_x=0.1, background_color=(0.5,0,0,1))
        delete_btn.bind(on_press=self.delete_operation)
        
        self.add_widget(info)
        self.add_widget(amount_label)
        self.add_widget(delete_btn)
    
    def delete_operation(self, instance):
        app = App.get_running_app()
        ops_screen = app.root.get_screen('operations')
        ops_screen.delete_transaction(self, self.trans_id)

class AccountsScreen(Screen):
    """Экран счетов и долгов"""
    
    def on_enter(self):
        self.load_data()
    
    def load_data(self):
        db = App.get_running_app().db
        
        # Загружаем счета
        accounts = db.get_all_accounts()
        accounts_list = self.ids.get('accounts_list')
        if accounts_list:
            accounts_list.clear_widgets()
            
            for acc in accounts:
                acc_id, name, balance, currency, icon = acc
                item = AccountItem(name, balance, currency, icon)
                accounts_list.add_widget(item)
        
        # Загружаем долги
        debts = db.get_all_debts()
        debts_list = self.ids.get('debts_list')
        if debts_list:
            debts_list.clear_widgets()
            
            i_owe_total = 0
            owed_to_me_total = 0
            
            for debt in debts:
                debt_id, name, amount, debt_type, date, description = debt
                if debt_type == 'i_owe':
                    i_owe_total += amount
                else:
                    owed_to_me_total += amount
                
                item = DebtItem(name, amount, debt_type, date, description, debt_id)
                debts_list.add_widget(item)
            
            i_owe_label = self.ids.get('i_owe_label')
            if i_owe_label:
                i_owe_label.text = f"-{i_owe_total:,.0f} ₽"
            
            owed_label = self.ids.get('owed_to_me_label')
            if owed_label:
                owed_label.text = f"+{owed_to_me_total:,.0f} ₽"
    
    def delete_debt(self, item, debt_id):
        db = App.get_running_app().db
        db.delete_debt(debt_id)
        self.load_data()
    
    def show_add_account_dialog(self):
        popup = self.ids.get('add_account_popup')
        if popup:
            popup.opacity = 1
            popup.disabled = False
    
    def hide_add_account_dialog(self):
        popup = self.ids.get('add_account_popup')
        if popup:
            popup.opacity = 0
            popup.disabled = True
    
    def add_account(self):
        name_input = self.ids.get('account_name_input')
        balance_input = self.ids.get('account_balance_input')
        
        if not name_input or not balance_input:
            return
        
        name = name_input.text.strip()
        balance_text = balance_input.text.strip()
        
        if not name:
            return
        
        try:
            balance = float(balance_text) if balance_text else 0
        except ValueError:
            balance = 0
        
        db = App.get_running_app().db
        db.add_account(name, balance)
        
        name_input.text = ''
        balance_input.text = ''
        self.hide_add_account_dialog()
        self.load_data()
    
    def show_add_debt_dialog(self):
        popup = self.ids.get('add_debt_popup')
        if popup:
            popup.opacity = 1
            popup.disabled = False
    
    def hide_add_debt_dialog(self):
        popup = self.ids.get('add_debt_popup')
        if popup:
            popup.opacity = 0
            popup.disabled = True
    
    def add_debt(self):
        name_input = self.ids.get('debt_name_input')
        amount_input = self.ids.get('debt_amount_input')
        type_spinner = self.ids.get('debt_type_spinner')
        desc_input = self.ids.get('debt_description_input')
        
        if not all([name_input, amount_input, type_spinner]):
            return
        
        name = name_input.text.strip()
        amount_text = amount_input.text.strip()
        debt_type = type_spinner.text
        description = desc_input.text.strip() if desc_input else ''
        
        if not name or not amount_text:
            return
        
        try:
            amount = float(amount_text)
        except ValueError:
            return
        
        type_map = {'Я должен': 'i_owe', 'Мне должны': 'owed_to_me'}
        db_type = type_map.get(debt_type, 'owed_to_me')
        
        db = App.get_running_app().db
        db.add_debt(name, amount, db_type, description)
        
        name_input.text = ''
        amount_input.text = ''
        if desc_input:
            desc_input.text = ''
        self.hide_add_debt_dialog()
        self.load_data()

class OperationsScreen(Screen):
    """Экран операций с группировкой по дням"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_type = 'expense'
    
    def on_enter(self):
        self.load_operations()
    
    def load_operations(self):
        db = App.get_running_app().db
        grouped = db.get_transactions_grouped_by_day()
        
        operations_list = self.ids.get('operations_list')
        if operations_list:
            operations_list.clear_widgets()
            
            for date, transactions in grouped.items():
                # Заголовок с датой
                date_header = Label(text=date, font_size=18, bold=True, 
                                    size_hint_y=None, height=40, color=(0.3,0.6,0.9,1))
                operations_list.add_widget(date_header)
                
                # Транзакции за этот день
                for trans in transactions:
                    trans_id, trans_date, trans_type, category, amount, description = trans
                    item = OperationItem(trans_id, trans_date, trans_type, category, amount, description)
                    operations_list.add_widget(item)
    
    def delete_transaction(self, item, trans_id):
        db = App.get_running_app().db
        db.delete_transaction(trans_id)
        self.load_operations()
        # Обновляем другие экраны
        accounts_screen = self.manager.get_screen('accounts')
        if accounts_screen:
            accounts_screen.load_data()
        analytics_screen = self.manager.get_screen('analytics')
        if analytics_screen:
            analytics_screen.update_stats()
    
    def show_add_operation_dialog(self):
        popup = self.ids.get('add_operation_popup')
        if popup:
            popup.opacity = 1
            popup.disabled = False
            self.update_categories()
    
    def hide_add_operation_dialog(self):
        popup = self.ids.get('add_operation_popup')
        if popup:
            popup.opacity = 0
            popup.disabled = True
    
    def set_type(self, trans_type):
        self.transaction_type = trans_type
        
        # Меняем цвета кнопок
        expense_btn = self.ids.get('expense_btn')
        income_btn = self.ids.get('income_btn')
        
        if expense_btn and income_btn:
            if trans_type == 'income':
                income_btn.background_color = (0.2, 0.6, 0.2, 1)
                expense_btn.background_color = (0.3, 0.3, 0.3, 1)
            else:
                income_btn.background_color = (0.3, 0.3, 0.3, 1)
                expense_btn.background_color = (0.8, 0.2, 0.2, 1)
        
        self.update_categories()
    
    def update_categories(self):
        if self.transaction_type == 'income':
            categories = ['Зарплата', 'Фриланс', 'Подарок', 'Инвестиции', 'Другое']
        else:
            categories = ['Продукты', 'Транспорт', 'Кафе', 'Развлечения', 'Здоровье', 
                         'Одежда', 'ЖКХ', 'Связь', 'Обучение', 'Другое']
        
        category_spinner = self.ids.get('op_category_spinner')
        if category_spinner:
            category_spinner.values = categories
            category_spinner.text = categories[0]
    
    def save_transaction(self):
        amount_input = self.ids.get('op_amount_input')
        category_spinner = self.ids.get('op_category_spinner')
        desc_input = self.ids.get('op_description_input')
        
        if not all([amount_input, category_spinner]):
            return
        
        amount_text = amount_input.text.strip()
        category = category_spinner.text
        description = desc_input.text.strip() if desc_input else ''
        
        if not amount_text:
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                return
        except ValueError:
            return
        
        db = App.get_running_app().db
        db.add_transaction(self.transaction_type, category, amount, description, 1)
        
        amount_input.text = ''
        if desc_input:
            desc_input.text = ''
        
        self.hide_add_operation_dialog()
        self.load_operations()
        
        accounts_screen = self.manager.get_screen('accounts')
        if accounts_screen:
            accounts_screen.load_data()
        
        analytics_screen = self.manager.get_screen('analytics')
        if analytics_screen:
            analytics_screen.update_stats()

class AnalyticsScreen(Screen):
    """Экран аналитики"""
    
    def on_enter(self):
        self.update_stats()
    
    def update_stats(self):
        db = App.get_running_app().db
        summary = db.get_summary()
        expenses = db.get_expenses_by_category()
        
        total_income_label = self.ids.get('total_income_label')
        total_expense_label = self.ids.get('total_expense_label')
        balance_label = self.ids.get('balance_label')
        
        if total_income_label:
            total_income_label.text = f"+{summary['total_income']:,.0f} ₽"
        if total_expense_label:
            total_expense_label.text = f"-{summary['total_expense']:,.0f} ₽"
        if balance_label:
            balance_label.text = f"{summary['balance']:,.0f} ₽"
        
        stats_list = self.ids.get('stats_list')
        if stats_list:
            stats_list.clear_widgets()
            
            total = sum(exp[1] for exp in expenses)
            
            for category, amount in expenses:
                percentage = (amount / total * 100) if total > 0 else 0
                item = self.create_stat_item(category, amount, percentage)
                stats_list.add_widget(item)
    
    def create_stat_item(self, category, amount, percentage):
        container = BoxLayout(orientation='vertical', size_hint_y=None, height=60)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=0.5)
        header.add_widget(Label(text=category, font_size=14, halign='left'))
        header.add_widget(Label(text=f"{amount:,.0f} ₽ ({percentage:.1f}%)", 
                               font_size=14, halign='right'))
        
        progress = ProgressBar(max=100, value=percentage, size_hint_y=0.3)
        
        container.add_widget(header)
        container.add_widget(progress)
        
        return container

class MoreScreen(Screen):
    """Экран 'Еще' - настройки"""
    
    def on_enter(self):
        self.update_theme_switch()
    
    def update_theme_switch(self):
        """Обновляем состояние переключателя темы"""
        # Ищем переключатель в ids
        theme_switch = self.ids.get('theme_switch')
        if theme_switch:
            current_theme = theme_manager.get_current_theme()
            theme_switch.active = (current_theme == 'dark')
        
        # Обновляем статус
        theme_status = self.ids.get('theme_status')
        if theme_status:
            current_theme = theme_manager.get_current_theme()
            theme_status.text = "Темная тема" if current_theme == 'dark' else "Светлая тема"
    
    def toggle_theme(self, instance, value):
        """Переключение темы"""
        new_theme = 'dark' if value else 'light'
        if theme_manager.switch_theme(new_theme):
            # Обновляем статус
            theme_status = self.ids.get('theme_status')
            if theme_status:
                theme_status.text = "Темная тема" if value else "Светлая тема"
            
            # Обновляем все экраны для применения новой темы
            self.update_all_screens()
            
            # Показываем сообщение
            message_label = self.ids.get('message_label')
            if message_label:
                message_label.text = "✅ Тема изменена"
                Clock.schedule_once(lambda dt: self.clear_message(), 2)
    
    def clear_message(self):
        message_label = self.ids.get('message_label')
        if message_label:
            message_label.text = ""
    
    def update_all_screens(self):
        """Обновляем все экраны для применения новой темы"""
        # Принудительно перезагружаем данные на всех экранах
        for screen_name in ['accounts', 'operations', 'analytics']:
            screen = self.manager.get_screen(screen_name)
            if hasattr(screen, 'load_data'):
                screen.load_data()
            if hasattr(screen, 'load_operations'):
                screen.load_operations()
            if hasattr(screen, 'update_stats'):
                screen.update_stats()
        
        # Обновляем цвета на текущем экране
        self.apply_theme_to_widgets()
    
    def apply_theme_to_widgets(self):
        """Применяем тему к виджетам на текущем экране"""
        colors = theme_manager.get_all_colors()

        # Применяем фон для экрана
        container = self.ids.get('container')
        if container:
            container.canvas.before.clear()
            with container.canvas.before:
                Color(*colors['background'])
                Rectangle(pos=container.pos, size=container.size)
    
    def export_data(self):
        """Экспорт данных"""
        message_label = self.ids.get('message_label')
        if message_label:
            message_label.text = "📁 Экспорт данных будет доступен в следующей версии"
            Clock.schedule_once(lambda dt: self.clear_message(), 2)
    
    def backup_data(self):
        """Резервное копирование"""
        message_label = self.ids.get('message_label')
        if message_label:
            message_label.text = "💾 Резервное копирование будет доступно в следующей версии"
            Clock.schedule_once(lambda dt: self.clear_message(), 2)
    
    def reset_data(self):
        """Сброс данных"""
        message_label = self.ids.get('message_label')
        if message_label:
            message_label.text = "⚠️ Сброс данных будет доступен в следующей версии"
            Clock.schedule_once(lambda dt: self.clear_message(), 2)

class ZenMoneyApp(App):
    """Главный класс приложения"""
    
    def build(self):
        self.db = Database()
        
        sm = ScreenManager()
        sm.add_widget(AccountsScreen(name='accounts'))
        sm.add_widget(OperationsScreen(name='operations'))
        sm.add_widget(AnalyticsScreen(name='analytics'))
        sm.add_widget(MoreScreen(name='more'))
        
        return sm
    
    # def on_start(self):
    #     """При запуске применяем сохраненную тему"""
    #     colors = theme_manager.get_all_colors()
    #     if self.root:
    #         self.root.canvas.before.clear()
    #         with self.root.canvas.before:
    #             Color(*colors['background'])
    #             Rectangle(pos=self.root.pos, size=self.root.size)
    
    def on_stop(self):
        self.db.close()

if __name__ == '__main__':
    ZenMoneyApp().run()