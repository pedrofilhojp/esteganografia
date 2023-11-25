#!/usr/bin/python3

#   Autor: Pedro Filho
#   Email: pedro.filho.jp@gmail.com
#   Criado em 08/Jun/2020, atualizado em 22 Nov 2023 (Conferencia Tempest)
#   
#   Este é um algoritmo para realizar esteganografia utilizando o bit
#   menos significativo do pixel. 
#   Para cada letra, será utilizado 3 pixels, o algoritmo segue a sequencia:
#   1º Pega letra
#   2º Extrai seu valor de código ASCII, converte em binário, e complementa esse número binário
#       com zeros a esquerda para conter 9 bits
#   3º Separa esse número binário em 3 partes com 3 bits cada
#   4º Para cada parte (3bits), utiliza 1 pixel para esconder esses bits dentro das cores RGB
#   5º Insere por fim, três caracteres um delimitador (#) para sinalizar o algoritmo que alí finaliza o texto
#   

from PIL import Image
import sys

# Print na tela algumas informacoes de conversao do pixel
DEBUG=True

#caracter delimitador, sera inserido 3 desses caracteres no fim da mensagem
DELIMITER='#'

# Valores de referencia da matriz da imagem durante a leitura de cada pixel
POS_WIDTH=0
POS_HEIGHT=0

# Tamanho da imagem
WIDTH=0
HEIGHT=0

#
# Abre a imagem
#
def open_image(path):
  newImage = Image.open(path)
  return newImage

#
# Salva a imagem
#
def save_image(image, path):
  image.save(path, 'png')

#
# Cria uma nova imagem com fundo branco
#
def create_image(i, j):
  image = Image.new("RGB", (i, j), "black")
  return image

#
# Retorna 1 pixel da imagem
#
def get_pixel(image, i, j):
    # Inside image bounds?
    width, height = image.size
    if i > width or j > height:
      return None

    # Get Pixel
    pixel = image.getpixel((i, j))
    return pixel

################ Extrair Texto ###########################
# Extrai o texto da imagem
#
def decript(image):
    # pegando tamanho da imagem
    width, height = image.size

    # Carrega o mapeamento de pixels   
    pixels = image.load()

    count_3pixels = 0
    letra_bits = ''
    count_delimiter = 0
    text_output = ''
    for i in range(width):
        for j in range(height):
            count_3pixels +=1 
        
            # Pega o pixel correspondente
            pixel = get_pixel(image, i, j)

            # Pega o ultimo bit de cada cor do pixel
            bits = get_3bits_from_pixel(pixel)
            
            # Quando somar 9 bits, converte os bits em letra
            letra_bits = letra_bits+bits

            if (count_3pixels == 3):
                #converte os 9 bits em letra
                letter = get_letter_from_bits(letra_bits)
                text_output = text_output+letter                
                
                if (letter == DELIMITER):                    
                    count_delimiter +=1
                    # Quando encontrar o 3 caracteres delimitador, mostra a mensagem
                    # e sai do algoritmo
                    if (count_delimiter == 3):
                        print(text_output)
                        exit(0)
                else:
                    count_delimiter = 0               

                count_3pixels = 0                
                letra_bits = '' #inicia uma nova letra
                  
    return pixels

#
# Pega o ultimo bit de cada cor do pixel
#
def get_3bits_from_pixel(pixel):
    # Pega os valores de R, G, B e converte para binario
    r = str(bin(pixel[0])[2:])  # Red
    g = str(bin(pixel[1])[2:])  # Green
    b = str(bin(pixel[2])[2:])  # blue

    # Pegando ultimo digito
    r = (r)[-1]  # Red
    g = (g)[-1]  # Green
    b = (b)[-1]  # blue
        
    bits = r+g+b
    
    return bits

#
# Converte os bits em letra
#
def get_letter_from_bits(bits):    
    ascii_code = int(bits, 2)

    # Converte codigo ASCII em caractere
    letter = chr(ascii_code)
    
    return letter

################## Inserir Texto ###########################
# Funcao para inserir o texto na imagem
# 
# @param image
# @param text 
#
# return Image
#
def encript(image, text):
    #global POS_WIDTH, POS_HEIGHT

    # pegando tamanho da imagem
    width, height = image.size
    
    # Pega o mapeamento de pixels
    pixels = image.load()
       
    # Ler cada letra do texto    
    for letter in text:
        # Envia a letra para ser inserida em 3 pixels
        # obtém como retorno, o mapa completo de pixels com os 3 pixels modificado
        pixels = put_letter_in_3pixels(image, pixels, letter)
       
    # Adicionar o caractere delimitador no final da mensagem
    pixels = put_letter_in_3pixels(image, pixels,DELIMITER)
    pixels = put_letter_in_3pixels(image, pixels,DELIMITER)
    pixels = put_letter_in_3pixels(image, pixels,DELIMITER)
   
    return image

