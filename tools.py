from PIL import Image
# Função para converter uma string em binário
def str_to_bin(text):
    return ''.join(format(ord(c), '08b') for c in text)

# Função para converter binário em string
def bin_to_str(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(char, 2)) for char in chars])

# Função para esconder texto em imagem usando LSB
def hide_text_in_image(image_path, output_path, secret_text):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    binary_text = str_to_bin(secret_text) + '1111111111111110'  # delimitador de fim
    idx = 0

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if idx < len(binary_text):
                r = (r & ~1) | int(binary_text[idx])
                idx += 1
            if idx < len(binary_text):
                g = (g & ~1) | int(binary_text[idx])
                idx += 1
            if idx < len(binary_text):
                b = (b & ~1) | int(binary_text[idx])
                idx += 1
            pixels[x, y] = (r, g, b)
            if idx >= len(binary_text):
                break
        if idx >= len(binary_text):
            break

    img.save(output_path)
    print(f"Texto oculto com sucesso em '{output_path}'")

# Função para extrair texto da imagem
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    binary_text = ''
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_text += str(r & 1)
            binary_text += str(g & 1)
            binary_text += str(b & 1)

    # Encontrar delimitador de fim
    end_index = binary_text.find('1111111111111110')
    if end_index != -1:
        binary_text = binary_text[:end_index]
        return bin_to_str(binary_text)
    else:
        return "Delimitador de fim não encontrado."

