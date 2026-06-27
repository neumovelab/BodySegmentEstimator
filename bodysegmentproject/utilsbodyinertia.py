import numpy as np
import math
from .utils import *
from .BodyObjects import *

def ellipsoid_inertia(R, r, h, m):
    Ixx = (1/5) * m * (R**2 + h**2)
    Iyy = (1/5) * m * (r**2 + R**2)
    Izz = (1/5) * m * (r**2 + h**2)
    return Ixx, Iyy, Izz

def head_parameters(head_circumference, head_length, head_mass, head_breadth):

    def calculate_axes (circumference, diameter):
        """Calculate the semi-major and semi-minor axes from circumference and one axis diameter."""
        semi_major_axis = diameter / 2
        semi_minor_axis = (circumference / (2 * math.pi))**2 - semi_major_axis**2
        semi_minor_axis = math.sqrt(semi_minor_axis) if semi_minor_axis > 0 else semi_major_axis
        return semi_major_axis, semi_minor_axis
    

    R, r  = calculate_axes (head_circumference, head_breadth) 
    # Semi-major axis of the ellipsoid (derived from head circumference)
    # Semi-minor axis of the ellipsoid (assuming circular cross-section)
    h = head_length / 2  # Half of the head length (semi-axis along the length)
    m = head_mass  # Mass of the head
    # Calculate the volume of the ellipsoid
    volume_head = (4 / 3) * np.pi * r * R * h
    
    center_of_mass_head_Y =  0
    center_of_mass_head_X =  0
    center_of_mass_head_Z =  0

    # Calculate moments of inertia for the ellipsoid
    Ixx_head, Iyy_head, Izz_head = ellipsoid_inertia(r, R, h, m)

    return Head(head_length,head_mass,head_circumference,volume_head,center_of_mass_head_X,center_of_mass_head_Y,center_of_mass_head_Z, Ixx_head, Iyy_head, Izz_head)
        


def calculate_center_of_mass(h, r1, R1, r2, R2):
    # Calculate the center of mass using the given formula
    center_of_mass = (h * (r1 * (R1 + R2) + r2 * (R1 + 3 * R2))) / (2 * (r1 * (2 * R1 + R2) + r2 * (R1 + 2 * R2)))
    return center_of_mass



def frustum_inertia(r1, R1, r2, R2, density, h):
    """
    Calculate the moments of inertia for a frustum of a right elliptical cone.
    
    Parameters:
    r1 (float): Semi-minor axis of the upper base ellipse
    R1 (float): Semi-major axis of the upper base ellipse
    r2 (float): Semi-minor axis of the lower base ellipse
    R2 (float): Semi-major axis of the lower base ellipse
    density (float): Density of the material
    h (float): Height of the frustum
    
    Returns:
    tuple: (Ixx, Iyy, Izz) moments of inertia for the frustum
    """
    volume = (1/3) * np.pi * h * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
    M = volume*density 
    Ixx= (np.pi / 240) * density * h * (
            4*h**2 * (r1*(2*R1 + 3*R2) + 3*r2*(R1 + 4*R2)) + 
            3 * (r1 * (4*R1**3 + 3*R1**2*R2 + 2*R1*R2**2 + R2**3) + 
                 r2 * (R1**3 + 2*R1**2*R2 + 3*R1*R2**2 + 4*R2**3)))
        

    Iyy = (np.pi / 80) * density * h * (
            r1**3 * (4*R1 + R2) + r1**2 * r2 * (3*R1 + 2*R2) + 
            r1 * (4*R1**3 + 3*R1**2*R2 + 3*r2**2*R2 + R2**3 + 2*R1*(r2**2 + R2**2)) + 
            r2 * (R1**3 + 2*R1**2*R2 + 4*R2*(r2**2 + R2**2) + R1*(r2**2 + 3*R2**2)))

    Izz = (np.pi / 240) * density * h * (4*h**2 * (r1*(2*R1 + 3*R2) + 3*r2*(R1 + 4*R2)) + 
                                       3 * (r1**3 * (4*R1 + R2) + r1**2 * r2 * (3*R1 + 2*R2) + 
                                            r1 * r2**2 * (2*R1 + 3*R2) + r2**3 * (R1 + 4*R2)))
    com = (h * (r1 * (R1 + R2) + r2 * (R1 + 3 * R2))) / (2 * (r1 * (2 * R1 + R2) + r2 * (R1 + 2 * R2)))
    
    Ixx= Ixx-(M*com**2)
    Izz= Izz-(M*com**2)
    
    return Ixx, Iyy, Izz

