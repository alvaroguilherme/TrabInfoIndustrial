from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder

class MainApp(App):
    """
    Classe com App
    """
    def build(self):
        self.__widget =  MainWidget()
        return self.__widget

if __name__ == '__main__':
    Builder.load_string(open('mainwidget.kv',encoding='utf8').read(),rulesonly=True)
    MainApp().run()