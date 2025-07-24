from flask import Flask, request, jsonify, url_for
from pdf2docx import Converter
import os
import uuid
import requests

app = Flask(__name__)

# Folder where converted DOCX files are saved and served from
SAVE_FOLDER = "static"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert_pdf_from_url():
    data = request.get_json()

    if not data or 'file_url' not in data:
        return jsonify({"error": "Missing 'file_url' in request body"}), 400

    file_url = data['file_url']
    try:
        # Download PDF from URL
        response = requests.get(file_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download file"}), 400

        # Save the PDF to a temp file
        pdf_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(SAVE_FOLDER, pdf_filename)

        with open(pdf_path, 'wb') as f:
            f.write(response.content)

        # Convert to DOCX
        docx_filename = pdf_filename.replace('.pdf', '.docx')
        docx_path = os.path.join(SAVE_FOLDER, docx_filename)

        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()

        # Generate a URL to the DOCX file
        file_url = url_for('static', filename=docx_filename, _external=True)

        return jsonify({"message": "Conversion successful", "download_url": file_url})

    except Exception as e:
        return jsonify({"error": f"Conversion failed: {str(e)}"}), 500


# ✅ This line is changed to support Railway or Heroku dynamic ports
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
