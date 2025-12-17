from ursina import *
import random

app = Ursina()
camera.orthographic = True
camera.fov = 4
speed = 4

# ---- Startbildschirm ----
titletext = Text(text='🎅 Santa Run 🎄', origin=(0,0), scale=3, y=0.3, color=color.azure)
yestext = Text(text='Drücke "Ja", um zu starten', origin=(0,0), y=0.1, scale=1.5)
nowtext = Text(text='Drücke "Nein", um zu beenden', origin=(0,0), y=-0.05, scale=1.5)

yesbutton = Button(text='Ja', color=color.green, scale=(0.2,0.1), y=-0.15)
nobutton = Button(text='Nein', color=color.red, scale=(0.2,0.1), y=-0.3)

# ---- Hintergrund & Spieler ----
background = [Entity(model='quad', texture='img/background.png', scale=(16,4), x=16*i, z=1) for i in range(2)]
santa = Animation('img/santa/santa', scale=1, y=-1, x=-2, z=-1, collider='box')
grinch = Animation('img/grinch/grinch', scale=1, y=-1, x=-3, z=-2)

# ---- Physik ----
gravity = -5
jump_power = 3.5
velocity_y = 0

# ---- Geschenke ----
gift_templates = [
    Entity(model='quad', texture='img/obstacles/A.png', collider='box', y=-1, z=-1, scale=1, enabled=False),
    Entity(model='quad', texture='img/obstacles/B.png', collider='box', y=-1, z=-1, scale=1, enabled=False)
]
gifts = []
spawn_delay = 2.0
game_over = False
spawn_index = 0

# ---- Game Over ----
game_over_text = Text('Game Over', origin=(0,0), scale=3, color=color.red, enabled=False)
retry_button = Button(
    text='Neuer Versuch',
    parent=camera.ui,
    origin=(0,0),
    scale=(0.2,0.1),
    y=-0.1,
    color=color.green,
    enabled=False
)
quit_button = Button(
    text='Beenden',
    parent=camera.ui,
    origin=(0,0),
    scale=(0.2,0.1),
    y=-0.25,
    color=color.red,
    enabled=False
)

# ---- Funktionen ----
def start_game():
    """Spiel starten: Startbildschirm ausblenden und pausierung aufheben"""
    titletext.enabled = False
    yestext.enabled = False
    nowtext.enabled = False
    yesbutton.enabled = False
    nobutton.enabled = False
    application.paused = False  # Spiel pausierung aufheben
    reset_game()

def quit_game():
    application.quit()

def reset_game():
    global gifts, spawn_delay, velocity_y, game_over, spawn_index
    for g in gifts:
        destroy(g)
    gifts.clear()
    santa.position = Vec3(-2, -1, -1)
    spawn_delay = 2.0
    velocity_y = 0
    game_over = False
    spawn_index = 0
    game_over_text.enabled = False
    retry_button.enabled = False
    quit_button.enabled = False
    application.paused = False  # Pausierung aufheben

def create_gift():
    global spawn_index
    new_x = 9 + random.uniform(0,3)
    template = gift_templates[spawn_index]
    new_gift = duplicate(template, x=new_x, enabled=True)
    gifts.append(new_gift)
    spawn_index = (spawn_index + 1) % len(gift_templates)

def update():
    global velocity_y, game_over
    if game_over or application.paused:
        return

    # Hintergrund scrollen
    for b in background:
        b.x -= time.dt * speed
        if b.x <= -16:
            b.x += 32

    # Santa Bewegung
    santa.y += velocity_y * time.dt
    velocity_y += gravity * time.dt

    if santa.y > 1.5:
        santa.y = 1.5
        if velocity_y > 0:
            velocity_y = 0

    if santa.y <= -1:
        santa.y = -1
        velocity_y = 0

    # Geschenke Bewegung & Kollision
    for g in gifts[:]:
        g.x -= time.dt * speed
        if g.intersects(santa).hit:
            trigger_game_over()
        if g.x < -10:
            gifts.remove(g)
            destroy(g)

def input(key):
    global velocity_y
    if key == 'space' and not game_over and not application.paused:
        velocity_y = jump_power

def trigger_game_over():
    global game_over
    game_over = True
    game_over_text.enabled = True
    retry_button.enabled = True
    quit_button.enabled = True
    application.paused = True

# ---- Button-Callbacks ----
yesbutton.on_click = start_game
nobutton.on_click = quit_game
retry_button.on_click = Func(reset_game)
quit_button.on_click = Func(quit_game)

def spawn_loop():
    global spawn_delay
    if not game_over:
        create_gift()
        spawn_delay = max(0.5, spawn_delay - 0.1)
        invoke(spawn_loop, delay=spawn_delay)

# Spiel pausieren, bis „Ja“ gedrückt wird
application.paused = True

spawn_loop()
app.run()