def elliptical_cone_inertia(R1, r1, h, m):
    
    Ixx = (3 * m / 20) * (4 * R1**2 + h**2)
    Iyy = (3 * m / 10) * (r1**2 + R1**2)
    Izz = (3 * m / 20) * (4 * r1**2 + h**2)
    com = (1/4) *h
    Ixx= Ixx-(m*com**2)
    Izz= Izz-(m*com**2)
    return Ixx, Iyy, Izz
      
def combine_segments(segment1, segment2):
    """
    Combine two segments using mass, center of mass (COM), and inertia properties.
    Implements the Parallel Axis Theorem for adjusting inertia when the COM is shifted.

    Parameters:
    - segment1 (dict): Properties of the first segment (mass, COM, inertia tensor).
    - segment2 (dict): Properties of the second segment (mass, COM, inertia tensor).

    Returns:
    - dict: Combined segment properties (mass, COM, inertia tensor).
    """
    # Calculate the mass of the resulting segment
    combined_mass = segment1['mass'] +  segment2['mass']
    
    if combined_mass == 0:
        raise ValueError("Combined mass is zero, division by zero in COM calculation.")

    # Calculate the center of mass (COM) of the resulting segment
    r1 = np.array(segment1['com'])  # Original COM for segment 1
    r2 = np.array(segment2['com'])  # Original COM for segment 2
    combined_com = (segment1['mass'] * r1 + segment2['mass'] * r2) / combined_mass

    # Calculate the moments of inertia of the resulting segment
    I1 = np.array(segment1['inertia'])  # Inertia tensor for segment 1
    I2 = np.array(segment2['inertia'])  # Inertia tensor for segment 2

    # Compute relative position of COM for each segment
    r1_relative = r1 - combined_com
    r2_relative = r2 - combined_com

    # Apply the Parallel Axis Theorem to X and Z components only
    I_combined = np.zeros((3, 3))
    # X-component
    I_combined[0, 0] = (
        I1[0, 0] + I2[0, 0] + segment1['mass'] * (r1_relative[1]**2) + segment2['mass'] * (r2_relative[1]**2) + segment1['mass'] * (r1_relative[2]**2) + segment2['mass'] * (r2_relative[2]**2)
    )  
    # Y-component
    I_combined[1, 1] = (
        I1[1, 1] + I2[1, 1] + segment1['mass'] * (r1_relative[0]**2) + segment2['mass'] * (r2_relative[0]**2) + segment1['mass'] * (r1_relative[2]**2) + segment2['mass'] * (r2_relative[2]**2)
    )  
    # Z-component
    I_combined[2, 2] = (
        I1[2, 2] + I2[2, 2] + segment1['mass'] * (r1_relative[0]**2) + segment2['mass'] * (r2_relative[0]**2) + segment1['mass'] * (r1_relative[1]**2) + segment2['mass'] * (r2_relative[1]**2)
    ) 
   
    # Check for negative moments of inertia and issue a warning
    if np.any(I_combined < 0):
        print("Warning: Negative moments of inertia detected. Results may be physically implausible.")
        # Optional: Clamp negative values to zero
        I_combined[I_combined < 0] = 0

    # Return the combined segment properties
    return {
        'mass': combined_mass,
        'com': combined_com,
        'inertia': I_combined
        
    }

