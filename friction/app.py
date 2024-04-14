from shiny.express import input, render, ui
from shiny import reactive
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

plot_width: float = 100.0
plot_height: float = 100.0
box_width: float = 30.0
box_height: float = 30.0
box_color: str = 'white'
box_edge_sliding_color: str = 'red'
box_edge_stationary_color: str = 'green'
anchor_x: float = plot_width / 2 - box_width / 2
original_x: float = anchor_x
slope_x = np.array([0,100])
angle: float = 19
mass: float = 100
mu: float = 0.168
g: float = 9.8

ui.page_opts(title="Reaction force, normal force and friction",) # fillable=True)

def rad(angle: float) -> float:
    return angle / 180 * np.pi

with ui.sidebar():
    ui.input_text("angle", "Slope Angle:", str(angle))
    ui.input_slider("angle_slider", "", min=0, max=60, value=angle, step=0.001)
    ui.input_text("mass", "Mass / kg", str(mass))
    ui.input_text("mu", "Coefficient Of Friction", str(mu))
    ui.input_slider("mu_slider", "", min=0, max=1, value=mu, step=0.001)
    ui.input_slider("time", "Animate", min=0, max=100,value=0, step=2, animate=True)

@reactive.effect
def store_angle() -> None:
    try:
        global angle
        angle = float(input.angle())
    except:
        f'error: setting angle = {angle}; input.angle() = {input.angle()}'
        ui.update_text("angle", value=str(0))

@reactive.effect
def store_mu() -> None:
    try:
        global mu
        mu = float(input.mu())
    except:
        f'error: setting mu = {mu}; input.mu() = {input.mu()}'
        ui.update_text("mu", value=str(0))

@reactive.effect
def store_mass() -> None:
    try:
        global mass
        mu = float(input.mass())
    except:
        f'error: setting mass = {mass}; input.mass() = {input.mass()}'
        ui.update_text("mass", value=str(100))

def calc_y(x: float) -> None:
    if  angle < 60:
        return np.tan(rad(angle)) * x

def create_rectangle(anchor_x: float, _anchor_y: float, width: float, height: float, angle: float) -> matplotlib.patches.Rectangle:
    edge_color = box_edge_sliding_color if is_sliding() else box_edge_stationary_color
    return Rectangle((anchor_x, _anchor_y), width, height, angle=angle, lw=5, facecolor = box_color, edgecolor = edge_color)

def is_sliding() -> bool:
    try:
        crit_angle = np.arccos(np.sqrt(1/(1+float(input.mu())**2))) / np.pi * 180
        print(f'critical angle is: {crit_angle}')
        if float(input.angle()) > crit_angle:
            return True
        else:
            return False
    except:
        print(f'error: coefficient of friction was {input.mu()}; input angle was {input.angle()}')

@reactive.effect
def update_angle() -> None:
    ui.update_text("angle", value=str(input.angle_slider()))

@reactive.effect
def update_angle_slider() -> None:
    ui.update_slider("angle_slider", value=str(input.angle()))

@reactive.effect
def update_angle() -> None:
    ui.update_text("mu", value=str(input.mu_slider()))

@reactive.effect
def update_angle_slider() -> None:
    ui.update_slider("mu_slider", value=str(input.mu()))

@reactive.effect
@reactive.event(input.angle, input.mu, input.mass)
def calc_forces() -> None:
    global W_slope
    global f
    
    try:
        m: float = mass
        W: float = m * g
        t: np.array = np.linspace(0, 5, 100)
        
        W_slope = W * np.sin(rad(angle))
        f = mu * W * np.cos(rad(angle)) if angle > 0 else 0
        
    except:
        print(f'error: angle: {input.angle()}, m: {input.mass()}')

@reactive.effect
@reactive.event(input.time)
def calc_motion() -> None:
    global anchor_x
    
    try:
        t: float = float(input.time())
        downhill_force: float = W_slope - f
        print(downhill_force)
        a_slope: float = (W_slope - f) / mass

        #displacement
        d_slope = -0.5 * a_slope * t**2
        if downhill_force > 0 and original_x + d_slope * np.cos(rad(angle)) > 0:
            anchor_x = original_x + d_slope * np.cos(rad(angle))
        else:
            anchor_x = original_x
            ui.update_slider("time",value=str(0))
    except:
        ...

