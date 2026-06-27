import numpy as np
import math
from .utilsobese import *
from .BodyObjects import *


def ellipsoid_inertia(R, r, h, m):
    Ixx = (1/5) * m * (R**2 + h**2)
    Iyy = (1/5) * m * (r**2 + R**2)
    Izz = (1/5) * m * (r**2 + h**2)
    return Ixx, Iyy, Izz

def headObeseParameters(head_circumference_obese, head_length, head_breadth_obese, head_mass_obese):
    """
    Calculate parameters for an obese head model based on given measurements.

    :param head_circumference_base: Base head circumference value.
    :param head_length: Length of the head.
    :param head_mass_base: Base head mass value.
    :param head_mass_obese: Obese head mass value.
    :return: List of head parameters including length, mass, volume, center of mass, and inertia.
    """

    def calculate_axes (circumference, diameter):
        """Calculate the semi-major and semi-minor axes from circumference and one axis diameter."""
        semi_major_axis = diameter / 2
        semi_minor_axis = (circumference / (2 * math.pi))**2 - semi_major_axis**2
        semi_minor_axis = math.sqrt(semi_minor_axis) if semi_minor_axis > 0 else semi_major_axis
        return semi_major_axis, semi_minor_axis
    

    R, r  = calculate_axes (head_circumference_obese, head_breadth_obese) 
    # Semi-major axis of the ellipsoid (derived from head circumference)
    # Semi-minor axis of the ellipsoid (assuming circular cross-section)
    h = head_length / 2  # Half of the head length (semi-axis along the length)
    m = head_mass_obese  # Mass of the head
    # Calculate the volume of the ellipsoid
    volume_head = (4 / 3) * np.pi * r * R * h
    
    
    # Center of mass of ellipsoid (at the center)
    center_of_mass_head_obese_Y =  0
    center_of_mass_head_obese_X =  0
    center_of_mass_head_obese_Z =  0
    
    # Calculate moments of inertia for the ellipsoid
    Ixx_head_obese, Iyy_head_obese, Izz_head_obese = ellipsoid_inertia(r, R, h, m)

    # Return all parameters as a list
    return Head(head_length,head_mass_obese,head_circumference_obese,volume_head,center_of_mass_head_obese_X,center_of_mass_head_obese_Y,center_of_mass_head_obese_Z,
                Ixx_head_obese,Iyy_head_obese,Izz_head_obese)



