from flask import Flask, render_template, request, url_for, redirect
from PIL import Image
import os
from werkzeug.utils import secure_filename

# Importando os filtros personalizados
import tools
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def get_image_files(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(tuple(ALLOWED_EXTENSIONS))]

@app.route('/', methods=['GET', 'POST'])
def index():
    active_tab_source = request.form.get('action') if request.method == 'POST' else request.args.get('active_tab', 'hide_text')

    context = {
        'imagens': get_image_files(UPLOAD_FOLDER),
        'active_tab': active_tab_source,
        'steganography_result': None,
        'processed_image_hide_url': None,
        'processed_hide_filename': None,
        'extracted_text': None,
        'original_hide': None,
        'original_extract': None,
        'hide_text_error': None,
        'extract_text_error': None,
    }

    if request.method == 'POST':
        action = request.form.get('action')
        context['active_tab'] = action

        if action == 'clear_all_images':
            for folder_to_clear in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
                if os.path.exists(folder_to_clear):
                    for filename in os.listdir(folder_to_clear):
                        file_path = os.path.join(folder_to_clear, filename)
                        try:
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                        except Exception as e:
                            app.logger.error(f'Failed to delete {file_path}. Reason: {e}')
            return redirect(url_for('index'))

        img_path = None
        img_filename = None
        imagem_existente_url = request.form.get('imagem_existente')
        file = request.files.get('imagem')
        
        current_image_url_for_form = None # For repopulating form on error

        if file and file.filename != '':
            filename_lower = file.filename.lower()
            if any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                img_filename = secure_filename(file.filename)
                img_path = os.path.join(UPLOAD_FOLDER, img_filename)
                file.save(img_path)
                context['imagens'] = get_image_files(UPLOAD_FOLDER) # Refresh image list
                current_image_url_for_form = url_for('static', filename=f'{UPLOAD_FOLDER.split(os.sep)[-1]}/{img_filename}')
            else: # Invalid file type uploaded
                img_filename = None # Ensure it's None if type is bad
                img_path = None
        elif imagem_existente_url:
            current_image_url_for_form = imagem_existente_url # This is the URL from the form
            img_filename = os.path.basename(imagem_existente_url)
            static_url_prefix = url_for('static', filename='')
            if imagem_existente_url.startswith(static_url_prefix):
                relative_path_from_static = imagem_existente_url[len(static_url_prefix):]
                # Check both UPLOAD_FOLDER and PROCESSED_FOLDER
                # The filename is os.path.basename(relative_path_from_static)
                base_filename_from_url = os.path.basename(relative_path_from_static)
                potential_upload_path = os.path.join(UPLOAD_FOLDER, base_filename_from_url)
                potential_processed_path = os.path.join(PROCESSED_FOLDER, base_filename_from_url)

                if os.path.exists(potential_upload_path):
                    img_path = potential_upload_path
                    img_filename = base_filename_from_url
                elif os.path.exists(potential_processed_path):
                    img_path = potential_processed_path
                    img_filename = base_filename_from_url
            else: # Fallback if not a static URL (should not happen with current JS)
                potential_upload_path = os.path.join(UPLOAD_FOLDER, img_filename)
                if os.path.exists(potential_upload_path):
                     img_path = potential_upload_path


        if action == 'hide_text':
            if current_image_url_for_form:
                context['original_hide'] = current_image_url_for_form
            
            if not img_path or not os.path.exists(img_path):
                context['hide_text_error'] = "Por favor, selecione uma imagem válida."
            else:
                secret_text = request.form.get('secret_text')
                if not secret_text:
                    context['hide_text_error'] = "Erro: Texto secreto não fornecido."
                else:
                    base, ext = os.path.splitext(img_filename)
                    processed_filename = f"{secure_filename(base)}_hidden{ext}"
                    output_path = os.path.join(PROCESSED_FOLDER, processed_filename)
                    try:
                        tools.hide_text_in_image(img_path, output_path, secret_text)
                        context.update({
                            'steganography_result': f"Texto oculto com sucesso em '{processed_filename}'!",
                            'processed_image_hide_url': url_for('static', filename=f'processed/{processed_filename}'),
                            'processed_hide_filename': processed_filename
                        })
                    except Exception as e:
                        context['steganography_result'] = f"Erro ao ocultar texto: {str(e)}"

        elif action == 'extract_text':
            if current_image_url_for_form:
                context['original_extract'] = current_image_url_for_form

            if not img_path or not os.path.exists(img_path):
                context['extract_text_error'] = "Por favor, selecione uma imagem válida."
            else:
                try:
                    extracted_text = tools.extract_text_from_image(img_path)
                    context['extracted_text'] = extracted_text
                except Exception as e:
                    context['extracted_text'] = f"Erro ao extrair texto: {str(e)}"
        
        # If there was an error message set, keep the selected image in the form
        if context['hide_text_error'] and not context['original_hide'] and current_image_url_for_form:
            context['original_hide'] = current_image_url_for_form
        if context['extract_text_error'] and not context['original_extract'] and current_image_url_for_form:
            context['original_extract'] = current_image_url_for_form


    elif request.method == 'GET':
        if not request.args and os.path.exists(PROCESSED_FOLDER): # Clear processed on "fresh" load
            for filename in os.listdir(PROCESSED_FOLDER):
                file_path = os.path.join(PROCESSED_FOLDER, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    app.logger.error(f'Failed to delete {file_path}. Reason: {e}')
        # context['imagens'] is already populated for GET
        # context['active_tab'] is set based on args or default.
    
    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)