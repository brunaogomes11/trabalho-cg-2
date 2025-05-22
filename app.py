from flask import Flask, render_template, request, url_for
from PIL import Image
import os

# Importando os filtros personalizados
import tools
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        filtro_nome = request.form.get('filtro')
        file = request.files['imagem']
        imagem_existente = request.form.get('imagem_existente')

        if file and file.filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(img_path)
            img_filename = file.filename
        elif imagem_existente:
            # Extrai apenas o nome do arquivo da URL recebida
            img_filename = os.path.basename(imagem_existente)
            img_path = os.path.join(UPLOAD_FOLDER, img_filename)
        else:
            img_filename = None
            img_path = None

        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)

            filtros_disponiveis = {
                'negativo' : tools.filtro_negativo,
                'gray' : tools.filtro_gray,
                'mediana' : tools.filtro_mediana,
                'blur' : tools.filtro_blur,
                'gaussiano' : tools.filtro_gaussiano,
                'correcao_gamma' : tools.filtro_correcao_gamma,
                'contorno' : tools.filtro_contorno,
                'contorno_sobel' : tools.filtro_contorno_sobel,
                'contorno_laplaciano' : tools.filtro_laplaciano,
            }

            func_filtro = filtros_disponiveis.get(filtro_nome, lambda x: x)
            img_processada = func_filtro(img)

            processed_path = os.path.join(PROCESSED_FOLDER, img_filename)
            img_processada.save(processed_path)

            # Gere as URLs corretas para as imagens
            original_url = url_for('static', filename=f'uploads/{img_filename}')
            processada_url = url_for('static', filename=f'processed/{img_filename}')

            # Lista todas as imagens em uploads
            imagens = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]

            filtro_nome_formatado = {
                'negativo' : 'Negativo',
                'gray' : 'Escala de Cinza',
                'mediana' : 'Mediana',
                'blur' : 'Blur',
                'gaussiano' : 'Gaussiano',
                'correcao_gamma' : 'Correção Gamma',
                'contorno' : 'Detecção de bordas',
                'contorno_sobel' : 'Detecção de bordas Sobel',
                'contorno_laplaciano' : 'Detecção de bordas Laplaciano',
            }
            
            # Caminhos para salvar os histogramas
            hist_original = os.path.join(PROCESSED_FOLDER, f'hist_{img_filename}')
            hist_processada = os.path.join(PROCESSED_FOLDER, f'hist_proc_{img_filename}')

            tools.salvar_histograma(img, hist_original)
            tools.salvar_histograma(img_processada, hist_processada)

            # URLs dos histogramas para passar ao template
            hist_original_url = url_for('static', filename=f'processed/hist_{img_filename}')
            hist_processada_url = url_for('static', filename=f'processed/hist_proc_{img_filename}')
            
            return render_template(
                'index.html',
                original=original_url,
                processada=processada_url,
                filtro=filtro_nome_formatado[filtro_nome],
                imagens=imagens,
                hist_original=hist_original_url,
                hist_processada=hist_processada_url,
            )
    for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)