def uppertorsoParameters(uppertorso_mass, Neckbase_circumference, Shoulder_breadth, Chest_depth,
                         upper_torso, middle_torso, shoulderwaistlen, Chest_circumference, Chest_breadth):
    
    # Function to calculate the volume of an elliptical frustum
    def calculate_frustum_volume(R1, r1, R2, r2, h):
        sqrt_arg = R1 * r1 * R2 * r2
        if sqrt_arg<0:
            print("Frustum volume with sqrt<0, check values")
            sqrt_arg=np.abs(sqrt_arg)
        return (1/3) * np.pi * h * (R1 * r1 + R2 * r2 + np.sqrt(sqrt_arg))
    

   

    # Calculate dimensions and volumes for upper and lower torso frustums
    neck_radius = Neckbase_circumference/(2*math.pi)
    shoulder_radius = Shoulder_breadth/2
    chest_radius = Chest_depth/2
    upper_torso_height = upper_torso + middle_torso - shoulderwaistlen
    lower_torso_height = shoulderwaistlen - middle_torso

    # Calculate volumes
    volume_uppertorso_upper = calculate_frustum_volume(neck_radius, neck_radius, shoulder_radius, chest_radius, upper_torso_height)
    volume_uppertorso_lower = calculate_frustum_volume(shoulder_radius, chest_radius, Chest_breadth/2, chest_radius, lower_torso_height)
    total_volume_uppertorso = volume_uppertorso_upper + volume_uppertorso_lower

    volume_uppertorso_upper = calculate_frustum_volume(neck_radius, neck_radius, shoulder_radius, chest_radius, upper_torso_height)
    volume_uppertorso_lower = calculate_frustum_volume(shoulder_radius, chest_radius, Chest_breadth/2, chest_radius, lower_torso_height)
    total_volume_uppertorso = volume_uppertorso_upper + volume_uppertorso_lower

    # Calculate mass distribution
    mass_upper = uppertorso_mass * (volume_uppertorso_upper / total_volume_uppertorso)
    mass_lower = uppertorso_mass * (volume_uppertorso_lower / total_volume_uppertorso)
    density = uppertorso_mass / total_volume_uppertorso

    # Calculate center of mass for each part
    com_upper = calculate_center_of_mass(upper_torso_height, neck_radius, neck_radius, shoulder_radius, chest_radius)
    com_lower = calculate_center_of_mass(lower_torso_height, shoulder_radius, chest_radius, Chest_breadth / 2, chest_radius)

    # Calculate overall center of mass using weighted average
    total_com = (volume_uppertorso_upper * com_upper + volume_uppertorso_lower * (upper_torso_height + com_lower)) / total_volume_uppertorso
    center_of_mass_uppertorso_X=0
    center_of_mass_uppertorso_Y=total_com
    center_of_mass_uppertorso_Z=0

    # Calculate moments of inertia for each part
    Ixx_upper, Iyy_upper, Izz_upper = frustum_inertia(neck_radius, neck_radius, shoulder_radius, chest_radius, density, upper_torso_height)
    Ixx_lower, Iyy_lower, Izz_lower = frustum_inertia(shoulder_radius, chest_radius, Chest_breadth / 2, chest_radius, density, lower_torso_height)

    # Combined Inertia Properties (neck base~chest) using the parallel axis theorem

    com_y_upper= com_upper
    com_y_lower= upper_torso_height + com_lower

    segment_upper = {
    'mass': mass_upper,
    'com': [0.0, com_y_upper , 0.0],
    'inertia': [[Ixx_upper, 0.0, 0.0], [0.0, Iyy_upper, 0.0], [0.0, 0.0, Izz_upper]]
    }

    segment_lower = {
    'mass': mass_lower,
    'com': [0.0, com_y_lower , 0.0],
    'inertia': [[Ixx_lower, 0.0, 0.0], [0.0, Iyy_lower, 0.0], [0.0, 0.0, Izz_lower]]
    }

    result = combine_segments(segment_upper, segment_lower)

    
    center_of_mass_uppertorso_X = result['com'][0]
    center_of_mass_uppertorso_Y = result['com'][1]*-1
    center_of_mass_uppertorso_Z = result['com'][2]
    Ixx_uppertorso = result['inertia'][0, 0]
    Iyy_uppertorso = result['inertia'][1, 1]
    Izz_uppertorso = result['inertia'][2, 2]


    return UpperTorso(upper_torso,uppertorso_mass,Chest_circumference,total_volume_uppertorso,center_of_mass_uppertorso_X,
                      center_of_mass_uppertorso_Y,center_of_mass_uppertorso_Z,
                      Ixx_uppertorso,Iyy_uppertorso,Izz_uppertorso)

    # Function to calculate parameters for the middle torso
