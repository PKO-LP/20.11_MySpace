# БЛОК 1: окно и пути
from panda3d.core import loadPrcFileData
loadPrcFileData("", "audio-library-name null")
from ursina import *
from pathlib import Path
import math
import random
from planet_data import PLANETS, FACTS
from storage import load_notes, save_notes
from motion import orbit_position, next_angle, zoom_distance

BASE = Path(__file__).resolve().parent.parent
app = Ursina(title='MySpace', size=(1280, 720),
             borderless=False, fullscreen=False, development_mode=False)
window.color = color.rgb32(4, 8, 18)
application.asset_folder = BASE / 'assets'
Text.default_font = 'OpenSans-Regular.ttf'
camera.position = (0, 40, -55)
camera.look_at(Vec3(0, 0, 0))


# БЛОК 2: Солнце и планеты
def texture_for(name):
    path = BASE / 'assets' / 'textures' / f'{name}.png'
    return load_texture(path.name, folder=path.parent) if path.exists() else 'white_cube'


sun = Entity(model='sphere', scale=2.4,
             texture=texture_for('sun'), color=color.orange)
planet_entities = []
for i, row in enumerate(PLANETS):
    key, name, radius, size, speed, diameter, distance, period = row
    body = Entity(model='sphere', scale=size,
                  texture=texture_for(key), collider='sphere')
    body.planet_index = i
    body.orbit_angle = i * 42
    body.position = orbit_position(radius, body.orbit_angle)
    planet_entities.append(body)
    vertices = [orbit_position(radius, n * 3) for n in range(121)]
    Entity(model=Mesh(vertices=vertices, mode='line', thickness=1),
           color=color.rgba(90, 120, 155, 90))
ring = Entity(parent=planet_entities[5], model=Circle(64, mode='line'),
              rotation_x=90, scale=2.1, color=color.rgb32(215, 190, 140))

random.seed(17)
for _ in range(160):
    Entity(model='quad', scale=.09, color=color.white,
           position=(random.uniform(-55, 55), random.uniform(15, 40),
                     random.uniform(-55, 55)), billboard=True)


# БЛОК 3: камера, данные и интерфейс
rig = Entity()
camera.parent = rig
camera.fov = 60
camera_distance = 55
selected = None
paused = False
multiplier = 1
notes_path = BASE / 'data' / 'notes.txt'
load_error = ''
try:
    notes = load_notes(notes_path)
except (OSError, UnicodeError):
    notes = {}
    load_error = 'Файл заметок не прочитан. Проверьте data/notes.txt.'

Text('MYSPACE', position=(-.86, .47), scale=1.4)
Text('Размеры, расстояния и скорости условные',
     position=(-.86, -.46), scale=.8)
status = Text(load_error or 'Выберите планету',
              position=(-.86, -.40), scale=.85)
panel = Entity(parent=camera.ui, enabled=False, position=(.53, .06))
Entity(parent=panel, model='quad', scale=(.57, .70),
       color=color.rgb32(16, 28, 45), z=.1, collider='box')
portrait = Entity(parent=panel, model='quad', scale=(.18, .12),
                  position=(0, .25))
card = Text(parent=panel, position=(-.25, .16), scale=.85)
note_field = InputField(parent=panel, position=(0, -.18),
                        scale=(.50, .045), character_limit=160)
Text('Моя заметка (до 160 знаков):', parent=panel,
     position=(-.25, -.12), scale=.75)


# БЛОК 4: действия пользователя
def focus(index):
    global selected, camera_distance
    if selected is not None:
        planet_entities[selected].color = color.white
    selected = index
    body = planet_entities[index]
    body.color = color.rgb32(255, 240, 175)
    key, name, radius, size, speed, diameter, distance, period = PLANETS[index]
    portrait.texture = texture_for(key)
    card.text = (f'{name}\nНомер: {index + 1}\nДиаметр: {diameter} км\n'
                 f'От Солнца: {distance} млн км\nПериод: {period}\n\n'
                 + FACTS[index])
    card.wordwrap = 32
    note_field.text = notes.get(key, '')
    note_field.active = False
    panel.enabled = True
    camera_distance = size * 7 + 3
    status.text = 'Выбрана планета: ' + name


def overview():
    global selected, camera_distance
    if selected is not None:
        planet_entities[selected].color = color.white
    selected = None
    panel.enabled = False
    note_field.active = False
    camera_distance = 55
    rig.position = (0, 0, 0)
    rig.rotation = (0, 0, 0)
    status.text = 'Общий вид'


def save_current():
    if selected is None:
        return
    key = PLANETS[selected][0]
    updated = dict(notes)
    updated[key] = note_field.text
    try:
        save_notes(notes_path, updated)
    except (OSError, UnicodeError, ValueError):
        status.text = 'Не сохранено: проверьте доступ к файлу.'
    else:
        notes.clear()
        notes.update(updated)
        status.text = 'Заметка сохранена в data/notes.txt'


def set_speed(value):
    global multiplier
    multiplier = value
    speed_label.text = f'Скорость: x{value}'


def toggle_pause():
    global paused
    paused = not paused
    pause_button.text = 'Продолжить' if paused else 'Пауза'


# БЛОК 5: кнопки
for i, row in enumerate(PLANETS):
    Button(text=row[1], scale=(.21, .042), position=(-.74, .36 - i * .06),
           on_click=Func(focus, i), color=color.rgb32(28, 51, 76))
Button(text='Сохранить', parent=panel, position=(0, -.27),
       scale=(.25, .045), on_click=save_current)
Button(text='Общий вид [R]', scale=(.23, .045),
       position=(-.72, -.20), on_click=overview)
pause_button = Button(text='Пауза', scale=(.19, .045),
                      position=(-.72, -.29), on_click=toggle_pause)
speed_label = Text('Скорость: x1', position=(-.48, -.29), scale=.85)
for i, value in enumerate((.5, 1, 5, 10)):
    Button(text=str(value), scale=(.075, .04),
           position=(-.22 + i * .09, -.30), on_click=Func(set_speed, value))
for i, body in enumerate(planet_entities):
    body.on_click = Func(focus, i)


# БЛОК 6: управление и движение
def input(key):
    global camera_distance
    if key == 'escape':
        application.quit()
    if note_field.active:
        return
    if key == 'space':
        toggle_pause()
    elif key == 'r':
        overview()
    ui_hovered = mouse.hovered_entity and mouse.hovered_entity.has_ancestor(camera.ui)
    if key in ('scroll up', 'scroll down') and not ui_hovered:
        minimum = PLANETS[selected][3] * 2 + 1 if selected is not None else 10
        direction = 1 if key == 'scroll up' else -1
        camera_distance = zoom_distance(camera_distance, direction, minimum, 65)


def update():
    for row, body in zip(PLANETS, planet_entities):
        body.orbit_angle = next_angle(body.orbit_angle, row[4], time.dt,
                                      multiplier, paused)
        body.position = orbit_position(row[2], body.orbit_angle)
        if not paused:
            body.rotation_y += 15 * time.dt * multiplier
    target = planet_entities[selected].position if selected is not None else Vec3(0, 0, 0)
    rig.position = lerp(rig.position, target, min(1, time.dt * 8))
    ui_hovered = mouse.hovered_entity and mouse.hovered_entity.has_ancestor(camera.ui)
    if held_keys['right mouse'] and not ui_hovered and not note_field.active:
        rig.rotation_y += mouse.velocity[0] * 120
    desired = Vec3(0, camera_distance * .72, -camera_distance)
    camera.position = lerp(camera.position, desired, min(1, time.dt * 8))
    camera.look_at(rig)


app.run()
