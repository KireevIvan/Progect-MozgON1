from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window


class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20

        # Текущая тема: 'light' или 'dark'
        self.theme = 'light'
        self.update_theme()

        # Создаем кнопки
        self.btn_start = Button(text='Начать игру', size_hint=(1, 0.2))
        self.btn_stats = Button(text='Статистика', size_hint=(1, 0.2))
        self.btn_theme = Button(text='Сменить тему', size_hint=(1, 0.2))

        # Связываем кнопки с функциями
        self.btn_start.bind(on_press=self.start_game)
        self.btn_stats.bind(on_press=self.show_statistics)
        self.btn_theme.bind(on_press=self.change_theme)

        # Добавляем кнопки в макет
        self.add_widget(self.btn_start)
        self.add_widget(self.btn_stats)
        self.add_widget(self.btn_theme)

    def update_theme(self):
        if self.theme == 'light':
            Window.clearcolor = (1, 1, 1, 1)  # белый фон
        else:
            Window.clearcolor = (0.2, 0.3, 0.6, 1)  # темно-синий/голубой

    def start_game(self, instance):
        # Пока просто очищаем экран - создадим новый виджет с белым фоном
        self.clear_widgets()
        # Можно добавить сюда реальную кнопку начала игры позже
        self.add_widget(Button(text='Игра началась! (пока пусто)', size_hint=(1, 1)))

    def show_statistics(self, instance):
        self.clear_widgets()
        self.add_widget(Button(text='Статистика (пока пусто)', size_hint=(1, 1)))

    def change_theme(self, instance):
        # Переключение темы
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.update_theme()


class BrainOnApp(App):
    def build(self):
        return MainMenu()


if __name__ == '__main__':
    BrainOnApp().run()