def middletorsoParameters(Chest_circumference, Chest_breadth, Chest_depth,
                          Waist_circumference, Waist_breadth, Waist_depth,
                          middle_torso, middletorso_mass):
    # Calculate radii for chest and waist measurements
    r1 = Chest_depth / 2  # Radius for chest depth (half of chest depth)
    R1 = Chest_breadth / 2  # Radius for chest breadth (half of chest breadth)
    r2 = Waist_depth / 2  # Radius for waist depth (half of waist depth)
    R2 = Waist_breadth / 2  # Radius for waist breadth (half of waist breadth)
    
    # Assign height and mass for the middle torso
    h = middle_torso  # Height of the middle torso
    mass = middletorso_mass  # Mass of the middle torso
    
    # Calculate volume of the elliptical frustum representing the middle torso
    volume_middletorso = (1 / 3) * np.pi * h * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
    
    # Calculate density of the middle torso using mass and volume
    density = mass / volume_middletorso  # Density of the middle torso
    # Note: density can also be approximated as 0.00102 based on Pearsall et al. (1996)
    
    # Calculate the center of mass for the middle torso frustum
    center_of_mass_middletorso_X = 0
    center_of_mass_middletorso_Y = calculate_center_of_mass(h, r1, R1, r2, R2)*-1
    center_of_mass_middletorso_Z = 0
    
    # Calculate moments of inertia (Ixx, Iyy, Izz) for the frustum representing the middle torso
    Ixx_middletorso, Iyy_middletorso, Izz_middletorso = frustum_inertia(r1, R1, r2, R2, density, h)
    
    # Return all calculated parameters as a list
    return MiddleTorso(middle_torso,mass,Waist_circumference,volume_middletorso,center_of_mass_middletorso_X,
                       center_of_mass_middletorso_Y,center_of_mass_middletorso_Z,Ixx_middletorso,
                       Iyy_middletorso,Izz_middletorso)


# Function to calculate parameters for the lower torso
def lowertorsoParameters(Waist_circumference, Waist_breadth, Waist_depth, 
                         Buttock_circumference, Hip_breadth, buttock_depth,
                         lower_torso, lowertorso_mass, crotch_height, 
                         ankle_height, shank, thigh):
    # Calculate radii for waist and buttock measurements
    r1 = Waist_depth / 2  # Radius for waist depth (half of waist depth)
    R1 = Waist_breadth / 2  # Radius for waist breadth (half of waist breadth)
    r2 = buttock_depth / 2  # Radius for buttock depth (half of buttock depth)
    R2 = Hip_breadth / 2  # Radius for hip breadth (half of hip breadth)
    
    # Assign height and crotch length values
    h = lower_torso  # Height of the lower torso (in cm)
    crotch = (ankle_height + shank + thigh) - crotch_height  # Length from hip to crotch
    h1 = crotch  # Height of the lower part of the torso
    
    # Calculate volume of the elliptical frustum representing the upper lower torso
    volume_lowertorso_upper = (1 / 3) * np.pi * h * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
    # Calculate volume of the elliptical cone representing the lower part of the torso
    volume_lowertorso_lower = (np.pi * R2 * r2 * h1) / 3
    # Calculate total volume of the lower torso
    volume_lowertorso = volume_lowertorso_upper + volume_lowertorso_lower
    
    # Calculate mass distribution for upper and lower parts of the lower torso
    mass_upper = lowertorso_mass * (volume_lowertorso_upper / volume_lowertorso)  # Mass of upper part
    mass_lower = lowertorso_mass * (volume_lowertorso_lower / volume_lowertorso)  # Mass of lower part
    # Calculate density of the lower torso
    density = lowertorso_mass / volume_lowertorso
    
    # Calculate center of mass for the upper part of the lower torso
    center_of_mass_lowertorso_upper = calculate_center_of_mass(h, r1, R1, r2, R2)
    
    # Calculate moments of inertia for the upper part of the lower torso
    Ixx_lowertorso_upper, Iyy_lowertorso_upper, Izz_lowertorso_upper = frustum_inertia(r1, R1, r2, R2, density, h)
    
    # Calculate center of mass for the lower part of the lower torso
    center_of_mass_lowertorso_lower = h1 / 4  # Approximate center of mass for a cone
    
    # Calculate moments of inertia for the lower part of the lower torso
    Ixx_lowertorso_lower, Iyy_lowertorso_lower, Izz_lowertorso_lower = elliptical_cone_inertia(R2, r2, h1, mass_lower)
    
    # Calculate combined center of mass for the entire lower torso
    
    # Combined Inertia Properties (waist~crotch)
    com_y_upper= center_of_mass_lowertorso_upper
    com_y_lower= lower_torso + center_of_mass_lowertorso_lower

    segment_upper = {
        'mass': mass_upper,
        'com': [0.0, com_y_upper , 0.0],
        'inertia': [[Ixx_lowertorso_upper, 0.0, 0.0], [0.0, Iyy_lowertorso_upper, 0.0], [0.0, 0.0, Izz_lowertorso_upper]]
    }

    segment_lower = {
        'mass': mass_lower,
        'com': [0.0, com_y_lower, 0.0],
        'inertia': [[Ixx_lowertorso_lower, 0.0, 0.0], [0.0, Iyy_lowertorso_lower, 0.0], [0.0, 0.0, Izz_lowertorso_lower]]
    }


    result = combine_segments(segment_upper, segment_lower)

    
    center_of_mass_lowertorso_X = result['com'][0] 
    center_of_mass_lowertorso_Y = result['com'][1]*-1
    center_of_mass_lowertorso_Z = result['com'][2]
    Ixx_lowertorso = result['inertia'][0, 0]
    Iyy_lowertorso = result['inertia'][1, 1]
    Izz_lowertorso = result['inertia'][2, 2]


    # Return all calculated parameters as a list
    return LowerTorso(lower_torso,lowertorso_mass,Buttock_circumference,volume_lowertorso,center_of_mass_lowertorso_X,center_of_mass_lowertorso_Y,
                      center_of_mass_lowertorso_Z,Ixx_lowertorso,Iyy_lowertorso,Izz_lowertorso)

