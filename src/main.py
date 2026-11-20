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
window.color = color.rgb(4, 8, 18)
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
              rotation_x=90, scale=2.1, color=color.rgb(215, 190, 140))

random.seed(17)
for _ in range(160):
    Entity(model='quad', scale=.09, color=color.white,
           position=(random.uniform(-55, 55), random.uniform(15, 40),
                     random.uniform(-55, 55)), billboard=True)

app.run()