@render.plot
@reactive.event(input.angle, input.mu, input.mass, input.time)
def plot() -> None:
    fig, ax = plt.subplots(figsize=(10,12))
    try:
        ax.plot(slope_x, calc_y(slope_x), lw=40, zorder=0)
    except:
        print(f'error: slope_x = {slope_x}, y = {calc_y(x)}')

    x: float = anchor_x
    y: float = calc_y(x)

    rect = create_rectangle(x, y, box_width, box_height, angle=angle) # angle in degrees
    rect_bottom_centre_x = rect.get_x() + box_width/2 * np.cos(rad(angle))
    rect_bottom_centre_y = calc_y(rect_bottom_centre_x)
    ax.add_patch(rect)

    w: float = mass * g
    dy_std = 30
    
    ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=0, dy=-dy_std, shape='full', lw=2, head_width=plot_width/50)
    ax.text(rect_bottom_centre_x + 2, rect_bottom_centre_y - 0.5 * dy_std, f'{str(round(w, 1))} N', fontdict={'size':12})
    ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=-dy_std*np.sin(rad(angle)), dy=dy_std*np.cos(rad(angle)), shape='full', lw=2, head_width=plot_width/50)
    ax.text(rect_bottom_centre_x - dy_std*np.sin(rad(angle)) - 8, rect_bottom_centre_y + dy_std*np.cos(rad(angle)) + 8, f'{str(round(w*np.cos(rad(angle)), 1))} N', fontdict={'size':12})
    if W_slope:
        ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=-W_slope/w*dy_std * np.cos(rad(angle)), dy=-W_slope/w*dy_std * np.sin(rad(angle)), shape='full', lw=2, head_width=plot_width/50)
        ax.text(rect_bottom_centre_x - W_slope/w*dy_std * np.cos(rad(angle)) - 8, rect_bottom_centre_y - W_slope/w*dy_std * np.sin(rad(angle)) - 2, f'{str(round(W_slope,1))} N', ha='right', fontdict={'size':12})
    if f:
        ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=f/w*dy_std * np.cos(rad(angle)), dy=f/w*dy_std * np.sin(rad(angle)), shape='full', lw=2, head_width=plot_width/50)
        ax.text(rect_bottom_centre_x + f/w*dy_std * np.cos(rad(angle)) + 8, rect_bottom_centre_y + f/w*dy_std * np.sin(rad(angle)) + 2, f'{str(round(f,1))} N', ha='left', fontdict={'size':12})        
    
    ax.set_xlim(0,plot_width)
    ax.set_ylim(-40,plot_height)
    ax.set_aspect('equal')
    ax.axis('off')

    return fig


@render.text
def notes1():
    return f"We are interested in whether the block will slide down the slope here.  The forces along the sloping surface is what we would like to work out."


@render.text
def notes2():
    return f"Suppose y is direction perpendicularly upward from the sloping surface.  Since the object sliding down the slope could neither lift off from the sloping service nor sink into the sloping surface, the net force in the y direction has to be zero.  (Recall Newton's law of inertia)"

@render.text
def notes3():
    return f"This is the key point to starting point of the calculations.  Given the weight of the object and the angle of the slope, one can work out the y component of the block's weight, which is in equal magnitude but in opposite direciton to the Normal force that is required for the calculation of friction.  Consequently, we can calculate the friction, using a known or measured coefficient of friction and the normal force, where friction = 'coefficient of friction x normal force.  Note that the direction of friction must be pointing up-slope against the downward pull as a result of the block's weight."

@render.text
def notes4():
    return f"What is left is just working out the down-slope force as a result of the block's weight.  This is the x component of the block's weight that is perpendicular to the y component, pointing in the down-slope direction."

@render.text
def notes5():
    return f"What is left is just working out the down-slope force as a result of the block's weight.  This is the x component of the block's weight that is perpendicular to the y component, pointing in the down-slope direction.  The block will remain stationary if friction is greater than or equal to the down-slope force."

@render.text
def notes6():
    return f"Weighing and measuring the coefficient of friction on a flat surface and then make prediction is far more convenient than to measure the forces along a slope.  And safer! Imagine dragging 10 tonne object up and down a hill!"

