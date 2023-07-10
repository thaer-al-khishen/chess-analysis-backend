import re
import os
import subprocess

def execute_pgn_extract_command(file_path, pgn_extract_path='./pgn-extract.exe'):
    command = [pgn_extract_path, '-e', 'eco.pgn', file_path]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    return result.stdout

def get_game_headers(game_lines):
    headers = {}
    for line in game_lines:
        if '[ECO ' in line or '[Opening ' in line or '[Variation ' in line or '[White ' in line or '[Black ' in line or '[Result ' in line:
            key, value = re.search(r'\[(\w+) "(.+)"\]', line).groups()
            headers[key] = value
    return headers

def get_book_moves(headers):
    with open('eco.pgn', 'r') as eco_file:
        eco_lines = eco_file.readlines()
        for j, eco_line in enumerate(eco_lines):
            if f'[ECO "{headers.get("ECO")}"]' in eco_line and f'[Opening "{headers.get("Opening")}"]' in eco_lines[j+1]:
                book_moves_line = eco_lines[j+4]
                headers['BookMoves'] = " ".join(book_moves_line.rstrip("*\n").split())
                break
    return headers

def sanitize_pgn_content(content):
    return re.sub(r'{(.*?)}', r'\1', content)  # Remove only the braces

def add_opening_strategy_headers(pgn_content):
    lines = pgn_content.split('\n')
    new_lines = []

    game_starts = [i for i, line in enumerate(lines) if '[Event ' in line]
    for i in range(len(game_starts)):
        game_lines = lines[game_starts[i]:game_starts[i + 1] if i + 1 < len(game_starts) else len(lines)]
        headers = get_game_headers(game_lines)
        if headers.get('White') != '?' and headers.get('Black') != '?':
            headers = get_book_moves(headers)

        if 'BookMoves' in headers:
            book_moves_header = f'[BookMoves "{headers["BookMoves"]}"]\n'
            # find the position of the last header in the game_lines and insert 'BookMoves' after that
            last_header_index = next((i for i, line in reversed(list(enumerate(game_lines))) if '[' in line), None)
            if last_header_index is not None:
                game_lines.insert(last_header_index + 1, book_moves_header)
                # remove trailing empty line from headers
                if game_lines[last_header_index + 2] == '':
                    game_lines.pop(last_header_index + 2)
                new_lines.extend(game_lines)

    return '\n'.join(new_lines)
