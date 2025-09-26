# Eckhardt Optics Remote Sensing Calculator GUI
# Version 1.1 - June 2024

import math

#inputs
HFOV = 60.0 #degrees
Altitude = 120 #meters
ImageDiameter = 35.9 #mm
Wavelength = 0.54 #microns
PixelSize = 4.4 #microns

#calculate swath
theta_rad = HFOV * (math.pi/180.0)/2 #theta is half the HFOV, convert to radians
SWATH = 2*Altitude*math.tan(theta_rad) #trig to get swath in meters

#calculate focal length
mag = -ImageDiameter/(1000*SWATH) #unitless
s = -Altitude*1000 #object distance in mm
sprime = s*mag #image distance in mm
FocalLength = (s*sprime)/(s-sprime) #mm F = (s*s')/(s-s')

#calculate GSD
GSD = (Altitude * PixelSize) / (10*FocalLength) #Ground Sampling Distance in cm

#Calculate F/# and entrance pupil diameter
Fnumber = PixelSize/(1.22*Wavelength) #assume Airy disk radius equal to pixel size to determine required F/# (Ra = 1.22 * lambda * F#)
EntrancePupilDiameter = FocalLength/Fnumber #mm

print("Calculated Swath, Focal Length and Ground Sampling Distance:")
print(f"Swath = {round(SWATH,2)} meters")
print(f"Focal Length = {round(FocalLength,2)} mm")
print(f"GSD = {round(GSD,2)} cm")

print("Required F/# and Entrance Pupil Diameter to resolve GSD (Airy Disk Radius < 1 pixel):")
print(f"F/# = {round(Fnumber,2)}")
print(f"EPD = {round(EntrancePupilDiameter,2)} mm")
