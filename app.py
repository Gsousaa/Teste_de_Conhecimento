#Bibliotecas Utilizadas
from flask import Flask, render_template, request #Biblioteca para criar a API
import base64 #Biblioteca para codificar e decodificar as imagens
from cv2 import cv2 #Biblioteca Opencv para Tratamento da imagem
from io import BytesIO #Biblioteca para codificar e decodificar as imagens
from PIL import Image #Biblioteca para Leitura de Imagem
import sqlite3 #Bilioteca para o banco de dados
import pytesseract #Biblioteca para extração do texto de imagem

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract' #Caminho para acessar o tesseract para extração

app = Flask(__name__)

@app.route('/', methods = ["POST"])#Utilizando o metodo Post, pois será enviado o arquivo json com as informacoes
def ImageBase64():
    banco = sqlite3.connect('dado.db')
    cursor = banco.cursor()

#Recebe o código Base 64 e transforma em uma imagem
    body = request.get_json() #Realiza a Leitura do Json recebido pela API
    if (body == {}):
        return "Informação inválida, favor entrar com o Image Name e Base64 Code no body em formato Json. Conforme exemplo abaixo: \n {\n     "'Image Name'": "'Nome Image'",\n    "'Base64 Code'": "'Codigo'"\n}"

    file = "data:"+body["Image Name"]+":/png;base64,"+body["Base64 Code"] #Será recebido pela api o nome da imagem e o código Base64
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii") #Decodificando o código base64
    im = Image.open(BytesIO(base64.b64decode(image_data))) #Abrindo a imagem decodificada
    im.save(body["Image Name"]+".png") #Salva a imagem

#Inicializa a tratativa da imagem para remover os ruidos presentes
    image= cv2.imread(body["Image Name"]+".png") #Realiza a abertura para iniciar a tratativa de ruido
    image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    se=cv2.getStructuringElement(cv2.MORPH_RECT , (2,3))
    bg=cv2.morphologyEx(image, cv2.MORPH_DILATE, se)
    out_gray=cv2.divide(image, bg, scale=150)
    out_binary=cv2.threshold(out_gray, 0, 260, cv2.THRESH_OTSU )[1] #Finalização da tratativa de ruido
    cv2.imwrite(body["Image Name"]+"_Ajustado.png",out_binary)
    
#Realiza a extração do Texto presente no OCR da Imagem.
    Text_ocr = pytesseract.image_to_string(out_binary,lang='eng')

#Realiza a códificação da imagem tratada
    with open(body["Image Name"]+"_Ajustado.png", "rb") as image_file:
        data = base64.b64encode(image_file.read())

#Adicionando Dados ao Banco de Dados.
    cursor.execute("INSERT INTO Image VALUES('"+body["Image Name"]+"','"+body["Base64 Code"]+"','"+str(data).replace("b","").replace("'","")+"','"+Text_ocr+"')")
    banco.commit()
    return "Dados Adicionados e Tratados com Sucesso"