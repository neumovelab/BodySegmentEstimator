import pandas as pd
import numpy as np
from .BodyObjects import *

def check_data_format_and_bmi(data):
    height=data.get('height')
    weight=data.get('weight')
    sex=data.get('sex')
    if height==None or weight==None or sex==None:
        raise ValueError("Height, Weight and Sex are required")
    bmi = calculate_bmi(weight, height)
    return bmi

def calculate_new_mass(m0,v0,v1,mtotal,vtotal0,vtotal):
    """
        Returns the updated mass.
        Parameters:
        - m0 : mass value from baseline.
        - v0: volume value from baseline.
        - v1: volume obtained with custom measure
        - mtotal: total moss of the body
        - vtotal0: total volume of the body (baseline)
        - vtotal: total volume of the body with custom measure
        Returns:
        - new mass.
    """
    mass=v1 * ((m0/v0) / (mtotal/vtotal0) * mtotal/vtotal)
    return mass

def get_single_value(df, segment, column):
    # Get a single value from the dataframe based on the segment and column
    value = df.loc[df['Segment'] == segment, column].values
    if value.size == 0:
        # Raise an error if the segment is not found in the dataframe
        raise ValueError(f"Segment '{segment}' not found in the DataFrame.")
    return value[0]

def modify_single_value(df, segment, column, new_value):
    if segment not in df['Segment'].values:
        # Raise an error if the segment is not found in the dataframe
        raise ValueError(f"Segment '{segment}' not found in the DataFrame.")
    # Update the value in the specified column for the given segment
    df.loc[df['Segment'] == segment, column] = new_value
    return df

def update_segment_value(df, segment, new_value):
    """
    Updates the value of a specific segment in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing data with 'Segment' and 'Value' columns.
        segment (str): The name of the segment to update.
        new_value (float): The new value to assign to the segment.

    Returns:
        pd.DataFrame: The updated DataFrame.
    """
    if segment in df['Segment'].values:
        df.loc[df['Segment'] == segment, 'Value'] = new_value
    else:
        print(f"Segment '{segment}' not found in the DataFrame.")
    return df
    