class ObeseTorsoDissection():
    def __init__(self, Neckbase_circumference_base, Neckbase_circumference_obese,
                 Shoulder_breadth_base,Shoulder_breadth_obese,Chest_depth_base,Chest_depth_obese, 
                 upper_torso, middle_torso,lower_torso,
                 shoulderwaistlen,Chest_circumference_base,Chest_circumference_obese,
                 Chest_breadth_base, Chest_breadth_obese, uppertorso_mass,BMI_obese,
                 Waist_circumference_base,Waist_circumference_obese,
                 Waist_depth_base,Waist_depth_obese,middletorso_mass,
                 Waist_breadth_base,Waist_breadth_obese,Hip_breadth_base,Hip_breadth_obese,
                 buttock_depth_base,buttock_depth_obese,lowertorso_mass,Hip_circumference_base,Hip_circumference_obese,
                 torso_mass_obese,crotch_height,ankle_height,shank,thigh,uppertorsomassobese=None,middletorsomassobese=None,
                 lowertorsomassobese=None):
        
        self.Neckbase_circumference_base=Neckbase_circumference_base
        self.Neckbase_circumference_obese = Neckbase_circumference_obese 
        self.Shoulder_breadth_base=Shoulder_breadth_base
        self.Shoulder_breadth_obese=Shoulder_breadth_obese
        self.upper_torso=upper_torso
        self.middle_torso=middle_torso
        self.lower_torso=lower_torso
        self.shoulderwaistlen=shoulderwaistlen
        self.Chest_circumference_base=Chest_circumference_base
        self.Chest_circumference_obese=Chest_circumference_obese
        self.Chest_breadth_base=Chest_breadth_base
        self.Chest_breadth_obese=Chest_breadth_obese
        self.Chest_depth_base=Chest_depth_base
        self.Chest_depth_obese=Chest_depth_obese
        self.uppertorso_mass=uppertorso_mass
        self.lowertorso_mass=lowertorso_mass
        self.middletorso_mass=middletorso_mass
        self.BMI_obese=BMI_obese

        self.Waist_circumference_base=Waist_circumference_base
        self.Waist_circumference_obese=Waist_circumference_obese
        self.Waist_depth_base=Waist_depth_base
        self.Waist_depth_obese=Waist_depth_obese
        self.Waist_breadth_base=Waist_breadth_base
        self.Waist_breadth_obese=Waist_breadth_obese
        self.Hip_breadth_base=Hip_breadth_base
        self.Hip_breadth_obese=Hip_breadth_obese
        self.buttock_depth_base=buttock_depth_base
        self.buttock_depth_obese=buttock_depth_obese
        self.Hip_circumference_base=Hip_circumference_base
        self.Hip_circumference_obese=Hip_circumference_obese
        self.torso_mass_obese=torso_mass_obese
        self.crotch_height=crotch_height
        self.ankle_height=ankle_height
        self.shank=shank
        self.thigh=thigh
        self.uppertorsomassobese=uppertorsomassobese
        self.middletorsomassobese=middletorsomassobese
        self.lowertorsomassobese=lowertorsomassobese
    
    
    def calculate_upper_torso_volume(self):
        # Calculate the volume of the upper torso (upper and lower parts)
        R1 = r1 = self.Neckbase_circumference_base / (2 * np.pi)  # Neck radius
        R2 = self.Shoulder_breadth_base / 2
        r2 = self.Chest_depth_base / 2
        h1 = self.upper_torso + self.middle_torso - self.shoulderwaistlen  # Height of upper torso (upper part)
        volume_uppertorso_upper = (1/3) * np.pi * h1 * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))

        # Calculate the volume of the upper torso (lower part)
        R1, r1 = self.Shoulder_breadth_base / 2, self.Chest_depth_base / 2
        R2 = self.Chest_breadth_base / 2
        r2 = self.Chest_depth_base / 2
        h2 = self.shoulderwaistlen - self.middle_torso  # Height of upper torso (lower part)
        volume_uppertorso_lower = (1/3) * np.pi * h2 * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
        volume_uppertorso_base = volume_uppertorso_upper + volume_uppertorso_lower

        # Calculate volume of upper torso for obese model (upper part)
        R1 = r1 = self.Neckbase_circumference_obese / (2 * np.pi)  # Neck radius
        R2 = self.Shoulder_breadth_obese / 2
        r2 = self.Chest_depth_base / 2
        self.volume_uppertorso_upper_obese = (1/3) * np.pi * h1 * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))

        # Calculate volume of upper torso for obese model (lower part)
        R1, r1 = self.Shoulder_breadth_obese / 2, self.Chest_depth_base / 2
        R2, r2 = self.Chest_breadth_obese / 2, self.Chest_depth_obese / 2
        #self.volume_uppertorso_lower_obese = (1/3) * np.pi * h2 * (r1**2 + r2**2 + r1 * r2)
        self.volume_uppertorso_lower_obese = (1/3) * np.pi * h2 * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
        self.volume_uppertorso_obese = self.volume_uppertorso_upper_obese + self.volume_uppertorso_lower_obese
        self.volumechange_uppertorso = self.volume_uppertorso_obese - volume_uppertorso_base


    
    def calculate_middle_torso_volume(self):
        # Calculate the volume of the middle torso (base model)
        r1 = self.Chest_depth_base / 2  # Chest radius (semi-minor axis)
        R1 = self.Chest_breadth_base / 2  # Chest radius (semi-major axis)
        r2 = self.Waist_depth_base / 2  # Waist radius (semi-minor axis)
        R2 = self.Waist_breadth_base / 2  # Waist radius (semi-major axis)
        h = self.middle_torso  # Height of middle torso
        volume_middletorso_base = (1/3) * np.pi * h * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))

        # Calculate volume of middle torso for obese model
        R1, r1 = self.Chest_breadth_obese / 2, self.Chest_depth_obese / 2
        R2, r2 = self.Waist_breadth_obese / 2, self.Waist_depth_obese / 2
        self.volume_middletorso_obese = (1/3) * np.pi * h * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
        self.volumechange_middletorso = self.volume_middletorso_obese - volume_middletorso_base

    
    def calculate_lower_torso_volume(self):
        # Calculate the volume of the lower torso (base model)
        r1 = self.Waist_depth_base / 2  # Waist radius (semi-minor axis)
        R1 = self.Waist_breadth_base / 2  # Waist radius (semi-major axis)
        r2 = self.buttock_depth_base / 2  # Buttock radius (semi-minor axis)
        R2 = self.Hip_breadth_base / 2  # Hip radius (semi-major axis)
        
        self.crotch=self.ankle_height+self.shank+self.thigh-self.crotch_height # length for hip ~ crotch
        
        volume_lowertorso_base_upper = (1/3) * np.pi * self.lower_torso * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
        volume_lowertorso_base_lower = (np.pi * R2 * r2 * self.crotch) / 3
        volume_lowertorso_base= volume_lowertorso_base_upper+volume_lowertorso_base_lower

        # Calculate volume of lower torso for obese model
        R1, r1 = self.Waist_breadth_obese/2, self.Waist_depth_obese/2
        R2, r2 = self.buttock_depth_obese/2, self.Hip_breadth_obese/2
        self.volume_lowertorso_obese_upper = (1/3) * np.pi * self.lower_torso * (R1 * r1 + R2 * r2 + np.sqrt(R1 * r1 * R2 * r2))
        self.volume_lowertorso_obese_lower = (np.pi * R2 * r2 * self.crotch) / 3
        self.volume_lowertorso_obese= self.volume_lowertorso_obese_upper+self.volume_lowertorso_obese_lower
        self.volumechange_lowertorso = self.volume_lowertorso_obese - volume_lowertorso_base

        
    def calculate_torso_mass(self):
        # Calculate the mass of the entire torso based on volume changes
        torso_mass_base = self.uppertorso_mass + self.middletorso_mass + self.lowertorso_mass
        Total_volumechange = self.volumechange_uppertorso + self.volumechange_middletorso + self.volumechange_lowertorso
        Total_masschange = self.torso_mass_obese - torso_mass_base

        # Adjust individual torso masses for obese model
        if self.uppertorsomassobese==None:
            self.uppertorso_mass_obese = self.uppertorso_mass + Total_masschange * (self.volumechange_uppertorso / Total_volumechange)
            self.middletorso_mass_obese = self.middletorso_mass + Total_masschange * (self.volumechange_middletorso / Total_volumechange)
            self.lowertorso_mass_obese = self.lowertorso_mass + Total_masschange * (self.volumechange_lowertorso / Total_volumechange)
        else:
            self.uppertorso_mass_obese=self.uppertorsomassobese
            self.middletorso_mass_obese=self.middletorsomassobese
            self.lowertorso_mass_obese=self.lowertorsomassobese

        
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
    
    def uppertorso_inertia(self):
        """
        Calculate the inertia properties of the obese upper torso.
    
        Returns:
            list: Inertia properties of the upper torso.
        """
        # Height of the upper torso
        h1 = self.upper_torso + self.middle_torso - self.shoulderwaistlen
        h2 = self.shoulderwaistlen - self.middle_torso
    
        # Radii calculations for center of mass and inertia
        R1 = r1 = self.Neckbase_circumference_obese / (2 * np.pi)  # Radius at the neck
        R2 = self.Shoulder_breadth_obese / 2  # Shoulder radius
        r2 = self.Chest_depth_base / 2  # Chest depth
    
        # Calculate density based on mass and volume of the obese upper torso
        density = self.uppertorso_mass_obese / self.volume_uppertorso_obese
    
        # Calculate center of mass for the upper part of the obese upper torso
        center_of_mass_upper1 = calculate_center_of_mass(h1, r1, R1, r2, R2)
    
        # Calculate mass distribution for upper and lower parts of the torso
        mass_upper = self.uppertorso_mass_obese * (self.volume_uppertorso_upper_obese / self.volume_uppertorso_obese)
        mass_lower = self.uppertorso_mass_obese * (self.volume_uppertorso_lower_obese / self.volume_uppertorso_obese)
    
        # Calculate moments of inertia for the upper part of the torso
        Ixx_uppertorso_upper , Iyy_uppertorso_upper , Izz_uppertorso_upper  = frustum_inertia(r1, R1, r2, R2, density, h1)
        
        R1= self.Shoulder_breadth_obese/2
        r1= self.Chest_depth_base/2
        
        R2=self.Chest_breadth_obese/2
        r2 =self.Chest_depth_obese/2
    
        # Calculate center of mass for the lower part of the obese upper torso
        center_of_mass_upper2 = calculate_center_of_mass(h2, r1, R1, r2, R2)
    
        # Calculate moments of inertia for the lower part of the torso
        Ixx_uppertorso_lower , Iyy_uppertorso_lower , Izz_uppertorso_lower  = frustum_inertia(r1, R1, r2, R2, density, h2)
    
        # Adjust moments of inertia for the center of mass shift
        # Combined Inertia Properties (neck base~chest)
        com_y_upper= center_of_mass_upper1
        com_y_lower= h1+center_of_mass_upper2


        segment_upper= {
            'mass': mass_upper,
            'com': [0.0, com_y_upper , 0.0],
            'inertia': [[Ixx_uppertorso_upper, 0.0, 0.0], [0.0, Iyy_uppertorso_upper, 0.0], [0.0, 0.0, Izz_uppertorso_upper]]
        }

        segment_lower = {
            'mass': mass_lower,
            'com': [0.0, com_y_lower , 0.0],
            'inertia': [[Ixx_uppertorso_lower, 0.0, 0.0], [0.0, Iyy_uppertorso_lower, 0.0], [0.0, 0.0, Izz_uppertorso_lower]]
        }

        result = self.combine_segments(segment_upper, segment_lower)

        # Return the calculated properties for the upper torso
        center_of_mass_uppertorso_obese_X = result['com'][0]
        center_of_mass_uppertorso_obese_Y = result['com'][1]*-1
        center_of_mass_uppertorso_obese_Z = result['com'][2]
        Ixx_uppertorso_obese = result['inertia'][0, 0]
        Iyy_uppertorso_obese = result['inertia'][1, 1]
        Izz_uppertorso_obese = result['inertia'][2, 2]
        
    
        # Returning the calculated properties for the upper torso
        return UpperTorso(self.upper_torso,self.uppertorso_mass_obese,self.Chest_circumference_obese,self.volume_uppertorso_obese,
                          center_of_mass_uppertorso_obese_X,center_of_mass_uppertorso_obese_Y,center_of_mass_uppertorso_obese_Z,
                          Ixx_uppertorso_obese,Iyy_uppertorso_obese,Izz_uppertorso_obese)
    
    def middletorso_inertia(self):
        """
        Calculate the inertia properties of the obese middle torso.
    
        Returns:
            list: Inertia properties of the middle torso.
        """
        # Define radii for the middle torso
        R1, r1 = self.Chest_breadth_obese / 2, self.Chest_depth_obese / 2
        R2, r2 = self.Waist_breadth_obese / 2, self.Waist_depth_obese / 2
    
        # Calculate density based on mass and volume
        density = self.middletorso_mass_obese / self.volume_middletorso_obese
    
        # Calculate center of mass for the middle torso
        center_of_mass_middletorso_obese = calculate_center_of_mass(self.middle_torso, r1, R1, r2, R2)
        center_of_mass_middletorso_obese_Y= center_of_mass_middletorso_obese*-1
        center_of_mass_middletorso_obese_Z= 0
        # Calculate moments of inertia for the middle torso based on BMI
        
        Ixx_middletorso_obese, Iyy_middletorso_obese, Izz_middletorso_obese = frustum_inertia(r1, R1, r2, R2, density, self.middle_torso)
        
        # Calculate anterior and posterior volume components of the middle torso
        if r1 > r2:
            volume_middletorso_obese_posterior = (np.pi * R1 * r2) * self.middle_torso
            volume_middletorso_obese_anterior = self.volume_middletorso_obese - volume_middletorso_obese_posterior
            com1_x =  (2*r1 - 2*r2) * (1/3)+2*r2 # com of Volume of elliptical halfcone
            com2_x =  r2
            com_x = (volume_middletorso_obese_anterior * com1_x + volume_middletorso_obese_posterior * com2_x) / self.volume_middletorso_obese
            d_x = abs(com_x - r2)
        else:# In case of waist_depth is larger than chest_depth 
            volume_middletorso_obese_posterior = (np.pi * R1 * r2) * self.middle_torso
            volume_middletorso_obese_anterior = self.volume_middletorso_obese - volume_middletorso_obese_posterior
            com1_x = (2*r2 - 2*r1) * (1/3)+2*r1 # com of Volume of elliptical halfcone
            com2_x = r1
            com_x = (volume_middletorso_obese_anterior * com1_x + volume_middletorso_obese_posterior * com2_x) / self.volume_middletorso_obese
            d_x = abs(com_x - r1)
    
        # use the principle of weighted averages, considering the volume and center of mass of each part    
        center_of_mass_middletorso_obese_X= d_x      
        
        # incorporate the principles of the parallel axis theorem to adjust the moments of inertia when the center of mass is shifted.
        Iyy_middletorso_obese += (self.middletorso_mass_obese * d_x**2 )
        Izz_middletorso_obese += (self.middletorso_mass_obese * d_x**2 )
    
        # Return the calculated properties for the middle torso
        return MiddleTorso(self.middle_torso,self.middletorso_mass_obese,self.Waist_circumference_obese,self.volume_middletorso_obese,
                           center_of_mass_middletorso_obese_X,center_of_mass_middletorso_obese_Y,center_of_mass_middletorso_obese_Z,
                           Ixx_middletorso_obese,Iyy_middletorso_obese,Izz_middletorso_obese)
    
    
    def lowertorso_inertia(self):
        # Parameters for lower torso 
        R1, r1 = self.Waist_breadth_obese/2, self.Waist_depth_obese/2

        R2, r2 = self.Hip_breadth_obese/2, self.buttock_depth_obese/2
        
        mass_upper=  self.lowertorso_mass_obese* (self.volume_lowertorso_obese_upper/self.volume_lowertorso_obese)
        mass_lower=  self.lowertorso_mass_obese* (self.volume_lowertorso_obese_lower/self.volume_lowertorso_obese)
        h1 = self.lower_torso
        h2 = self.crotch
        density= self.lowertorso_mass_obese/self.volume_lowertorso_obese #density=0.00107, from Pearsall et al. (1996)
        center_of_mass_lowertorso_upper = calculate_center_of_mass(self.lower_torso, r1, R1, r2, R2)
        center_of_mass_lowertorso_lower = (h2)/4
        
        # Inertia calculations formulas_upper

        Ixx_lowertorso_upper, Iyy_lowertorso_upper, Izz_lowertorso_upper   = frustum_inertia(r1, R1, r2, R2, density, h1)

        # Inertia calculations formulas_lower

        Ixx_lowertorso_lower, Iyy_lowertorso_lower, Izz_lowertorso_lower = elliptical_cone_inertia(R2, r2, h2, mass_lower)


        # Combined Inertia Properties (waist~crotch)
        
        if r1 > r2:
            volume_lowertorso_obese_upper_posterior = (np.pi * R1 * r2) * self.lower_torso # Volume of elliptical cylinder
            volume_lowertorso_obese_upper_anterior = self.volume_lowertorso_obese_upper - volume_lowertorso_obese_upper_posterior
            com1_x =  (2*r1 - 2*r2) * (1/3)+2*r2 # com of Volume of elliptical halfcone
            com2_x =  r2
            com_x_upper = (volume_lowertorso_obese_upper_anterior * com1_x + volume_lowertorso_obese_upper_posterior * com2_x) / self.volume_lowertorso_obese
        else: # In case of buttock_depth is larger than waist_depth 
            volume_lowertorso_obese_upper_posterior = (np.pi * R1 * r2) * self.lower_torso # Volume of elliptical cylinder
            volume_lowertorso_obese_upper_anterior = self.volume_lowertorso_obese_upper - volume_lowertorso_obese_upper_posterior
            com1_x = (2*r2 - 2*r1) * (1/3)+2*r1 # com of Volume of elliptical halfcone
            com2_x = r1
            com_x_upper = (volume_lowertorso_obese_upper_anterior * com1_x + volume_lowertorso_obese_upper_posterior * com2_x) / self.volume_lowertorso_obese
        
        # use the principle of weighted averages, considering the volume and center of mass of each part            

        com_x_lower = r2

        com_y_upper= center_of_mass_lowertorso_upper
        com_y_lower= self.lower_torso+center_of_mass_lowertorso_lower


        segment_upper = {
            'mass': mass_upper,
            'com': [com_x_upper, com_y_upper , 0.0],
            'inertia': [[Ixx_lowertorso_upper, 0.0, 0.0], [0.0, Iyy_lowertorso_upper, 0.0], [0.0, 0.0, Izz_lowertorso_upper]]
        }

        segment_lower = {
            'mass': mass_lower,
            'com': [com_x_lower, com_y_lower, 0.0],
            'inertia': [[Ixx_lowertorso_lower, 0.0, 0.0], [0.0, Iyy_lowertorso_lower, 0.0], [0.0, 0.0, Izz_lowertorso_lower]]
        }


        result = self.combine_segments(segment_upper, segment_lower)

        mass_upper,
        center_of_mass_lowertorso_obese_X = result['com'][0] -r1
        center_of_mass_lowertorso_obese_Y = result['com'][1]*-1
        center_of_mass_lowertorso_obese_Z = result['com'][2]
        Ixx_lowertorso_obese = result['inertia'][0, 0]
        Iyy_lowertorso_obese = result['inertia'][1, 1]
        Izz_lowertorso_obese = result['inertia'][2, 2]

        
        return LowerTorso(self.lower_torso,self.lowertorso_mass_obese,None,self.volume_lowertorso_obese,
                          center_of_mass_lowertorso_obese_X,center_of_mass_lowertorso_obese_Y,center_of_mass_lowertorso_obese_Z,
                          Ixx_lowertorso_obese,Iyy_lowertorso_obese,Izz_lowertorso_obese)
    
    def calculateInertiaTorso(self):
        self.calculate_upper_torso_volume()
        self.calculate_middle_torso_volume()
        self.calculate_lower_torso_volume()
        self.calculate_torso_mass()
        
        return self.uppertorso_inertia(),self.middletorso_inertia(),self.lowertorso_inertia()

    
    