# Function to calculate parameters for the thigh
def thighParameters(thigh, thigh_circumference, lowerthigh_circumference, thigh_mass,
                     crotch_height, ankle_height, shank):
    # Calculate crotch length based on height values
    crotch = (ankle_height + shank + thigh) - crotch_height
    
    # Calculate radii for thigh and lower thigh circumferences
    r1 = thigh_circumference / (2 * math.pi)  # Radius at one end (thigh circumference)
    R1=r1
    r2 = lowerthigh_circumference/(2 * np.pi)  # radius at other end
    R2=r2
    
    
    # Assign height values for different parts of the thigh
    h2 = thigh - crotch  # Height of the upper part of the thigh
    h1 = crotch  # Height of the lower part of the thigh
    h = thigh  # Total height of the thigh
    
    # Calculate volume of the elliptical cone and the elliptical frustum representing the thigh
    
    volume_upperthigh =  (np.pi * (r1)**2 * h1) / 3
    volume_lowerthigh = (1/3) * np.pi * h2 * (r1**2 + r2**2 + r1*r2)
    volume_thigh= volume_upperthigh+volume_lowerthigh
    
    mass_upper=  thigh_mass* (volume_upperthigh/volume_thigh)
    mass_lower=  thigh_mass * (volume_lowerthigh/volume_thigh)
    
    # Calculate density of the thigh
    density = thigh_mass / volume_thigh
    # Center of mass of biased cone
    center_of_mass_upper = h1*(3/4)
    
    # Center of mass of frustum
    center_of_mass_lower = calculate_center_of_mass(h2, r1, R1, r2, R2)
    # Center of mass of biased cone
    center_of_mass_upper = h1*(3/4)
    
    # distance from Center of mass of biased cone to mid-point of cone at z-axis
    d1_z=(r1)*(0.25)
    
    # Inertia of cone 

    Ixx_upperthigh, Iyy_upperthigh, Izz_upperthigh = elliptical_cone_inertia(R2, r2, h1, mass_upper)
    # Inertia of biased cone: Implements the Parallel Axis Theorem for adjusting inertia when the COM is shifted.
    Ixx_upperthigh += (mass_upper * d1_z**2)
    Iyy_upperthigh += (mass_upper * d1_z**2)
    
    # Inertia of frustum
    Ixx_lowerthigh, Iyy_lowerthigh, Izz_lowerthigh = frustum_inertia(r1, R1, r2, R2, density, h2)

    # Combined Inertia Properties (crotch~knee)

    com_y_upper= center_of_mass_upper 
    com_z_upper= (r1)*(0.25)+r1

    com_y_lower= crotch+center_of_mass_lower 
    com_z_lower= r1


    # Combined Inertia Properties (crotch~knee)
    segment_upper = {
        'mass': mass_upper,
        'com': [0.0, com_y_upper,com_z_upper],
        'inertia': [[Ixx_upperthigh, 0.0, 0.0], [0.0, Iyy_upperthigh, 0.0], [0.0, 0.0, Izz_upperthigh]]
    }

    segment_lower = {
        'mass': mass_lower,
        'com': [0.0, com_y_lower, com_z_lower],
        'inertia': [[Ixx_lowerthigh, 0.0, 0.0], [0.0, Iyy_lowerthigh, 0.0], [0.0, 0.0, Izz_lowerthigh]]
    }


    result = combine_segments(segment_upper, segment_lower)

    thigh_mass = result['mass']
    center_of_mass_thigh_X = result['com'][0] 
    center_of_mass_thigh_Y = (result['com'][1]-h1)*-1
    center_of_mass_thigh_Z = result['com'][2]-r1
    Ixx_thigh = result['inertia'][0, 0]
    Iyy_thigh = result['inertia'][1, 1]
    Izz_thigh = result['inertia'][2, 2]
    
    return Thigh(thigh,thigh_mass,thigh_circumference,volume_thigh,
                 center_of_mass_thigh_X,center_of_mass_thigh_Y,center_of_mass_thigh_Z,
                 Ixx_thigh,Iyy_thigh,Izz_thigh)
    
    