# Function to adjust segment masses based on custom volume adjustments without modifying input dataframes
def adjust_mass_from_custom(weightdf,basemodel=Segments(), usermodel=Segments()):
    """
    Adjusts segment masses based on volume adjustments.
    
    Parameters:
    - weightdf: The target weight to adjust the masses to (in kg).
    - basemodel: Segments Object containing the base mass and volume information.
    - usermodel: Segments Object containing custom volume information.
    Returns:
    - weight dataframe: DataFrame with adjusted segment masses.
    """
    # Calculate the total mass of the custom model
    mtotal = usermodel.calculate_total_mass()
    
    # Calculate the total volume of the base and custom model
    vtotal0 = basemodel.calculate_total_volume()
    vtotal = usermodel.calculate_total_volume()
    
    # Create a copy of dfcustom to avoid modifying the original dataframe
    finaldf = weightdf.copy()
    
    # List of body segments to adjust
    segments = ['Head', 'thigh', 'shank', 'foot', 'upper_trunk', 'middle_trunk', 'lower_trunk', 'upper_arm', 'forearm', 'hand']
    finaldf=update_segment_value(finaldf, 'Head', calculate_new_mass(basemodel.Head.mass, basemodel.Head.volume, usermodel.Head.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'thigh', calculate_new_mass(basemodel.Thigh.mass, basemodel.Thigh.volume, usermodel.Thigh.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'shank', calculate_new_mass(basemodel.Shank.mass, basemodel.Shank.volume, usermodel.Shank.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'foot', calculate_new_mass(basemodel.Foot.mass, basemodel.Foot.volume, usermodel.Foot.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'upper_trunk', calculate_new_mass(basemodel.UpperTorso.mass, basemodel.UpperTorso.volume, usermodel.UpperTorso.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'middle_trunk', calculate_new_mass(basemodel.MiddleTorso.mass, basemodel.MiddleTorso.volume, usermodel.MiddleTorso.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'lower_trunk', calculate_new_mass(basemodel.LowerTorso.mass, basemodel.LowerTorso.volume, usermodel.LowerTorso.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'upper_arm', calculate_new_mass(basemodel.UpperArm.mass, basemodel.UpperArm.volume, usermodel.UpperArm.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'forearm',  calculate_new_mass(basemodel.Forearm.mass, basemodel.Forearm.volume, usermodel.Forearm.volume, mtotal, vtotal0, vtotal))
    finaldf=update_segment_value(finaldf, 'hand', calculate_new_mass(basemodel.Hand.mass, basemodel.Hand.volume, usermodel.Hand.volume, mtotal, vtotal0, vtotal))
    
    return finaldf

def adjust_mass_from_custom_obese(basemodel=Segments(), usermodel=Segments()):
    """
    Adjusts segment masses based on volume adjustments.
    
    Parameters:
    - basemodel: Segments Object containing the base mass and volume information.
    - usermodel: Segments Object containing custom volume information.
    Returns:
    - user model: Segments Objects with adjusted segment masses.
    """
    mtotal = usermodel.calculate_total_mass()
    
    # Calculate the total volume of the base and custom model
    vtotal0 = basemodel.calculate_total_volume()
    vtotal = usermodel.calculate_total_volume()
    
    usermodel.Head.mass=calculate_new_mass(basemodel.Head.mass, basemodel.Head.volume, usermodel.Head.volume, mtotal, vtotal0, vtotal)
    usermodel.Thigh.mass=calculate_new_mass(basemodel.Thigh.mass, basemodel.Thigh.volume, usermodel.Thigh.volume, mtotal, vtotal0, vtotal)
    usermodel.Shank.mass=calculate_new_mass(basemodel.Shank.mass, basemodel.Shank.volume, usermodel.Shank.volume, mtotal, vtotal0, vtotal)
    usermodel.Foot.mass=calculate_new_mass(basemodel.Foot.mass, basemodel.Foot.volume, usermodel.Foot.volume, mtotal, vtotal0, vtotal)
    usermodel.UpperTorso.mass=calculate_new_mass(basemodel.UpperTorso.mass, basemodel.UpperTorso.volume, usermodel.UpperTorso.volume, mtotal, vtotal0, vtotal)
    usermodel.MiddleTorso.mass=calculate_new_mass(basemodel.MiddleTorso.mass, basemodel.MiddleTorso.volume, usermodel.MiddleTorso.volume, mtotal, vtotal0, vtotal)
    usermodel.LowerTorso.mass=calculate_new_mass(basemodel.LowerTorso.mass, basemodel.LowerTorso.volume, usermodel.LowerTorso.volume, mtotal, vtotal0, vtotal)
    usermodel.UpperArm.mass=calculate_new_mass(basemodel.UpperArm.mass, basemodel.UpperArm.volume, usermodel.UpperArm.volume, mtotal, vtotal0, vtotal)
    usermodel.Forearm.mass=calculate_new_mass(basemodel.Forearm.mass, basemodel.Forearm.volume, usermodel.Forearm.volume, mtotal, vtotal0, vtotal)
    usermodel.Hand.mass=calculate_new_mass(basemodel.Hand.mass, basemodel.Hand.volume, usermodel.Hand.volume, mtotal, vtotal0, vtotal)
    return usermodel
    


def check_hip_waist(data,df,bmi):
    
    if data.get('hip_circumference')==None:
        data['hip_circumference'],_ =get_hip_waist_advanced(bmi, df)
    
    if data.get('waist_circumference')==None:
        _,data['waist_circumference']=get_hip_waist_advanced(bmi, df)
        
    if bmi>=30:
       hip_circ=data.get('hip_circumference')
       waist_circ=data.get('waist_circumference')
       if  hip_circ==np.nan or waist_circ==np.nan:
           raise ValueError("Obese case requires waist and hip circumference")
    return data
         

# Definizione della funzione avanzata
def get_hip_waist_advanced(bmi, df, bin_size=1, max_expansion=5):
    """
        Returns the hip and waist values based on the given BMI.
        If there is no data in the bin, it expands the search range until data is found.
        
        Parameters:
        - bmi (float): BMI value of interest.
        - df (pd.DataFrame): DataFrame containing the columns 'bmi', 'hip', 'waist'.
        - bin_size (float): Size of the BMI bin. Default is 1.
        - max_expansion (int): Maximum number of bins to expand if the initial bin is empty.
        
        Returns:
        - tuple: (hip, waist) estimated values.
    """

    for expansion in range(max_expansion + 1):
        lower = bmi - (bin_size / 2) - expansion * bin_size
        upper = bmi + (bin_size / 2) + expansion * bin_size
        subset = df[(df['bmi'] >= lower) & (df['bmi'] < upper)]
        
        if not subset.empty:
            # Campiona casualmente una riga dal subset
            sampled = subset.sample(n=1, random_state=42)
            hip = sampled['hip'].values[0]
            waist = sampled['waist'].values[0]
            return hip, waist

    # Se nessun dato trovato dopo espansione massima, usa interpolazione
    # Trova i BMI più vicini inferiori e superiori con dati
    lower_df = df[df['bmi'] < bmi].sort_values('bmi', ascending=False)
    upper_df = df[df['bmi'] > bmi].sort_values('bmi', ascending=True)
    
    if not lower_df.empty and not upper_df.empty:
        lower_bmi = lower_df.iloc[0]['bmi']
        upper_bmi = upper_df.iloc[0]['bmi']
        
        # Calcola i pesi per l'interpolazione
        weight = (bmi - lower_bmi) / (upper_bmi - lower_bmi)
        
        # Interpolazione lineare per hip e waist
        hip = lower_df.iloc[0]['hip'] + weight * (upper_df.iloc[0]['hip'] - lower_df.iloc[0]['hip'])
        waist = lower_df.iloc[0]['waist'] + weight * (upper_df.iloc[0]['waist'] - lower_df.iloc[0]['waist'])
        return hip, waist
    elif not lower_df.empty:
        # Se solo i BMI inferiori sono disponibili
        return lower_df.iloc[0]['hip'], lower_df.iloc[0]['waist']
    elif not upper_df.empty:
        # Se solo i BMI superiori sono disponibili
        return upper_df.iloc[0]['hip'], upper_df.iloc[0]['waist']
    else:
        # Se non ci sono dati nel DataFrame
        return np.nan, np.nan
      
        

def calculate_bmi(weight_kg, height_cm):
    # Convert height from centimeters to meters
    height_m = height_cm/100
    
    # Calculate BMI
    bmi = weight_kg/(height_m**2)
    
    # Return the BMI, rounded to 2 decimal places
    return round(bmi, 2)

def calculate_weight_for_bmi(height_cm, target_bmi=29):
    # Convert height from centimeters to meters
    height_m = height_cm/100
    
    # Calculate the weight needed to achieve the target BMI
    weight_kg = target_bmi * (height_m ** 2)
    
    # Return the weight, rounded to 2 decimal places
    return round(weight_kg, 2)

def convert_units(data):
    """
    Converts all length-related measurements in the dictionary to centimeters.
    If the unit system is 'SI', converts from meters to centimeters.
    If the unit system is 'USCS', converts from inches to centimeters.
    Weight remains in kilograms if it's SI, otherwise converts from pounds to kilograms.

    Parameters:
    - data (dict): The dictionary containing unit_measure and various body measurements.

    Returns:
    - dict: The updated dictionary with converted measurements.
    """
    
    # Conversion factors
    meter_to_cm = 100  # For SI (meters to centimeters)
    inch_to_cm = 2.54  # For USCS (inches to centimeters)
    pound_to_kg = 0.453592  # For USCS (pounds to kilograms)
    
    # List of keys that represent lengths and should be converted
    length_keys = [
        'height', 'head', 'upper_torso', 'middle_torso', 'lower_torso', 
        'thigh', 'shank', 'foot', 'ankle', 'upperarm', 'forearm', 'hand',
        'head_circumference', 'headbreadth', 'chestdepth', 'biacromialbreadth',
        'neck_base_circumference', 'shoulder_circumference', 'shoulderwaistlen',
        'chest_circumference', 'hip_circumference', 'waist_circumference',
        'waistbreadth', 'waistdepth', 'hipbreadth', 'buttockdepth', 'crotchheight',
        'thigh_circumference', 'lower_thigh_circumference', 'calf_circumference',
        'ankle_circumference', 'balloffoot_circumference', 'buttock_circumference',
        'bicep_circumference', 'neck_circumference', 'forearm_circumference',
        'wrist_circumference', 'handbreadth'
    ]
    
    # Check if the unit system is 'SI' (metric) or 'USCS' (imperial)
    unit_system = data.get('unit_measure').lower()

    # Conversion based on the unit system
    if unit_system == 'si':
        # Convert lengths from meters to centimeters
        for key in length_keys:
            if key in data:
                data[key] = data[key] * meter_to_cm
        # Weight remains in kilograms, no change
    elif unit_system in ['uscs', 'imperial', 'us']:
        # Convert lengths from inches to centimeters
        for key in length_keys:
            if key in data:
                data[key] = data[key] * inch_to_cm
        # Convert weight from pounds to kilograms
        if 'weight' in data:
            data['weight'] = data['weight'] * pound_to_kg
    else:
        raise ValueError("Unsupported unit system. Use 'SI' or 'USCS'.")
    return data





def percent_segments(df_mass, mass):
    required_segments = ['thigh', 'shank', 'foot', 'upper_trunk', 'middle_trunk', 'lower_trunk', 'upper_arm', 'forearm', 'hand']
    
    # Verify all segments are in required segments
    if not all(segment in df_mass['segment'].values for segment in required_segments):
        raise ValueError("Required segments missing")

    # Calcolo delle somme delle masse per i diversi segmenti del corpo
    leg_total = df_mass[df_mass['segment'].isin(['thigh', 'shank', 'foot'])]['value'].sum()
    trunk_total = df_mass[df_mass['segment'].isin(['upper_trunk', 'middle_trunk', 'lower_trunk'])]['value'].sum()
    arm_total = df_mass[df_mass['segment'].isin(['upper_arm', 'forearm', 'hand'])]['value'].sum()
    
    # Creazione del dizionario per le proporzioni
    proportion = {'leg': {}, 'trunk': {}, 'arm': {}}
    
    # Calcolo delle proporzioni per il tronco
    if trunk_total != 0:
        proportion['trunk']['upper_trunk'] = (df_mass[df_mass['segment'] == 'upper_trunk']['value'].values[0] / trunk_total) * 100
        proportion['trunk']['middle_trunk'] = (df_mass[df_mass['segment'] == 'middle_trunk']['value'].values[0] / trunk_total) * 100
        proportion['trunk']['lower_trunk'] = (df_mass[df_mass['segment'] == 'lower_trunk']['value'].values[0] / trunk_total) * 100
    else:
        proportion['trunk']['upper_trunk'] = proportion['trunk']['middle_trunk'] = proportion['trunk']['lower_trunk'] = 0
    
    # Calcolo delle proporzioni per il braccio
    if arm_total != 0:
        proportion['arm']['upper_arm'] = (df_mass[df_mass['segment'] == 'upper_arm']['value'].values[0] / arm_total) * 100
        proportion['arm']['forearm'] = (df_mass[df_mass['segment'] == 'forearm']['value'].values[0] / arm_total) * 100
        proportion['arm']['hand'] = (df_mass[df_mass['segment'] == 'hand']['value'].values[0] / arm_total) * 100
    else:
        proportion['arm']['upper_arm'] = proportion['arm']['forearm'] = proportion['arm']['hand'] = 0
    
    # Calcolo delle proporzioni per la gamba
    if leg_total != 0:
        proportion['leg']['thigh'] = (df_mass[df_mass['segment'] == 'thigh']['value'].values[0] / leg_total) * 100
        proportion['leg']['shank'] = (df_mass[df_mass['segment'] == 'shank']['value'].values[0] / leg_total) * 100
        proportion['leg']['foot'] = (df_mass[df_mass['segment'] == 'foot']['value'].values[0] / leg_total) * 100
    else:
        proportion['leg']['thigh'] = proportion['leg']['shank'] = proportion['leg']['foot'] = 0
    
    return proportion 


def divide_segments(proportion_dict, df_values):
    # Creare una lista per memorizzare i nuovi dati
    new_data = []

    # Loop attraverso ogni riga del DataFrame originale
    for index, row in df_values.iterrows():
        segment = row['Segment']
        value = row['Value']

        if segment == 'Leg':
            for sub_segment, proportion in proportion_dict['leg'].items():
                new_data.append({'Segment': sub_segment, 'Value': value * (proportion / 100)})
        elif segment == 'Arm':
            for sub_segment, proportion in proportion_dict['arm'].items():
                new_data.append({'Segment': sub_segment, 'Value': value * (proportion / 100)})
        elif segment == 'Trunk':
            for sub_segment, proportion in proportion_dict['trunk'].items():
                new_data.append({'Segment': sub_segment, 'Value': value * (proportion / 100)})
        else:  # Per 'Head' e qualsiasi altro segmento non suddiviso
            new_data.append({'Segment': segment, 'Value': value})

    # Creare un nuovo DataFrame dai nuovi dati
    new_df = pd.DataFrame(new_data)
    return new_df

def adjust_mass_values(df,w):
    segments = ['thigh', 'shank', 'foot','upper_arm', 'forearm', 'hand']
    total_mass = df['Value'].sum() + df[df['Segment'].isin(segments)]['Value'].astype(float).sum()
    df.loc[:,'Value']=df['Value']/total_mass
    df.loc[:,'Value']=df.loc[:,'Value']*w
    return df

def adjust_mass_obese(df,w):
    segments = ['Leg', 'Arm']
    total_mass = df['Value'].sum() + df[df['Segment'].isin(segments)]['Value'].astype(float).sum()
    df.loc[:,'Value']=df['Value']/total_mass
    df.loc[:,'Value']=df.loc[:,'Value']*w
    return df


def adjust_mass(w,usermodel=Segments()):
    total_mass=usermodel.calculate_total_mass()
    usermodel.Head.mass=(usermodel.Head.mass/total_mass)*w
    usermodel.UpperTorso.mass=(usermodel.UpperTorso.mass/total_mass)*w
    usermodel.MiddleTorso.mass=(usermodel.MiddleTorso.mass/total_mass)*w
    usermodel.LowerTorso.mass=(usermodel.LowerTorso.mass/total_mass)*w
    usermodel.Thigh.mass=(usermodel.Thigh.mass/total_mass)*w
    usermodel.Shank.mass=(usermodel.Shank.mass/total_mass)*w
    usermodel.Foot.mass=(usermodel.Foot.mass/total_mass)*w
    usermodel.UpperArm.mass=(usermodel.UpperArm.mass/total_mass)*w
    usermodel.Forearm.mass=(usermodel.Forearm.mass/total_mass)*w
    usermodel.Hand.mass=(usermodel.Hand.mass/total_mass)*w
    return usermodel