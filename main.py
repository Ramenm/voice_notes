import datetime
import threading
from kivymd.app import MDApp
from kivy.uix.pagelayout import PageLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.uix.button import Button
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
import speech_recognition as sr
import os


class Voice_NotesApp(MDApp):
    text = None
    err_msg = None
    r = sr.Recognizer()
    m = sr.Microphone()
    def build(self):
        layout = PageLayout()

        page1 = GridLayout(rows = 2)
        page1_label = MDLabel(text='Приветики', pos_hint={"center_x": 0.5,"center_y":0.5}, halign='center')
        page1_button = Button(text='Начать запись голоса', size_hint=(.5, .1),
                              pos_hint={"center_x": 0.5, "center_y": 0.2},
                              )
        page1_button.bind(on_press=self.start_record)

        page2 = ScrollView(do_scroll_y=True, do_scroll_x=False, size_hint=(1, None), size=(Window.width, Window.height))
        page2_grid = GridLayout(cols=1, spacing=1, size_hint_y=None)
        page2_grid.bind(minimum_height=page2_grid.setter('height'))
        #check current dictionary and find .wav files
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.wav')]
        for name in files:
            page2_grid.add_widget(Button(text=str(name[:-4]), size_hint_y=None, height=50))
        page2.add_widget(page2_grid)

        page1.add_widget(page1_label)
        page1.add_widget(page1_button)
        layout.add_widget(page1)
        layout.add_widget(page2)

        self.page2_grid = page2_grid
        self.page1_label = page1_label
        self.page1_button = page1_button

        return layout


    def start_record(self, instance):
        instance.text = 'Recording'
        try:
            with self.m as source:
                self.r.adjust_for_ambient_noise(source)
            self.stop_listening = self.r.listen_in_background(self.m, self.callback)
            print('start')
        except:
            self.page1_label.text = 'Произошел прикол'


    def stop_record(self, instance):
        self.stop_listening()
        instance.text = 'Start voice record'
        print(self.text, self.err_msg)
        self.page1_button.unbind(on_press=self.stop_record)
        self.page1_button.bind(on_press=self.start_record)
        print('stop')



    def callback(self, recognizer, audio):
        try:
            self.text = recognizer.recognize_google(audio, language='ru')
            self.filename = ("{}.wav".format(str(self.text) if self.text.count(' ')>=2 else str(datetime.datetime.now()).replace(' ', '-').replace(':','-')))
            with open(self.filename, "wb") as f:
                f.write(audio.get_wav_data())
            self.page2_grid.add_widget(Button(text=self.text, size_hint_y=None, height=50))
            self.page1_button.text = 'Click to stop record voice'
            self.page1_button.unbind(on_press=self.start_record)
            self.page1_button.bind(on_press=self.stop_record)


        except sr.UnknownValueError:
            self.err_msg = "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            self.err_msg = "Could not request results from Google Speech Recognition service; {0}".format(e)




if __name__ == '__main__':
    app = Voice_NotesApp()
    app.run()