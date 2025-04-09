from flask import render_template, request, send_from_directory, send_file
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from pdf2image import convert_from_path
from manipulacaoPDF import app, enviados, convertidos
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import os
import zipfile
import io
import tempfile

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/pdf-word')
def pdf_word():
    return render_template('pdf-word.html')

@app.route('/upload-pdf-word', methods=['POST'])
def upload_pdf_word():
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(enviados, filename)
    file.save(input_path)

    base_name = os.path.splitext(filename)[0]
    convertido_docx = f"{base_name}.docx"
    output_path = os.path.join(convertidos, convertido_docx)

    converter = Converter(input_path)
    converter.convert(output_path)
    converter.close()

    return render_template("resultado-docx.html", arquivo_convertido=convertido_docx)

@app.route('/pdf-png')
def pdf_png():
    return render_template('pdf-png.html')

@app.route('/upload-pdf-png', methods=['POST'])
def upload_pdf_png():
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(enviados, filename)
    file.save(input_path)

    base_name = os.path.splitext(filename)[0]

    images = convert_from_path(input_path)
    image_paths = []

    for i, img in enumerate(images):
        image_filename = f"{base_name}_pagina_{i+1}.png"
        image_path = os.path.join(convertidos, image_filename)
        img.save(image_path, 'PNG')
        image_paths.append(image_filename)

    return render_template("resultado-img.html", imagens=image_paths)

@app.route('/pdf-jpeg')
def pdf_jpeg():
    return render_template('pdf-jpeg.html')

@app.route('/upload-pdf-jpeg', methods=['POST'])
def upload_pdf_jpeg():
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(enviados, filename)
    file.save(input_path)

    base_name = os.path.splitext(filename)[0]

    images = convert_from_path(input_path)
    image_paths = []

    for i, img in enumerate(images):
        image_filename = f"{base_name}_pagina_{i+1}.jpeg"
        image_path = os.path.join(convertidos, image_filename)
        img.save(image_path, 'JPEG')
        image_paths.append(image_filename)

    return render_template("resultado-img.html", imagens=image_paths)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(convertidos, filename, as_attachment=True)


@app.route('/download-selected-zip', methods=['POST'])
def download_selected_zip():
    selected_files = request.form.getlist('selected_images')
    if not selected_files:
        return "Nenhuma imagem selecionada", 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for img_name in selected_files:
            img_path = os.path.join(convertidos, img_name)
            if os.path.exists(img_path):
                zip_file.write(img_path, arcname=img_name)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name='imagens_selecionadas.zip', mimetype='application/zip')


@app.route('/merge-pdf')
def merge_pdf_page():
    return render_template('merge-pdf.html')

@app.route('/merge-pdf', methods=['POST'])
def merge_pdfs():
    if 'pdfs' not in request.files:
        return "Nenhum arquivo enviado", 400

    arquivos = request.files.getlist('pdfs')
    if len(arquivos) < 2:
        return "Envie pelo menos dois arquivos PDF", 400

    merger = PdfMerger()
    temp_files = []

    for file in arquivos:
        if file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(temp_path)
            merger.append(temp_path)
            temp_files.append(temp_path)

    output_name = 'pdf_unido.pdf'
    temp_output_path = os.path.join(tempfile.gettempdir(), output_name)
    merger.write(temp_output_path)
    merger.close()

    final_output_path = os.path.join(convertidos, output_name)
    os.replace(temp_output_path, final_output_path)

    return render_template("resultado-merge.html", arquivo_convertido=output_name)

@app.route('/separar-pdf')
def separar_pdf_page():
    return render_template('separar-pdf.html')


@app.route('/separar-pdf', methods=['POST'])
def separar_pdf():
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(enviados, filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    base_name = os.path.splitext(filename)[0]
    arquivos_gerados = []

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)

        output_filename = f"{base_name}_pagina_{i+1}.pdf"
        output_path = os.path.join(convertidos, output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        arquivos_gerados.append(output_filename)

    return render_template("resultado-separar.html", arquivos=arquivos_gerados)

@app.route('/girar-pdf')
def girar_pdf_page():
    return render_template('girar-pdf.html')


@app.route('/girar-pdf', methods=['POST'])
def girar_pdf():
    if 'pdf_file' not in request.files:
        return "Nenhum arquivo enviado", 400

    try:
        angulo = int(request.form.get('angulo', 90))
        if angulo not in [90, 180, 270]:
            return "Ângulo inválido", 400
    except ValueError:
        return "Ângulo inválido", 400

    file = request.files['pdf_file']
    filename = secure_filename(file.filename)
    input_path = os.path.join(enviados, filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(angulo)
        writer.add_page(page)

    output_filename = f"girado_{angulo}_{filename}"
    output_path = os.path.join(convertidos, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    return render_template("resultado-girar.html", arquivo_convertido=output_filename)
