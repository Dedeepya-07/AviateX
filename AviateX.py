from ursina import *
from random import uniform
import serial
import threading
import json

# === App Setup ===
app = Ursina()
window.color = color.rgb(135, 206, 250)  # Light blue sky
camera.fov = 60

# === Serial Setup ===
ser = serial.Serial('COM4', 19200, timeout=1)
accel_x = 0
accel_y = 0
game_over = False

# === Serial Reading Thread ===
def read_serial():
    global accel_x, accel_y
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                data = json.loads(line)
                accel_x = -data['x']  # Reverse direction
                accel_y = data['y']
        except:
            continue

threading.Thread(target=read_serial, daemon=True).start()

# === Sky ===
Sky()

# === Ground (Temporary) ===
ground = Entity(model='plane', scale=(500,1,500), texture='white_cube',
                texture_scale=(50,50), color=color.green, y=-2)
destroy(ground, delay=4)

# === Plane ===
plane_body = Entity(model='cube', color=color.red, scale=(1, 0.3, 2), position=(0,0,0))
left_wing = Entity(parent=plane_body, model='cube', scale=(0.2, 0.05, 1.5), position=(-0.6,0,0), color=color.gray)
right_wing = Entity(parent=plane_body, model='cube', scale=(0.2, 0.05, 1.5), position=(0.6,0,0), color=color.gray)
tail = Entity(parent=plane_body, model='cube', scale=(0.2, 0.5, 0.05), position=(0,0.25,-0.9), color=color.gray)

# === Bird Creation ===
def create_bird():
    bird = Entity(model='sphere', color=color.black, scale=(0.5, 0.4, 0.6))
    Entity(parent=bird, model='cube', scale=(0.1,0.02,0.6), position=(-0.35,0.05,0), rotation=(0,0,20), color=color.black)
    Entity(parent=bird, model='cube', scale=(0.1,0.02,0.6), position=(0.35,0.05,0), rotation=(0,0,-20), color=color.black)
    Entity(parent=bird, model='cube', scale=(0.1,0.15,0.05), position=(0,-0.1,-0.3), color=color.black)
    return bird

# === Obstacle Spawning ===
birds = []

def spawn_bird():
    if game_over: return
    bird = create_bird()
    bird.position = (
        plane_body.x + uniform(-4, 4),
        plane_body.y + uniform(-1, 2),
        plane_body.z + 60
    )
    birds.append(bird)
    invoke(spawn_bird, delay=0.7)

spawn_bird()

# === Score UI ===
score = 0
score_text = Text(text="Score: 0", position=(-0.75, 0.42), scale=1.2, background=True, color=color.black)

# === Game Over UI ===
game_over_text = Text(text="GAME OVER", enabled=False, scale=2, origin=(0,0), position=(0,0), color=color.red)

# === Update Loop ===
def update():
    global accel_x, accel_y, score, game_over

    if game_over:
        return

    # Smooth movement
    move_x = accel_x * 3
    move_y = accel_y * 3

    # Update position
    plane_body.x = lerp(plane_body.x, clamp(plane_body.x + move_x * time.dt * 10, -8, 8), 8 * time.dt)
    plane_body.y = lerp(plane_body.y, clamp(plane_body.y + move_y * time.dt * 10, -2, 8), 6 * time.dt)
    plane_body.z += 6 * time.dt

    # Tilt
    plane_body.rotation_z = lerp(plane_body.rotation_z, -move_x * 25, 6 * time.dt)
    plane_body.rotation_x = lerp(plane_body.rotation_x, move_y * 10, 4 * time.dt)

    # Camera follow
    camera.position = (plane_body.x, plane_body.y + 8, plane_body.z - 30)

    # Bird movement and collision
    for bird in birds[:]:
        bird.z -= 6 * time.dt
        if bird.z < plane_body.z - 10:
            bird.disable()
            birds.remove(bird)
            score += 1
            score_text.text = f"Score: {score}"
        elif distance(bird.position, plane_body.position) < 1:
            game_over = True
            game_over_text.enabled = True

app.run()
