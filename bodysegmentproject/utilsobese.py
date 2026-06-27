import math
import numpy as np


def calculate_axes (circumference, diameter):
        """Calculate the semi-major and semi-minor axes from circumference and one axis diameter."""
        semi_major_axis = diameter / 2
        semi_minor_axis = (circumference / (2 * math.pi))**2 - semi_major_axis**2
        semi_minor_axis = math.sqrt(semi_minor_axis) if semi_minor_axis > 0 else semi_major_axis
        return semi_major_axis, semi_minor_axis

def calculate_center_of_mass(h, r1, R1, r2, R2):
    # Calculate the center of mass using the given formula
    center_of_mass = (h * (r1 * (R1 + R2) + r2 * (R1 + 3 * R2))) / (2 * (r1 * (2 * R1 + R2) + r2 * (R1 + 2 * R2)))
    return center_of_mass

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

def combine_segments(self,segment1, segment2):
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


