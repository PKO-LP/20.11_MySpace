from pathlib import Path


def load_notes(path):
    path = Path(path)
    if not path.exists():
        return {}
    notes = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '|' in line:
            key, text = line.split('|', 1)
            if key:
                notes[key] = text
    return notes


def save_notes(path, notes):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for key, text in sorted(notes.items()):
        if '|' in key or '\n' in key or '\r' in key:
            raise ValueError('Неверный идентификатор планеты')
        text = text.replace('\n', ' ').replace('\r', ' ')
        rows.append(f'{key}|{text}')
    temporary = path.with_suffix('.tmp')
    temporary.write_text('\n'.join(rows), encoding='utf-8')
    temporary.replace(path)