#
# Insere 1 letra em 3 pixels da imagem
#
# @param image  Imagem de trabalho
# @param pixels Mapa de pixels imagem
# @param letter Letra que sera inserida
# 
# return pixels Mapa de pixel modificado
#
def put_letter_in_3pixels(image, pixels,letter):
    global POS_WIDTH
    global POS_HEIGHT
    global DEBUG

    # pegando tamanho da imagem
    width, height = image.size

    # Transforma a letra em 9 bits, equivalente a 3 pixels
    letter_bits = get_bits_from_letter(letter,9)

    # Separa os 9 bits em grupos de 3 bits
    bits = []
    bits.insert(0,(letter_bits)[0:3])   # pega o 1º grupo de 3 bits
    bits.insert(1,(letter_bits)[3:6])   # pega o 2º grupo de 3 bits
    bits.insert(2,(letter_bits)[6:9])   # pega o 3º grupo de 3 bits
    
    if (DEBUG):
        print("")
        print("Letra: "+letter+" ["+letter_bits+"]")
    
    count_3pixels = 0
    for i in range(POS_WIDTH,width):        
        for j in range(POS_HEIGHT,height):

            # Pega o pixel correspondente
            pixel = get_pixel(image, i, j)
                        
            # Insere o pixel modificado no mapa de pixels
            new_pixel = put_3bits_in_pixel(bits[count_3pixels], pixel);
            pixels[i, j] = new_pixel
            # print("width:"+str(width)+" height:"+str(height)+" || i="+str(i)+" POS_WIDTH: "+str(POS_WIDTH)+ "|| j="+str(j)+ " POS_HEIGHT:"+str(POS_HEIGHT))

            # No 3º pixel, retorna o mapa de pixel modificado
            if (count_3pixels == 2):                
                count_3pixels = 0

                # Caso chegue perto do fim da coluna e não cabe o próximo píxel, joga para próxima coluna
                if ( j == (height-1) ):
                    POS_HEIGHT = 0
                    POS_WIDTH +=1
                else:
                    POS_HEIGHT = j+1

                return pixels
                
            count_3pixels += 1

            # Caso chegue perto do fim da coluna e não cabe o próximo píxel, joga para próxima coluna
            if ( j == (height-1) ):
                POS_HEIGHT = 0
                POS_WIDTH +=1

    return pixels

#
# Adicionar 3 bits no pixel RGB
# Retorna uma tupla com os palores de RGB
#
# @param bits 3 bits
# @param pixel pixel em RGB da imagem
#
# @return pixel em tupla
#
def put_3bits_in_pixel(bits, pixel):
    # Pega os valores de R, G, B e converte para binario
    r = str(bin(pixel[0])[2:])  # Red
    g = str(bin(pixel[1])[2:])  # Green
    b = str(bin(pixel[2])[2:])  # blue
    
    # Preenchendo com 0 se tiver menos de [total_bits] bits
    r = transf_bit(r, 8)
    g = transf_bit(g, 8)
    b = transf_bit(b, 8)

    b1 = (bits)[0:1] # 1º bit
    b2 = (bits)[1:2] # 2º bit
    b3 = (bits)[2:3] # 3º bit

    # altera apenas o ultimo bit do pixel para o valor do bit
    r = (r)[0:7]+b1
    g = (g)[0:7]+b2
    b = (b)[0:7]+b3

    #Transforma em decimal cada valor antes de retornar
    pixel = (int(r,2), int(g,2), int(b,2), pixel[3])

    if (DEBUG):
        print("r:"+str(r)+" g:"+str(g)+" b:"+str(b)+" ["+ bits +"]")

    return pixel

#
# Retorna o valor em N bits da letra
# 
# @param letter Letra enviada por parâmetro
# @param total_bits total de bits para preenchimento
#
# return List bits
#
def get_bits_from_letter(letter,total_bits):
    x = ord(letter)         # Pega o codigo ASCII em decimal
    b1 = str(bin(x)[2:])    # transforma decimal em binario

    # Preenchendo com 0 se tiver menos de [total_bits] bits
    b1 = transf_bit(b1, total_bits)

    return b1

#
# Preenche com zeros o digito binario para completar o total de "total_bits"
#
def transf_bit(bit,total_bits):

    len_b1 = len(bit)     
    if (len_b1 < total_bits):
        for i in range(total_bits-len_b1):
            bit="0"+bit
            
    return bit



if __name__ == "__main__":

    if (len(sys.argv) < 3):
        print('Erro na passagem dos parâmetros')
        print('--------------------------------')
        print('Para realizar a esteganogra utilize o paramtro (e):')
        print('./script.py e ifpb.png')
        print(' ')
        print('Para realizar a extrair utilize o parametro (d):')
        print('./script.py d new_imagem.png')        
        exit(1)

    option = sys.argv[1]
    file = sys.argv[2]

    # Realiza a esteganografia
    if (option == 'e'):
        # Captura texto como stdin
        text = input('Insira o texto: ')
        
        image = open_image(file)    
        new = encript(image, text)        
        save_image(new, 'new_image.png')
        print('Criado o arquivo new_image.png')

    # Extrai o texto              
    elif(option == 'd'):
        image = open_image(file)
        decript(image)
    else:
        print('Opcao nao existe')
    
    


