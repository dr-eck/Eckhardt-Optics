# Eckhardt Optics Remote Sensing Calculator GUI
# Version 1.6 - June 2024
import math
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import os
from tkinter import messagebox


# --- Window scaling factor ---
SCALE = 1.4

#functions
def calculate():
    try:
        HFOV = float(hfov_var.get())
        Altitude = float(altitude_var.get())
        ImageDiameter = float(imagediameter_var.get())
        Wavelength = float(wavelength_var.get())
        PixelSize = float(pixelsize_var.get())
        
        #calculate swath
        theta_rad = HFOV * (math.pi/180.0)/2 #theta is half the HFOV, convert to radians
        SWATH = 2*Altitude*math.tan(theta_rad) #trig to get swath in meters

        #calculate focal length
        mag = -ImageDiameter/(1000*SWATH)
        s = -Altitude*1000
        sprime = s*mag
        FocalLength = (s*sprime)/(s-sprime)

        #calculate GSD
        GSD = (Altitude * PixelSize) / (10*FocalLength)

        #Calculate F/# and entrance pupil diameter
        Fnumber = PixelSize/(1.22*Wavelength) #assume Airy disk radius equal to pixel size to determine required F/# (Ra = 1.22 * lambda * F#)
        EntrancePupilDiameter = FocalLength/Fnumber #mm

        swath_var.set(f"{SWATH:.2f}")
        focal_var.set(f"{FocalLength:.2f}")
        gsd_var.set(f"{GSD:.2f}")
        fnum_var.set(f"{Fnumber:.2f}")
        epd_var.set(f"{EntrancePupilDiameter:.2f}")
    except Exception:
        swath_var.set("")
        focal_var.set("")
        gsd_var.set("")
        fnum_var.set("")
        epd_var.set("")

# --- HFOV validation: only allow 0-180 ---
def validate_hfov(new_value):
    try:
        if new_value == '':
            return True
        val = float(new_value)
        return 0 <= val <= 180
    except ValueError:
        return False

def scale(val):
    return int(val * SCALE)

root = tk.Tk()
root.title("Eckhardt Optics - Remote Sensing Calculator")
root.geometry(f'{scale(900)}x{scale(480)}')


# Set window icon to favsample.png (must be a valid PNG file in the same directory)
icon_path = os.path.join(os.path.dirname(__file__), "eofav01.png")
if os.path.exists(icon_path):
    try:
        icon_photo = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon_photo)
    except Exception as e:
        #messagebox.showwarning("Icon Error", f"Could not load window icon: {e}")
        print(f"Could not load window icon: {e}")
else:
    #messagebox.showwarning("Icon Missing", "favsample.png not found in script directory. Window icon not set.")
    print("Window icon not found in script directory. Window icon not set.")