class ObeseLegDissection():
    def __init__(self, thigh, thigh_circumference_base, lowerthigh_circumference_base,
                 calf_circumference_base, thigh_mass, thigh_circumference_obese, lowerthigh_circumference_obese, shank,
                 calf_circumference_obese, ankle_circumference_obese, shank_mass,
                 foot_mass, ankle_circumference_base, leg_mass_obese, ankle_height,
                 balloffoot_circumference, foot, crotch_height,Hip_circumference_obese,bmi,thighobesemass=None,
                 shankobesemass=None,footobesemass=None):
        """
        Initialize the ObeseLegDissection class with the provided parameters.
        
        :param thigh: Length of the thigh.
        :param thigh_circumference_base: Base circumference of the thigh.
        :param lowerthigh_circumference_base: Base circumference of the lower thigh.
        :param calf_circumference_base: Base circumference of the calf.
        :param thigh_mass: Base mass of the thigh.
        :param thigh_circumference_obese: Circumference of the obese thigh.
        :param shank: Length of the shank.
        :param calf_circumference_obese: Circumference of the obese calf.
        :param ankle_circumference_obese: Circumference of the obese ankle.
        :param shank_mass: Base mass of the shank.
        :param foot_mass: Base mass of the foot.
        :param ankle_circumference_base: Base circumference of the ankle.
        :param leg_mass_obese: Total mass of the obese leg.
        :param ankle_height: Height of the ankle.
        :param balloffoot_circumference: Circumference of the ball of the foot.
        :param foot: Length of the foot.
        :param crotch_height: Height of the crotch.
        """
        # Assigning all parameters to instance variables
        self.thigh = thigh
        self.thigh_circumference_base = thigh_circumference_base
        self.lowerthigh_circumference_base = lowerthigh_circumference_base
        self.calf_circumference_base = calf_circumference_base
        self.thigh_mass = thigh_mass
        self.thigh_circumference_obese = thigh_circumference_obese
        self.lowerthigh_circumference_obese = lowerthigh_circumference_obese
        self.shank = shank
        self.calf_circumference_obese = calf_circumference_obese
        self.ankle_circumference_obese = ankle_circumference_obese
        self.shank_mass = shank_mass
        self.foot_mass = foot_mass
        self.ankle_circumference_base = ankle_circumference_base
        self.leg_mass_obese = leg_mass_obese
        self.ankle_height = ankle_height
        self.balloffoot_circumference = balloffoot_circumference
        self.foot = foot
        self.crotch_height = crotch_height
        self.Hip_circumference_obese=Hip_circumference_obese
        self.thighobesemass=thighobesemass
        self.shankobesemass=shankobesemass
        self.footobesemass=footobesemass
        self.bmi=bmi

    def calculate_thigh_volume(self):
        """
        Calculate the volume of the thigh segment for both base and obese conditions.
        """
        # Length for hip ~ crotch
        self.crotch = self.ankle_height + self.shank + self.thigh - self.crotch_height

        # Base thigh volume (upper part as half cone and lower part as frustum)
        r1 = self.thigh_circumference_base / (2 * np.pi)  # radius at one end
        r2 = self.lowerthigh_circumference_base / (2 * np.pi)  # radius at other end
        h2 = self.thigh - self.crotch  # height of the lower part of the thigh
        
        volume1 = (np.pi * (r1)**2 * self.crotch) / 3  # Volume of biased cone
        volume2 = (1/3) * np.pi * h2 * (r1**2 + r2**2 + r1*r2)  # Volume of the frustum
        volume_thigh_base = volume1 + volume2

        # Obese thigh volume (upper part as half cone and lower part as frustum)
        r1 = self.thigh_circumference_obese / (2 * np.pi)
        r2 = self.lowerthigh_circumference_obese / (2 * np.pi)
        
        self.volume_thigh_obese_upper = (np.pi * (r1)**2 * self.crotch) / 3
        self.volume_thigh_obese_lower = (1/3) * np.pi * h2 * (r1**2 + r2**2 + r1*r2)
        self.volume_thigh_obese = self.volume_thigh_obese_upper + self.volume_thigh_obese_lower
        self.volumechange_thigh = self.volume_thigh_obese - volume_thigh_base


    
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

    def calculate_shank_volume(self):
        """
        Calculate the volume of the shank segment for both base and obese conditions.
        """
        # Obese shank volume
        r1 = self.calf_circumference_obese / (2 * np.pi)  # radius at one end
        r2 = self.ankle_circumference_obese / (2 * np.pi)  # radius at other end
        self.volume_shank_obese = (1/3) * np.pi * self.shank * (r1**2 + r2**2 + r1*r2)

        # Base shank volume
        r1 = self.calf_circumference_base / (2 * np.pi)
        r2 = self.ankle_circumference_base / (2 * np.pi)
        volume_shank_base = (1/3) * np.pi * self.shank * (r1**2 + r2**2 + r1*r2)

        # Calculate volume change
        self.volumechange_shank = self.volume_shank_obese - volume_shank_base

    def calculate_leg_mass(self):
        """
        Calculate the mass of each segment of the leg for the obese condition.
        """
        leg_mass_base = self.foot_mass + self.thigh_mass + self.shank_mass
        total_volumechange_leg = self.volumechange_thigh + self.volumechange_shank
        total_masschange = self.leg_mass_obese - leg_mass_base

        # Distribute the mass changes proportionally to volume changes
        if self.thighobesemass==None:
            self.thigh_mass_obese = self.thigh_mass + total_masschange * (self.volumechange_thigh / total_volumechange_leg)
            self.shank_mass_obese = self.shank_mass + total_masschange * (self.volumechange_shank / total_volumechange_leg)
            self.foot_mass_obese = self.foot_mass
        else:
            self.thigh_mass_obese =self.thighobesemass
            self.shank_mass_obese =self.shankobesemass
            self.foot_mass_obese=self.footobesemass

    def calculate_thigh_inertia(self):
        """
        Calculate the moment of inertia of the thigh for the obese condition.
        """
        # Frustum parameters for obese thigh
        r1 = self.thigh_circumference_obese / (2 * np.pi)
        R1= r1
        r2 = self.lowerthigh_circumference_obese / (2 * np.pi)
        R2= r2
        mass_upper = self.thigh_mass_obese * (self.volume_thigh_obese_upper / self.volume_thigh_obese)
        mass_lower = self.thigh_mass_obese * (self.volume_thigh_obese_lower / self.volume_thigh_obese)
        h2 = self.thigh - self.crotch
        density = self.thigh_mass_obese / self.volume_thigh_obese

        # Calculate centers of mass for upper and lower parts of the thigh
        center_of_mass_thigh_upper = self.crotch *(3/4)
        center_of_mass_thigh_lower = calculate_center_of_mass(h2, r1, R1, r2, R2)
        d1_z=(r1)*(0.25)
        # Calculate moments of inertia for upper and lower parts of the thigh
        
        Ixx_upperthigh, Iyy_upperthigh, Izz_upperthigh = elliptical_cone_inertia(R2, r2, self.crotch, mass_upper)
        # Inertia of biased cone: Implements the Parallel Axis Theorem for adjusting inertia when the COM is shifted.
        Ixx_upperthigh += (mass_upper * d1_z**2)
        Iyy_upperthigh += (mass_upper * d1_z**2)

        Ixx_lowerthigh, Iyy_lowerthigh, Izz_lowerthigh = frustum_inertia(r1, R1, r2, R2, density, h2)
        
        # Adjust moments of inertia for the center of mass shift
        # Combined Inertia Properties (crotch~knee)

        com_y_upper= center_of_mass_thigh_upper 
        com_z_upper= (r1)*(0.25)+r1

        com_y_lower= center_of_mass_thigh_lower 
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


        result = self.combine_segments(segment_upper, segment_lower)

        thigh_mass = result['mass']
        center_of_mass_thigh_obese_X = result['com'][0] 
        center_of_mass_thigh_obese_Y = (result['com'][1]-self.crotch)*-1
        center_of_mass_thigh_obese_Z = result['com'][2]-r1
        Ixx_thigh_obese = result['inertia'][0, 0]
        Iyy_thigh_obese = result['inertia'][1, 1]
        Izz_thigh_obese = result['inertia'][2, 2]
        
        return Thigh(self.thigh,self.thigh_mass_obese,self.thigh_circumference_obese,self.volume_thigh_obese,
                     center_of_mass_thigh_obese_X,center_of_mass_thigh_obese_Y,center_of_mass_thigh_obese_Z,
                     Ixx_thigh_obese,Iyy_thigh_obese,Izz_thigh_obese)
        
        

    def calculate_shank_inertia(self):
        """
        Calculate the moment of inertia of the shank for the obese condition.
        """
        r1 = self.calf_circumference_obese / (2 * np.pi)
        R1=r1
        r2 = self.ankle_circumference_obese / (2 * np.pi)
        R2=r2
        density = self.shank_mass_obese / self.volume_shank_obese

        # Calculate center of mass for the shank
        center_of_mass_shank_Y = calculate_center_of_mass(self.shank , r1, R1, r2, R2)*-1
        center_of_mass_shank_X =0
        center_of_mass_shank_Z =0

        # Calculate moments of inertia for the shank
        Ixx_shank_obese, Iyy_shank_obese, Izz_shank_obese = frustum_inertia(r1, R1, r2, R2, density, self.shank)

        return Shank(self.shank,self.shank_mass_obese,self.calf_circumference_obese,self.volume_shank_obese,
                     center_of_mass_shank_X,center_of_mass_shank_Y,center_of_mass_shank_Z,
                     Ixx_shank_obese, Iyy_shank_obese, Izz_shank_obese)

    def calculate_foot_inertia(self):
        """
        Calculate the moment of inertia of the foot for the obese condition.
        """
        r1 = self.ankle_height / 2
        R1=r1
        r2 = self.balloffoot_circumference / (2 * np.pi)
        R2=r2
        
        # Calculate volume and density of the foot
        volume_foot = (1/3) * np.pi * self.foot * (r1**2 + r2**2 + r1*r2)
        density = self.foot_mass_obese / volume_foot

        # Calculate center of mass for the foot
        center_of_mass_foot_X = calculate_center_of_mass(self.foot, r1, R1, r2, R2)-(self.foot/2)
        center_of_mass_foot_Y = r1*-1
        center_of_mass_foot_Z = 0

        # Calculate moments of inertia for the foot
        Ixx_foot_obese, Iyy_foot_obese, Izz_foot_obese =  frustum_inertia(r1, R1, r2, R2, density, self.foot)
        Ixx_foot_obese= Iyy_foot_obese
        Iyy_foot_obese= Izz_foot_obese
        return Foot(self.foot,self.foot_mass_obese,None,volume_foot,center_of_mass_foot_X,
                    center_of_mass_foot_Y,center_of_mass_foot_Z,
                    Ixx_foot_obese, Iyy_foot_obese, Izz_foot_obese)
    
    def calculateInertiaLeg(self):
        """
        Calculate the inertia of the entire leg, including thigh, shank, and foot.
        """
        # Calculate volume and mass for each segment
        self.calculate_thigh_volume()
        self.calculate_shank_volume()
        self.calculate_leg_mass()

        # Return the calculated inertia for thigh, shank, and foot
        return self.calculate_thigh_inertia(), self.calculate_shank_inertia(), self.calculate_foot_inertia()