# Function to calculate parameters for the shank
def shankParameters(shank, calf_circumference, ankle_circumference, shank_mass):
    # Calculate radii for calf and ankle circumferences
    r1 = calf_circumference / (2 * math.pi)  # Radius at one end (calf circumference)
    R1=r1
    r2 = ankle_circumference / (2 * math.pi)  # Radius at the other end (ankle circumference)
    R2=r2
    # Assign height and mass for the shank
    h = shank  # Height of the shank
    mass = shank_mass  # Mass of the shank
    
    # Calculate volume of the frustum representing the shank
    volume_shank = (1 / 3) * np.pi * h * (r1**2 + r2**2 + r1 * r2)
    
    # Calculate density of the shank
    density = mass / volume_shank
    
    # Calculate center of mass for the shank
    center_of_mass_shank_Y = calculate_center_of_mass(h, r1, R1, r2, R2)*-1
    center_of_mass_shank_X = 0
    center_of_mass_shank_Z = 0
    
    # Calculate moments of inertia (Ixx, Iyy, Izz) for the shank frustum
    Ixx_shank, Iyy_shank, Izz_shank = frustum_inertia(r1, R1, r2, R2, density, h)
    
    # Return all calculated parameters as a list
    return Shank(shank,shank_mass,calf_circumference,volume_shank,center_of_mass_shank_X,
                 center_of_mass_shank_Y,center_of_mass_shank_Z,Ixx_shank,Iyy_shank,Izz_shank)

# Function to calculate parameters for the foot
def footParameters(foot, ankle_height, balloffoot_circumference, foot_mass):
    # Calculate radii for ankle height and ball of foot circumference
    r1 = ankle_height / 2  # Radius at one end (half of ankle height)
    R1=r1
    r2 = balloffoot_circumference / (2 * np.pi)  # Radius at the other end (ball of foot circumference)
    R2=r2

    # Assign height and mass for the foot
    h = foot  # Height of the foot
    mass = foot_mass  # Mass of the foot
    
    # Calculate volume of the frustum representing the foot
    volume_foot = (1 / 3) * np.pi * h * (r1**2 + r2**2 + r1 * r2)
    
    # Calculate density of the foot
    density = mass / volume_foot
    
    # Calculate center of mass for the foot frustum
    center_of_mass_foot_X = calculate_center_of_mass(h, r1, R1, r2, R2)-(h/2)
    center_of_mass_foot_Y = r1*-1
    center_of_mass_foot_Z = 0
    
    # Calculate moments of inertia (Ixx, Iyy, Izz) for the foot frustum
    Ixx_foot, Iyy_foot, Izz_foot = frustum_inertia(r1, R1, r2, R2, density, h)
    Ixx_foot= Iyy_foot
    Iyy_foot= Izz_foot
    
    # Return all calculated parameters as a list
    return Foot(foot,foot_mass,balloffoot_circumference,volume_foot,center_of_mass_foot_X,
                center_of_mass_foot_Y,center_of_mass_foot_Z,
                Ixx_foot,Iyy_foot,Izz_foot)

