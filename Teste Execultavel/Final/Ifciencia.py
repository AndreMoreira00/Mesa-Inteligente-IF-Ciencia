import os
import pathlib
import json
from dotenv import load_dotenv
from monsterapi import client
import google.generativeai as genai
import sys

if getattr(sys, 'frozen', False):
    # Quando rodando como um executável
    caminho_base = pathlib.Path(sys._MEIPASS)
else:
    # Quando rodando como script normal
    caminho_base = pathlib.Path(__file__).parent

caminho_para_arquivo = caminho_base / "seu_arquivo_ou_diretorio"


# Carregando chaves
# load_dotenv()
# API_KEY_GEMINI = os.environ["API_KEY_GEMINI"]
# API_KEY_MONSTERAPI = os.environ['API_KEY_MONSTERAPI']
# URL = os.environ["URL"]

# Configurando modelo do Gemini
genai.configure(api_key=os.environ["API_KEY_GEMINI"])
model = genai.GenerativeModel(
  'gemini-1.5-flash',
  system_instruction="""
  Responda em Português; 
  Se tiver contas resolva; 
  Se tiver um desenho sem numeros e letras o descreva detalhadamente e de forma criativa (Desconsidere as cores);
  """,
  generation_config=genai.GenerationConfig(
    max_output_tokens=1000,
    temperature=0.5
  )
)

# Configurando modelo Monsterapi
monster_client = client(API_KEY_MONSTERAPI)

# Função de envio de dados para API
def Gemini(image):
  image = {
    'mime_type': 'image/jpeg',
    'data': pathlib.Path(f'{image}').read_bytes()
  }
  
  response = model.generate_content(image)
  
  return response.text

# Função de envio de dados para API
def Monsterapi(response):
  model = 'txt2img'
  input_data = {
  'prompt': f'{response}',
  'safe_filter': True,
  'samples': 1,
  'steps': 50,
  'aspect_ratio': 'square',
  'guidance_scale': 7.5,
  'seed': 2414,
  'style': 'anime'
  }

  result = monster_client.generate(model, input_data)

  return result['output']

# App

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import cv2
import time
import requests
from kivy.graphics.texture import Texture


# Classe que cria um rótulo (Label) com rolagem
class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollableLabel, self).__init__(**kwargs)
        
        self.label = Label(
            text="Text render...",
            font_size='20sp',
            color=(1,1,1,1),
            size_hint_y=None,  # Permite o ScrollView rolar o texto
            halign='left',
            valign='top',
            text_size=(Window.width * 0.9, None),  # Ajusta a largura do texto   
        )
        
        self.label.bind(texture_size=self.update_height)
        self.add_widget(self.label)
    
    def update_height(self, *args):
        self.label.height = self.label.texture_size[1]
        self.label.text_size = (self.width * 0.9, None)

    def update_text(self, new_text):
        self.label.text = new_text


# Classe da câmera
class CameraWidget(Image):
    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            self.texture = texture


# Botão com bordas arredondadas
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0,0,0,0)
        
        with self.canvas.before:
            Color(0.706, 0.11, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# Aplicação principal
class AssistenteApp(App):
    def build(self):
        Window.clearcolor = (0.157, 0.169, 0.157, 1)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Adiciona o widget da câmera
        self.camera_widget = CameraWidget(size_hint=(0.9, 0.5), pos_hint={'center_x': 0.5, 'top': 1})
        self.camera_widget.id = 'camera'
        self.layout.add_widget(self.camera_widget)

        # Cria o ScrollableLabel para textos longos
        self.scrollable_label = ScrollableLabel(size_hint=(0.9, 0.3), pos_hint={'center_x': 0.5, 'top': 0.48})
        self.layout.add_widget(self.scrollable_label)

        # Botão para capturar a imagem da câmera
        button = RoundedButton(
            text='Capturar',
            font_size='20sp',
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1)
        )
        button.bind(on_press=self.capture)
        self.layout.add_widget(button)

        return self.layout

    # Função de captura da imagem
    def capture(self, *args):
        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.camera_widget.export_to_png(f"./Images_input/IMG_{timestr}.png")
        time.sleep(5)
        response = Gemini(f'./Images_input/IMG_{timestr}.png')

        if "desenho" in response:
            url = Monsterapi(response)
            time.sleep(40)
            self.load_image_from_url(url[0])
        elif "desenho" not in response:
            self.update_label_text(response)

    # Atualiza o texto dentro do ScrollableLabel
    def update_label_text(self, new_text):
        self.scrollable_label.update_text(new_text)

    # Função para carregar a imagem de uma URL
    def load_image_from_url(self, url):
        try:
            self.layout.remove_widget(self.scrollable_label)
            self.url_image = Image(size_hint=(0.9, 0.5), pos_hint={'x': 0, 'y': 0.5})
            self.layout.add_widget(self.url_image)
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                image_path = './Images_output/monsterapt_image.png'
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                self.url_image.source = image_path
                self.url_image.reload()
            else:
                print(f"Erro ao baixar a imagem. Código de status: {response.status_code}")
        except Exception as e:
            print(f"Erro ao carregar a imagem da URL: {e}")


if __name__ == '__main__':
    AssistenteApp().run()