class ObeseArm:
    def __init__(self, upperarm, biceps_circumference_base, forearm_circumference_base, 
                 upperarm_mass, forearm_circumference_obese, forearm, wrist_circumference_base,
                 forearm_mass, hand_mass, wrist_circumference_obese, arm_mass_obese,
                 biceps_circumference_obese, hand_length,upperarmmassobese=None,forearmmassobese=None,handmassobese=None):
        """
        Initialize the ObeseArm class with the given parameters.

        :param upperarm: Length of the upper arm.
        :param biceps_circumference_base: Base biceps circumference.
        :param forearm_circumference_base: Base forearm circumference.
        :param upperarm_mass: Mass of the upper arm.
        :param forearm_circumference_obese: Obese forearm circumference.
        :param forearm: Length of the forearm.
        :param wrist_circumference_base: Base wrist circumference.
        :param forearm_mass: Mass of the forearm.
        :param hand_mass: Mass of the hand.
        :param wrist_circumference_obese: Obese wrist circumference.
        :param arm_mass_obese: Obese total arm mass.
        :param biceps_circumference_obese: Obese biceps circumference.
        :param hand_length: Length of the hand.
        """
        # Initialize instance variables
        self.upperarm = upperarm
        self.biceps_circumference_base = biceps_circumference_base
        self.forearm_circumference_base = forearm_circumference_base
        self.upperarm_mass = upperarm_mass
        self.forearm_circumference_obese = forearm_circumference_obese
        self.forearm = forearm
        self.wrist_circumference_base = wrist_circumference_base
        self.forearm_mass = forearm_mass
        self.hand_mass = hand_mass
        self.wrist_circumference_obese = wrist_circumference_obese
        self.arm_mass_obese = arm_mass_obese
        self.biceps_circumference_obese = biceps_circumference_obese
        self.hand_length = hand_length
        self.upperarmmassobese=upperarmmassobese
        self.forearmmassobese=forearmmassobese
        self.handmassobese=handmassobese

    def calculate_upperarm_volume(self):
        """
        Calculate the volume of the upper arm for both base and obese conditions.
        """
        # Base volume calculation for upper arm (as a frustum)
        r1 = self.biceps_circumference_base / (2 * np.pi)  # Radius at one end
        r2 = self.forearm_circumference_base / (2 * np.pi)  # Radius at the other end
        volume_upperarm_base = (1/3) * np.pi * self.upperarm * (r1**2 + r2**2 + r1 * r2)

        # Obese volume calculation for upper arm
        r1 = self.biceps_circumference_obese / (2 * np.pi)
        r2 = self.forearm_circumference_obese / (2 * np.pi)
        self.volume_upperarm_obese = (1/3) * np.pi * self.upperarm * (r1**2 + r2**2 + r1 * r2)
        self.volumechange_upperarm = self.volume_upperarm_obese - volume_upperarm_base

    def calculate_forearm_volume(self):
        """
        Calculate the volume of the forearm for both base and obese conditions.
        """
        # Base volume calculation for forearm (as a frustum)
        r1 = self.forearm_circumference_base / (2 * np.pi)
        r2 = self.wrist_circumference_base / (2 * np.pi)
        volume_forearm_base = (1/3) * np.pi * self.forearm * (r1**2 + r2**2 + r1 * r2)

        # Obese volume calculation for forearm
        r1 = self.forearm_circumference_obese / (2 * np.pi)
        r2 = self.wrist_circumference_obese / (2 * np.pi)
        self.volume_forearm_obese = (1/3) * np.pi * self.forearm * (r1**2 + r2**2 + r1 * r2)
        self.volumechange_forearm = self.volume_forearm_obese - volume_forearm_base

    def calculate_arm_mass(self):
        """
        Calculate the mass distribution of the arm for both base and obese conditions.
        """
        arm_mass_base = self.hand_mass + self.upperarm_mass + self.forearm_mass
        total_volume_change = self.volumechange_upperarm + self.volumechange_forearm
        total_mass_change = self.arm_mass_obese - arm_mass_base

        # Adjust the masses for upper arm, forearm, and hand
        if self.upperarmmassobese==None:
            self.upperarm_mass_obese = self.upperarm_mass + total_mass_change * (self.volumechange_upperarm / total_volume_change)
            self.forearm_mass_obese = self.forearm_mass + total_mass_change * (self.volumechange_forearm / total_volume_change)
            self.hand_mass_obese = self.hand_mass
        else:
            self.upperarm_mass_obese=self.upperarmmassobese
            self.forearm_mass_obese=self.forearmmassobese
            self.hand_mass_obese=self.handmassobese

    def calculateupperarmInertia(self):
        """
        Calculate the inertia of the upper arm.
        :return: A list of inertia parameters for the upper arm.
        """
        # Frustum parameters for upper arm
        r1 = self.biceps_circumference_obese / (2 * np.pi)
        R1= r1
        r2 = self.forearm_circumference_obese / (2 * np.pi)
        R2= r2
        # Calculate density and center of mass for upper arm
        density = self.upperarm_mass_obese / self.volume_upperarm_obese
        center_of_mass_upperarm_Y = calculate_center_of_mass(self.upperarm, r1, R1, r2, R2)*-1
        center_of_mass_upperarm_X = 0
        center_of_mass_upperarm_Z = 0

        # Calculate moments of inertia
        Ixx_upperarm_obese,Iyy_upperarm_obese, Izz_upperarm_obese = frustum_inertia(r1, R1, r2, R2, density, self.upperarm)

        return UpperArm(self.upperarm,self.upperarm_mass_obese,self.biceps_circumference_obese,self.volume_upperarm_obese,
                        center_of_mass_upperarm_X,center_of_mass_upperarm_Y,center_of_mass_upperarm_Z,
                         Ixx_upperarm_obese,Iyy_upperarm_obese, Izz_upperarm_obese)

    def calculateforearmInertia(self):
        """
        Calculate the inertia of the forearm.
        :return: A list of inertia parameters for the forearm.
        """
        # Frustum parameters for forearm
        r1 = self.forearm_circumference_obese / (2 * np.pi)
        R1= r1
        r2 = self.wrist_circumference_obese / (2 * np.pi)
        R2= r2
        density = self.forearm_mass_obese / self.volume_forearm_obese

        # Calculate center of mass for forearm
        center_of_mass_forearm_Y = calculate_center_of_mass(self.forearm, r1, R1, r2, R2)*-1
        center_of_mass_forearm_X = 0
        center_of_mass_forearm_Z = 0 

        # Calculate moments of inertia
        Ixx_forearm_obese, Iyy_forearm_obese, Izz_forearm_obese = frustum_inertia(r1, R1, r2, R2, density, self.forearm)

        return Forearm(self.forearm,self.forearm_mass_obese,None,self.volume_forearm_obese,
                       center_of_mass_forearm_X,center_of_mass_forearm_Y,center_of_mass_forearm_Z,
                       Ixx_forearm_obese, Iyy_forearm_obese, Izz_forearm_obese)

    def calculatehandInertia(self):
        """
        Calculate the inertia of the hand.
        :return: A list of inertia parameters for the hand.
        """
         # Calculate characteristic length for the hand (approximation)
        r = self.hand_length/4 # Hand length divided by 4 to approximate radius of equivalent sphere
        R = r
        h= R
        m = self.hand_mass # Mass of the hand
        # Calculate volume of the ellipsoid representing the hand
        volume_hand = (4 / 3) * np.pi * r**3
        
        # Calculate center of mass for the hand (approximated at the center)
        center_of_mass_hand_Y =  0
        center_of_mass_hand_X =  0
        center_of_mass_hand_Z =  0
    
        # Calculate moments of inertia (Ixx, Iyy, Izz) for the hand treated as a sphere
        Ixx_hand, Iyy_hand, Izz_hand = ellipsoid_inertia (R, r, h, m)

        return Hand(self.hand_length,self.hand_mass_obese,None,volume_hand,
                    center_of_mass_hand_X,center_of_mass_hand_Y,center_of_mass_hand_Z,
                    Ixx_hand, Iyy_hand, Izz_hand)

    def calculateInertiaArm(self):
        """
        Calculate the inertia of the entire arm (upper arm, forearm, and hand).
        :return: A tuple containing the inertia values for the upper arm, forearm, and hand.
        """
        # Calculate the volumes of the upper arm and forearm
        self.calculate_upperarm_volume()
        self.calculate_forearm_volume()

        # Calculate the arm mass distribution
        self.calculate_arm_mass()

        # Calculate and return the inertia values for the entire arm
        return self.calculateupperarmInertia(), self.calculateforearmInertia(), self.calculatehandInertia()

        
 
        
    
        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

    
    
        