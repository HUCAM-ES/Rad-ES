from django.apps import AppConfig
import webbrowser


class HucamSiteConfig(AppConfig):
    name = 'dose_app'

    def ready(self):
        url = 'http://127.0.0.1:8000/'

        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

        webbrowser.get(chrome_path).open(url)

