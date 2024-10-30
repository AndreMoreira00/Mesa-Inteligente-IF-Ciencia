import serial
import os
import pathlib
import json
from dotenv import load_dotenv
from monsterapi import client
import google.generativeai as genai

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
  # Função de envio de dados para API
def Gemini(image):
  image = {
    'mime_type': 'image/jpeg',
    'data': pathlib.Path(f'{image}').read_bytes()
  }
  
  response = model.generate_content(image)
  
  return response.text

# Configurando modelo Monsterapi
monster_client = client(API_KEY_MONSTERAPI)
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

def Conteudo_text(response):
  conteudo = {"response": f"{response}"}
  return conteudo

def Conteudo_img(response):
  conteudo = {"response": f"{response}"}
  return conteudo

def JSON(conteudo):
  with open("dados.json", "w", encoding="utf-8") as json_conteudo:
    json.dump(conteudo, json_conteudo, ensure_ascii=False, indent=4)
    
# Arduino

while True: 
  try:  
    arduino = serial.Serial('COM4', 9600)
    print('Arduino conectado')
    break

  except:
    pass

while True: 
  msg = str(arduino.readline()) 
  msg = msg[2:-5] 
  if msg == "S":
    image = 'images\manos.jpg'

    response = Gemini(image)

    if "desenho" in response:
      url = Monsterapi(response)
      conteudo = Conteudo_text(url)
      print(conteudo)
    elif "desenho" not in response:
      conteudo = Conteudo_text(response)
      print(conteudo)
      
    # with open('dados.json', 'r', encoding="utf-8") as json_file:
    #   resposta = json.load(json_file)
      
    # print(resposta)

  arduino.flush() 