# Function to calculate parameters for the upper arm
def upperarmParameters(upperarm, biceps_circumference, forearm_circumference, upperarm_mass):
    # Calculate radii for biceps and forearm circumferences
    r1 = biceps_circumference / (2 * np.pi)  # Radius at one end (biceps circumference)
    R1=r1
    r2 = forearm_circumference / (2 * np.pi)  # Radius at the other end (forearm circumference)
    R2=r2
    
    # Assign height and mass for the upper arm
    h = upperarm  # Height of the upper arm
    mass = upperarm_mass  # Mass of the upper arm
    
    # Calculate volume of the frustum representing the upper arm
    volume_upperarm = (1 / 3) * np.pi * h * (r1**2 + r2**2 + r1 * r2)
    
    # Calculate density of the upper arm
    density = mass / volume_upperarm
    
    # Calculate center of mass for the upper arm frustum
    center_of_mass_upperarm_Y =  calculate_center_of_mass(h, r1, R1, r2, R2)*-1
    center_of_mass_upperarm_X = 0
    center_of_mass_upperarm_Z =0 
    
    # Calculate moments of inertia (Ixx, Iyy, Izz) for the upper arm frustum
    Ixx_upperarm, Iyy_upperarm, Izz_upperarm = frustum_inertia(r1, R1, r2, R2, density, h)
    
    return UpperArm(upperarm,upperarm_mass,biceps_circumference,volume_upperarm,center_of_mass_upperarm_X,
                    center_of_mass_upperarm_Y,center_of_mass_upperarm_Z,
                    Ixx_upperarm,Iyy_upperarm,Izz_upperarm)

# Function to calculate parameters for the forearm
def forearmParameters(forearm, forearm_circumference, wrist_circumference, forearm_mass):
    # Calculate radii for forearm and wrist circumferences
    r1 = forearm_circumference / (2 * np.pi)  # Radius at one end (forearm circumference)
    R1=r1
    r2 = wrist_circumference / (2 * np.pi)  # Radius at the other end (wrist circumference)
    R2=r2

    # Assign height and mass for the forearm
    h = forearm  # Height of the forearm
    mass = forearm_mass  # Mass of the forearm
    
    # Calculate volume of the frustum representing the forearm
    volume_forearm = (1 / 3) * np.pi * h * (r1**2 + r2**2 + r1 * r2)
    
    # Calculate density of the forearm
    density = mass / volume_forearm
    
    # Calculate center of mass for the forearm frustum
    center_of_mass_forearm_Y = calculate_center_of_mass(h, r1, R1, r2, R2)*-1
    center_of_mass_forearm_X = 0
    center_of_mass_forearm_Z = 0
    
    # Calculate moments of inertia (Ixx, Iyy, Izz) for the forearm frustum
    Ixx_forearm, Iyy_forearm, Izz_forearm = frustum_inertia(r1, R1, r2, R2, density, h)
    
    # Return all calculated parameters as a list
    return Forearm(forearm,forearm_mass,forearm_circumference,volume_forearm,
                   center_of_mass_forearm_X,center_of_mass_forearm_Y,center_of_mass_forearm_Z,
                   Ixx_forearm,Iyy_forearm,Izz_forearm)

# Function to calculate parameters for the hand
def handParameters(Hand_length, hand_mass):
    # Calculate characteristic length for the hand (approximation)
    r = Hand_length/4 # Hand length divided by 4 to approximate radius of equivalent sphere
    R = r
    h= R
    m = hand_mass  # Mass of the hand
    # Calculate volume of the ellipsoid representing the hand
    volume_hand = (4 / 3) * np.pi * r**3
    
    # Calculate center of mass for the hand (approximated at the center)
    center_of_mass_hand_Y =  0
    center_of_mass_hand_X =  0
    center_of_mass_hand_Z =  0
    
    # Calculate moments of inertia (Ixx, Iyy, Izz) for the hand treated as a sphere
    Ixx_hand, Iyy_hand, Izz_hand = ellipsoid_inertia (R, r, h, m)
    
    
    return Hand(Hand_length,hand_mass,None,volume_hand,center_of_mass_hand_X,
                center_of_mass_hand_Y,center_of_mass_hand_Z,
                Ixx_hand,Iyy_hand,Izz_hand)

    