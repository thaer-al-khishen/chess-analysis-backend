from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from werkzeug.datastructures import Headers
import tempfile
import io
import pgn_utils

app = Flask(__name__)

def send_as_file(filename, content):
    bytes_io = io.BytesIO(content.encode())
    bytes_io.seek(0)
    headers = Headers()
    headers.add('Content-Disposition', 'attachment', filename='updated_' + filename)
    return send_file(bytes_io, mimetype='text/plain', as_attachment=True, download_name="custom_name.txt")

@app.route('/upload_pgn', methods=['POST'])
def take_single_game_from_pgn_return_headers_moves():
    if 'pgnFile' not in request.files:
        return "No pgnFile key in request.files"

    file = request.files['pgnFile']

    if file.filename == '':
        return 'No selected file'

    if file:
        filename = secure_filename(file.filename)

        # Save the file to a temporary location
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        temp_file.close()

        # Preprocess the file to remove comments in braces
        with open(temp_file.name, 'r') as pgn_file:
            content = pgn_file.read()
        content = pgn_utils.sanitize_pgn_content(content)

        # Save the preprocessed pgn to a temporary file
        with open(temp_file.name, 'w') as pgn_file:
            pgn_file.write(content)

        pgn_content = pgn_utils.execute_pgn_extract_command(temp_file.name)
        updated_pgn_content = pgn_utils.add_opening_strategy_headers(pgn_content)

        print(updated_pgn_content)

        return send_as_file(filename, updated_pgn_content)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
