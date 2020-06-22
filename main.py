import time
import os
import speech_recognition as sr
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel


class Voice_NotesApp(MDApp):
    text = None
    err_msg = None
    r = sr.Recognizer()
    m = sr.Microphone()
    SPLIT_WORD = ' разделение '
    FOLDER = 'other'

    def build(self):
        layout = PageLayout()

        page1 = GridLayout(rows=2)
        page1_label = MDLabel(text='Hello there', pos_hint={"center_x": 0.5,"center_y":0.5}, halign='center')
        page1_button = Button(text='Start voice record', size_hint=(.5, .1),
                              pos_hint={"center_x": 0.5, "center_y": 0.2},
                              )
        page1_button.bind(on_press=self.start_record)
        page1.add_widget(page1_label)
        page1.add_widget(page1_button)

        page2 = ScrollView(do_scroll_y=True, do_scroll_x=False, size_hint=(1, None), size=(Window.width, Window.height))
        page2_grid = GridLayout(cols=2, spacing=1, size_hint_y=None)
        page2_grid.bind(minimum_height=page2_grid.setter('height'))
        #check current folders and find .wav files
        folders = [f for f in os.listdir('./audio')]
        for folder in folders:
            btn = Button(text=str(folder), size_hint_y=None, height=50, )
            page2_grid.add_widget(btn)
            btn.bind(on_press=self.open_folder)
        page2.add_widget(page2_grid)

        page3 = ScrollView(do_scroll_y=True, do_scroll_x=False, size_hint=(1, None), size=(Window.width, Window.height))
        page3_grid = GridLayout(cols=2, spacing=1, size_hint_y=None)
        page3_grid.bind(minimum_height=page2_grid.setter('height'))
        page3.add_widget(page3_grid)

        layout.add_widget(page1)
        layout.add_widget(page2)
        layout.add_widget(page3)

        self.page2_grid = page2_grid
        self.page1_label = page1_label
        self.page1_button = page1_button
        self.page3_grid = page3_grid

        return layout

    def open_folder(self, instance):
        self.page3_grid.clear_widgets()
        folder = instance.text
        files = [f for f in os.listdir(f'./audio/{folder}') if f.endswith('.wav')]
        for f in files:
            self.page3_grid.add_widget(Button(text=str(f[:-4]), size_hint_y=None, height=50, ))

    def start_record(self, instance):
        instance.text = 'Recording'
        try:
            with self.m as source:
                self.r.adjust_for_ambient_noise(source)
            self.stop_listening = self.r.listen_in_background(self.m, self.record_callback)
            self.page1_button.unbind(on_press=self.start_record)
            self.page1_button.bind(on_press=self.stop_record)
        except:
            self.page1_label.text = 'Произошел прикол'

    def stop_record(self, instance):
        store = self.r.energy_threshold
        self.r.energy_threshold = 9001
        time.sleep(2.5)
        self.stop_listening()
        self.r.energy_threshhold = store
        instance.text = 'Start voice record'
        self.page1_button.unbind(on_press=self.stop_record)
        self.page1_button.bind(on_press=self.start_record)


    def record_callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language='ru')
            splitted_text = text.split(self.SPLIT_WORD)
            if len(splitted_text)>=2:
                self.FOLDER, self.text = splitted_text[0], splitted_text[1:]
            else:
                self.text = splitted_text[0]
            self.text = self.text[0]
            self.filename = ("{}.wav".format(str(self.text)))
            if not os.path.exists(f'./audio/{self.FOLDER}'):
                os.mkdir(f'./audio/{self.FOLDER}')
                self.page2_grid.add_widget(Button(text=str(self.FOLDER), size_hint_y=None, height=50))
            with open(f'./audio/{self.FOLDER}/{self.filename}', "wb") as f:
                f.write(audio.get_wav_data())
            self.page1_button.text = 'Click to stop record voice'
        except sr.UnknownValueError:
            self.err_msg = "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            self.err_msg = f"Could not request results from Google Speech Recognition service; {e}"


if __name__ == '__main__':
    app = Voice_NotesApp()
    app.run()