# --- Drawing function ---
def draw_diagram():
    drawing_canvas.delete("all")
    # Get values, use defaults if blank
    try:
        HFOV = float(hfov_var.get())
        Altitude = float(altitude_var.get())
        FocalLength = float(focal_var.get())
    except Exception:
        HFOV = 60.0
        Altitude = 120
        FocalLength = 31.08

    # Geometry
    theta_rad = HFOV * (math.pi/180.0)/2
    H = Altitude
    swath = 2*H*math.tan(theta_rad)

    # Canvas coordinates
    margin = scale(40)
    top_y = margin
    bottom_y = canvas_height - margin
    center_x = canvas_width//2

    # --- Draw drone image instead of sensor rectangle and lens ---
    # Load and display Drone-InfoG.png centered at the top
    global drone_img_tk
    drone_img_path = os.path.join(os.path.dirname(__file__), "Drone-InfoG-1.png")
    try:
        drone_img_tk = tk.PhotoImage(file=drone_img_path)
        img_h = drone_img_tk.height()
        # Center horizontally, place at top_y
        drawing_canvas.create_image(center_x, top_y + 15 + img_h//2, image=drone_img_tk)
    except Exception as e:
        drawing_canvas.create_text(center_x, top_y+30, text="[Drone image not found]", fill="red")

    # Label Camera Sensor Horizontal Dimension
    #drawing_canvas.create_text(center_x-80, top_y+60, text=f"Horizontal Camera Sensor\n Dimension = {ImageDiameter:.1f}mm", anchor="e", font=("Segoe UI",scale(8),"bold"), fill="blue")

    # Label Lens Focal Length
    drawing_canvas.create_text(center_x+60, top_y+70, text=f"Focal Length = {FocalLength:.1f}mm", anchor="w", font=("Segoe UI",scale(8),"bold"), fill="blue")

    # Draw HFOV arc (below drone)
    lens_y = top_y + 80
    arc_radius = scale(60)
    drawing_canvas.create_arc(center_x-arc_radius, lens_y-arc_radius, center_x+arc_radius, lens_y+arc_radius,
                             start=270-math.degrees(theta_rad), extent=2*math.degrees(theta_rad), style="arc", outline="black", width=2)
    drawing_canvas.create_text(center_x+scale(5), lens_y+arc_radius+scale(6), text=f"HFOV = {HFOV:.1f}°", anchor="w", font=("Segoe UI",scale(8),"bold"), fill="blue")


    # Draw rays at the edge of the HFOV arc, always at correct angle
    ground_y = bottom_y
    ray_length = ground_y - lens_y
    # For HFOV=180, rays should be horizontal
    left_x = center_x - ray_length * math.tan(theta_rad)
    right_x = center_x + ray_length * math.tan(theta_rad)

    # Calculate where the swath would be on the canvas
    swath_canvas = right_x - left_x
    max_swath_canvas = canvas_width - 2*margin
    swath_too_wide = swath_canvas > max_swath_canvas
    # If swath fits, ground line matches rays; if not, ground line is max width and rays are detached
    if not swath_too_wide:
        # Draw rays to ground
        drawing_canvas.create_line(center_x, lens_y, left_x, ground_y, fill="blue", dash=(2,2), width=scale(1))
        drawing_canvas.create_line(center_x, lens_y, right_x, ground_y, fill="blue", dash=(2,2), width=scale(1))
    else:
        # Draw rays, but stop them short of the ground line
        ray_short = ray_length * 0.85
        left_ray_x = center_x - ray_short * math.tan(theta_rad)
        right_ray_x = center_x + ray_short * math.tan(theta_rad)
        ray_y = lens_y + ray_short
        drawing_canvas.create_line(center_x, lens_y, left_ray_x, ray_y, fill="blue", dash=(2,2), width=scale(1))
        drawing_canvas.create_line(center_x, lens_y, right_ray_x, ray_y, fill="blue", dash=(2,2), width=scale(1))

    # Draw altitude label
    drawing_canvas.create_line(center_x, lens_y, center_x, ground_y, arrow=tk.LAST, width=scale(1))
    drawing_canvas.create_text(center_x+scale(5), (lens_y+ground_y)//2, text=f"Altitude = {Altitude:.0f} meters", anchor="w", font=("Segoe UI",scale(8),"bold"), fill="blue")


    # Draw ground and swath
    drawing_canvas.create_line(left_x, ground_y, right_x, ground_y, width=scale(2))
    #drawing_canvas.create_text(center_x, ground_y+scale(12), text="GROUND", font=("Segoe UI",scale(7)))
    drawing_canvas.create_line(left_x, ground_y+scale(5), right_x, ground_y+scale(5), arrow=tk.BOTH, width=scale(1))
    #drawing_canvas.create_text(center_x, ground_y+scale(18), text="SWATH", font=("Segoe UI",scale(7)))

    # Display SWATH value on the drawing
    drawing_canvas.create_text(center_x, ground_y+scale(15), text=f"SWATH = {swath:.1f} meters", font=("Segoe UI",scale(8),"bold"), fill="blue")

     
# Bind Enter key to calculate and draw diagram
def on_enter(event):
    calculate()
    draw_diagram()  
# Bind Enter key to calculate and draw diagram
root.bind('<Return>', on_enter)


# Input variables
hfov_var = tk.DoubleVar(value="60.0")
altitude_var = tk.DoubleVar(value="120")
imagediameter_var = tk.DoubleVar(value="35.9")
wavelength_var = tk.DoubleVar(value="0.54")
pixelsize_var = tk.DoubleVar(value="4.4")

# Output variables (read-only)
swath_var = tk.DoubleVar()
focal_var = tk.DoubleVar()
gsd_var = tk.DoubleVar()
fnum_var = tk.DoubleVar()
epd_var = tk.DoubleVar()

# Layout: left = input/output, right = drawing
mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

# Add a blank row above the input fields and drawing for vertical space
mainframe.grid_rowconfigure(0, minsize=scale(50))

input_frame = ttk.Frame(mainframe)
input_frame.grid(row=1, column=0, sticky="NW")

# Increase canvas width for better wide HFOV visualization
canvas_width = scale(500)
canvas_height = scale(350)
drawing_canvas = tk.Canvas(mainframe, width=canvas_width, height=canvas_height, bg="white")
drawing_canvas.grid(row=1, column=1, rowspan=20, padx=(scale(20),0), sticky="NE")

# Input fields (scaled fonts and entry widths)
label_font = ("Segoe UI", scale(10))
entry_font = ("Lucida Console", scale(10))

#change button font
s = ttk.Style()
s.configure('BtnFont.TButton', font=('Helvetica', scale(10)))


vcmd = (root.register(validate_hfov), '%P')
ttk.Label(input_frame, text="HFOV (deg):", font=label_font).grid(row=0, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=hfov_var, width=scale(10), font=entry_font, justify="center", validate='key', validatecommand=vcmd).grid(row=0, column=1)

ttk.Label(input_frame, text="Altitude (m):", font=label_font).grid(row=1, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=altitude_var, width=scale(10),font=entry_font, justify="center").grid(row=1, column=1)

ttk.Label(input_frame, text="Image Diameter (mm):", font=label_font).grid(row=2, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=imagediameter_var, width=scale(10),font=entry_font, justify="center").grid(row=2, column=1)

ttk.Label(input_frame, text="Wavelength (μm):", font=label_font).grid(row=3, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=wavelength_var, width=scale(10),font=entry_font, justify="center").grid(row=3, column=1)

ttk.Label(input_frame, text="Pixel Size (μm):", font=label_font).grid(row=4, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=pixelsize_var, width=scale(10),font=entry_font, justify="center").grid(row=4, column=1)

ttk.Button(input_frame, text="Calculate", style = 'BtnFont.TButton', command=lambda: [calculate(), draw_diagram()]).grid(row=5, column=1, columnspan=1, pady=scale(10))

# Output fields (read-only, scaled fonts and entry widths)
# Title for calculated section
title_font = ("Segoe UI", scale(9), "bold")
ttk.Label(input_frame, text="Calculated Swath, Focal Length and Ground Sampling Distance", font=title_font).grid(row=6, column=0, columnspan=2, pady=(scale(10),scale(2)), sticky="WENS")
canvas1 = tk.Canvas(input_frame, width=scale(220), height=scale(2), highlightthickness=0)
canvas1.grid(row=7, column=0, columnspan=2, sticky="WENS")

ttk.Label(input_frame, text="Swath (m):", font=label_font).grid(row=8, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=swath_var, width=scale(10),font=entry_font, justify="center", state="readonly", foreground="blue").grid(row=8, column=1)

ttk.Label(input_frame, text="Focal Length (mm):", font=label_font).grid(row=9, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=focal_var, width=scale(10),font=entry_font, justify="center", state="readonly", foreground="blue").grid(row=9, column=1)

ttk.Label(input_frame, text="GSD (cm):", font=label_font).grid(row=10, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=gsd_var, width=scale(10),font=entry_font, justify="center", state="readonly", foreground="blue").grid(row=10, column=1)

# Title for required aperture section
ttk.Label(input_frame, text="Required Aperture Based on Airy Disk Radius = Pixel Size", font=title_font).grid(row=11, column=0, columnspan=2, pady=(scale(10),scale(2)), sticky="WENS")
canvas2 = tk.Canvas(input_frame, width=scale(220), height=scale(2), highlightthickness=0)
canvas2.grid(row=12, column=0, columnspan=2, sticky="WENS")

ttk.Label(input_frame, text="F/#:", font=label_font).grid(row=13, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=fnum_var, width=scale(10),font=entry_font, justify="center", state="readonly", foreground="blue").grid(row=13, column=1)

ttk.Label(input_frame, text="Entrance Pupil Diameter (mm):", font=label_font).grid(row=14, column=0, sticky="E")
ttk.Entry(input_frame, textvariable=epd_var, width=scale(10),font=entry_font, justify="center", state="readonly", foreground="blue").grid(row=14, column=1)

#make label link to Eckhardt Optics GSD page
def open_gsd_page(event):
    import webbrowser
    webbrowser.open_new("https://www.eckop.com/home/applications/remote-sensing/ground-sampling-distance-and-spatial-resolution-of-remote-sensing-systems/")

#link_label = ttk.Label(mainframe, text="Visit our GSD and Spatial Resolution of Remote Sensing Systems page for more information.", font=label_font, foreground="blue", cursor="hand2")
link_label = ttk.Label(mainframe, text="www.eckop.com", font=label_font, foreground="#718BB9", cursor="hand2")
link_label.grid(row=21, column=0, columnspan=2, sticky="E")
link_label.bind("<Button-1>", open_gsd_page)

# Initial draw
draw_diagram()

root.mainloop()
