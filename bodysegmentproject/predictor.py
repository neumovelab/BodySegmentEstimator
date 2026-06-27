import pandas as pd

from .segment_additional import BodyAddMeasuresPredictor
from .segment_circumference import BodyCircumferencePredictor
from .segment_length import BodyLengthPredictor
from .segment_mass import BodyMassPredictor
from .utils import *
import numpy as np
from .utilsbodyinertia import *
from .utilsobeseinertia import *
from .BodyObjects import *

class HealthyBodyInertiaPredictor:
    
    def __init__(self,data,fromobese=False,weight=None):
        """
        Initialize the class with the target height, weight and sex.
        :param data: subject measures.
        :param fromobese: true if calculate baseline for obese model. Default:false
        """
        self.height = data.get('height')
        if weight==None:
            self.weight=data.get('weight')
        else:
            self.weight=weight
        self.sex= 1 if data.get('sex')== "male" else 2
        self.custom_measures=data
        self.bmi=calculate_bmi(self.weight,self.height)
        self.fromobese=fromobese

        

    # Function to calculate baseParameters values for various body segments (not from user input)
    def calculateBaseParameters(self): 
        # Predict and retrieve necessary anthropometric measures
        self.dfheight, self.heightcustom = self.predict_height()
        self.dfweight = self.predict_weight()
        self.dfcirc = self.predict_circumference()
        self.dfaddmeasures = self.predict_additional_measures()
        self.dfcircbase=self.predict_circumference_base()
        self.dfaddmeasuresbase=self.predict_additional_measures_base()
        
        # Calculate inertia parameters for different body segments
        head = self.calculate_head_inertia()
        upper_torso = self.calculate_uppertorso_inertia()
        middle_torso = self.calculate_middletrunk_inertia()
        lower_torso = self.calculate_lowertrunk_inertia()
        thigh = self.calculate_thigh_inertia()
        shank = self.calculate_shank_inertia()
        foot = self.calculate_foot_inertia()
        upperarm = self.calculate_upperarm_inertia()
        forearm = self.calculate_forearm_inertia()
        hand = self.calculate_hand_inertia()
        self.baseparameters=Segments(head,upper_torso,middle_torso,lower_torso,thigh,shank,foot,upperarm,forearm,hand)

    # Function to calculate parameters from User Input values
    def calculateParametersFromUserInput(self):
        # Calculate custom inertia parameters for different body segments
        head = self.calculate_head_inertia_custom()
        upper_torso = self.calculate_uppertorso_inertia_custom()
        middle_torso = self.calculate_middletrunk_inertia_custom()
        lower_torso = self.calculate_lowertrunk_inertia_custom()
        thigh = self.calculate_thigh_inertia_custom()
        shank = self.calculate_shank_inertia_custom()
        foot = self.calculate_foot_inertia_custom()
        upperarm = self.calculate_upperarm_inertia_custom()
        forearm = self.calculate_forearm_inertia_custom()
        hand = self.calculate_hand_inertia_custom()
        self.userinputparameters=Segments(head,upper_torso,middle_torso,lower_torso,thigh,shank,foot,upperarm,forearm,hand,self.dfheight,self.dfcirc,self.dfaddmeasures)
    
    def get_segments_properties(self):
        #Calculate base parameters
        self.calculateBaseParameters()
        #Calculate parameters from user input
        self.calculateParametersFromUserInput()
        #Update mass
        self.dfweight=adjust_mass_from_custom(self.dfweight,self.baseparameters, self.userinputparameters)
        #Calculate final model
        self.calculateParametersFromUserInput()
        return self.userinputparameters
        
    
    def calculate_circumferences(self):
        # Predict and calculate head circumference values
        self.dfcirc = self.predict_circumference()
        return self.dfcirc

    def calculate_addmeasures(self):
        # Predict and calculate additional body measures
        self.dfaddmeasures = self.predict_additional_measures()
        return self.dfaddmeasures

    def predict_height(self):
        # Create a height predictor instance and predict the adjusted height
        height_predictor = BodyLengthPredictor(self.height, self.sex, self.custom_measures)
        return height_predictor.predict_and_adjust()

    def predict_weight(self):
        # Create a weight predictor instance and predict the weight
        weight_predictor = BodyMassPredictor(self.height, self.weight, self.sex,True)
        return weight_predictor.predict()

    def predict_circumference(self):
        # Create a circumference predictor instance and predict the circumference values
        circ_predictor = BodyCircumferencePredictor(self.height, self.weight, self.sex,self.custom_measures,False)
        return circ_predictor.predict()
    
    def predict_circumference_base(self):
        # Create a circumference predictor instance and predict the circumference values
        circ_predictor = BodyCircumferencePredictor(self.height, self.weight, self.sex,None,True)
        return circ_predictor.predict()

    def predict_additional_measures(self):
        # Create an additional measures predictor instance and predict additional measures
        add_measures = BodyAddMeasuresPredictor(self.height, self.weight, self.sex,self.custom_measures,False)
        return add_measures.predict()
    
    def predict_additional_measures_base(self):
        # Create an additional measures predictor instance and predict additional measures
        add_measures = BodyAddMeasuresPredictor(self.height, self.weight, self.sex,None,True)
        return add_measures.predict()

    def get_single_value(self, df, segment, column):
        # Get a single value from the dataframe based on the segment and column
        value = df.loc[df['Segment'] == segment, column].values
        if value.size == 0:
            # Raise an error if the segment is not found in the dataframe
            raise ValueError(f"Segment '{segment}' not found in the DataFrame.")
        return value[0]
    
    def calculate_head_inertia(self):
        # Get head circumference from the dataframe
        head_circ = self.get_single_value(self.dfcircbase, 'head', 'Value')
        # Get head length from the dataframe
        head_len = self.get_single_value(self.dfheight, 'head', 'Value')
        # Get head weight from the dataframe
        head_weight = self.get_single_value(self.dfweight, 'Head', 'Value')
        # Get head breadth from the dataframe
        head_breadth = self.get_single_value(self.dfaddmeasuresbase, 'headbreadth', 'Value')

        # Calculate and return head parameters using the head_parameters function
        return head_parameters(head_circ, head_len, head_weight, head_breadth)

    def calculate_head_inertia_custom(self):
        """
        Calculate head inertia using custom or default measurements.
        """
        # Get head circumference from custom measures if available and 'fromobese' is False, otherwise from the dataframe
        if not self.fromobese:
            head_circ = self.custom_measures.get('head_circumference') or self.get_single_value(self.dfcirc, 'head', 'Value')
        else:
            head_circ = self.get_single_value(self.dfcircbase, 'head', 'Value')
        
        # Get head length from the custom height dataframe
        head_len = self.get_single_value(self.heightcustom, 'head', 'Value')
        
        # Get head weight from the dataframe
        head_weight = self.get_single_value(self.dfweight, 'Head', 'Value')
        
        # Get head breadth from custom measures if available and 'fromobese' is False, otherwise from the dataframe
        if not self.fromobese:
            head_breadth = self.custom_measures.get('headbreadth') or self.get_single_value(self.dfaddmeasures, 'headbreadth', 'Value')
        else:
            head_breadth = self.get_single_value(self.dfaddmeasuresbase, 'headbreadth', 'Value')

        # Calculate and return head parameters using the head_parameters function
        return head_parameters(head_circ, head_len, head_weight, head_breadth)
        
    
    # Function to calculate upper torso inertia using predefined data
    def calculate_uppertorso_inertia(self):
        # Retrieve mass value for upper trunk
        mass = self.get_single_value(self.dfweight, 'upper_trunk', 'Value')
        # Retrieve circumference of neck base
        neckbasecirc = self.get_single_value(self.dfcircbase, 'neckbase', 'Value')
        # Retrieve breadth of shoulders (biacromial breadth)
        shoulderbreadth = self.get_single_value(self.dfaddmeasuresbase, 'biacromialbreadth', "Value")
        # Retrieve chest depth value
        chestdepth = self.get_single_value(self.dfaddmeasuresbase, 'chestdepth', "Value")
        # Retrieve upper torso and middle torso height values
        uppertorso = self.get_single_value(self.dfheight, 'upper_torso', 'Value')
        middletorso = self.get_single_value(self.dfheight, 'middle_torso', 'Value')
        # Retrieve shoulder to waist length
        shoulderwaistlen = self.get_single_value(self.dfheight, 'shoulderwaistlen', 'Value')
        # Retrieve chest circumference
        chestcircumference = self.get_single_value(self.dfcircbase, 'chest', 'Value')
        # Retrieve chest breadth value
        chestbreadth = self.get_single_value(self.dfaddmeasuresbase, 'chestbreadth', 'Value')
        # Return all parameters as an uppertorsoParameters instance
        return uppertorsoParameters(mass, neckbasecirc, shoulderbreadth, chestdepth,
                                    uppertorso, middletorso, shoulderwaistlen,
                                    chestcircumference, chestbreadth)
    
    def calculate_uppertorso_inertia_custom(self):
        """
        Calculate upper torso inertia using custom or default measurements.
        """
        # Retrieve mass value for upper trunk
        mass = self.get_single_value(self.dfweight, 'upper_trunk', 'Value')
        
        # Use custom neck base circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            neckbasecirc = self.custom_measures.get('neck_base_circumference') or self.get_single_value(self.dfcirc, 'neckbase', 'Value')
        else:
            neckbasecirc = self.get_single_value(self.dfcircbase, 'neckbase', 'Value')
        
        # Use custom shoulder breadth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            shoulderbreadth = self.get_single_value(self.dfaddmeasures, 'biacromialbreadth', "Value")
        else:
            shoulderbreadth=self.custom_measures.get('shoulder-breadth') or self.get_single_value(self.dfaddmeasuresbase, 'biacromialbreadth', "Value")
        
        # Use custom chest depth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            chestdepth = self.custom_measures.get('chestdepth') or self.get_single_value(self.dfaddmeasures, 'chestdepth', "Value")
        else:
            chestdepth = self.get_single_value(self.dfaddmeasuresbase, 'chestdepth', "Value")
        
        # Retrieve upper torso and middle torso height values from custom data
        uppertorso = self.get_single_value(self.heightcustom, 'upper_torso', 'Value')
        middletorso = self.get_single_value(self.heightcustom, 'middle_torso', 'Value')
        
        # Use custom shoulder to waist length if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            shoulderwaistlen = self.custom_measures.get('shoulderwaistlen') or self.get_single_value(self.dfheight, 'shoulderwaistlen', 'Value')
        else:
            shoulderwaistlen = self.get_single_value(self.dfheight, 'shoulderwaistlen', 'Value')
        
        # Use custom chest circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            chestcircumference = self.custom_measures.get('chest_circumference') or self.get_single_value(self.dfcirc, 'chest', 'Value')
        else:
            chestcircumference = self.get_single_value(self.dfcircbase, 'chest', 'Value')
        
        # Use custom chest breadth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            chestbreadth = self.custom_measures.get('chestbreadth') or self.get_single_value(self.dfaddmeasures, 'chestbreadth', 'Value')
        else:
            chestbreadth = self.get_single_value(self.dfaddmeasuresbase, 'chestbreadth', 'Value')
        
        # Return all parameters as an uppertorsoParameters instance
        return uppertorsoParameters(mass, neckbasecirc, shoulderbreadth, chestdepth,
                                    uppertorso, middletorso, shoulderwaistlen,
                                    chestcircumference, chestbreadth)
    
    
    # Function to calculate middle trunk inertia using predefined data
    def calculate_middletrunk_inertia(self):
        # Retrieve chest circumference value
        chestcircumference = self.get_single_value(self.dfcircbase, 'chest', 'Value')
        # Retrieve chest depth value
        chestdepth = self.get_single_value(self.dfaddmeasuresbase, 'chestdepth', "Value")
        # Retrieve chest breadth value
        chestbreadth = self.get_single_value(self.dfaddmeasuresbase, 'chestbreadth', 'Value')
        # Retrieve waist circumference value
        waistcirc = self.get_single_value(self.dfcircbase, 'waist', 'Value')
        # Retrieve waist breadth value
        waistbreadth = self.get_single_value(self.dfaddmeasuresbase, 'waistbreadth', 'Value')
        # Retrieve waist depth value
        waistdepth = self.get_single_value(self.dfaddmeasuresbase, 'waistdepth', 'Value')
        # Retrieve mass value for middle trunk
        mass = self.get_single_value(self.dfweight, 'middle_trunk', 'Value')
        # Retrieve middle torso height value
        middletorso = self.get_single_value(self.dfheight, 'middle_torso', 'Value')
        # Return all parameters as a middletorsoParameters instance
        return middletorsoParameters(chestcircumference, chestbreadth, chestdepth,
                                     waistcirc, waistbreadth, waistdepth, middletorso, mass)
    
    # Function to calculate middle trunk inertia with support for custom measurements
    def calculate_middletrunk_inertia_custom(self):
        """
        Calculate middle trunk inertia using custom or default measurements.
        """
        # Use custom chest circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            chestcircumference = self.custom_measures.get('chest_circumference') or self.get_single_value(self.dfcirc, 'chest', 'Value')
        else:
            chestcircumference = self.get_single_value(self.dfcircbase, 'chest', 'Value')
        
        # Use custom chest depth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            chestdepth = self.custom_measures.get('chestdepth') or self.get_single_value(self.dfaddmeasures, 'chestdepth', "Value")
        else:
            chestdepth = self.get_single_value(self.dfaddmeasuresbase, 'chestdepth', "Value")
        
        # Use custom chest breadth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            chestbreadth = self.custom_measures.get('chestbreadth') or self.get_single_value(self.dfaddmeasures, 'chestbreadth', 'Value')
        else:
            chestbreadth = self.get_single_value(self.dfaddmeasuresbase, 'chestbreadth', 'Value')
        
        # Use custom waist circumference if provided and 'fromobese' is False, else use default
        waistcirc = self.custom_measures.get('waist_circumference') or self.get_single_value(self.dfcirc, 'waist', 'Value')
        
        # Use custom waist breadth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            waistbreadth = self.custom_measures.get('waistbreadth') or self.get_single_value(self.dfaddmeasures, 'waistbreadth', 'Value')
        else:
            waistbreadth = self.get_single_value(self.dfaddmeasuresbase, 'waistbreadth', 'Value')
        
        # Use custom waist depth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            waistdepth = self.custom_measures.get('waistdepth') or self.get_single_value(self.dfaddmeasures, 'waistdepth', 'Value')
        else:
            waistdepth = self.get_single_value(self.dfaddmeasuresbase, 'waistdepth', 'Value')
        
        # Retrieve mass value for middle trunk
        mass = self.get_single_value(self.dfweight, 'middle_trunk', 'Value')
        
        # Retrieve middle torso height value from custom data
        middletorso = self.get_single_value(self.heightcustom, 'middle_torso', 'Value')
        
        # Return all parameters as a middletorsoParameters instance
        return middletorsoParameters(chestcircumference, chestbreadth, chestdepth,
                                     waistcirc, waistbreadth, waistdepth, middletorso, mass)
    
    # Function to calculate lower trunk inertia using predefined data
    def calculate_lowertrunk_inertia(self):
        # Retrieve waist circumference value
        waistcirc = self.get_single_value(self.dfcircbase, 'waist', 'Value')
        # Retrieve waist breadth value
        waistbreadth = self.get_single_value(self.dfaddmeasuresbase, 'waistbreadth', 'Value')
        # Retrieve waist depth value
        waistdepth = self.get_single_value(self.dfaddmeasuresbase, 'waistdepth', 'Value')
        # Retrieve hip breadth value
        hipbreadth = self.get_single_value(self.dfaddmeasuresbase, 'hipbreadth', 'Value')
        # Retrieve buttock depth value
        buttockdepth = self.get_single_value(self.dfaddmeasuresbase, 'buttockdepth', 'Value')
        # Retrieve lower torso height value
        lowertorso = self.get_single_value(self.dfheight, 'lower_torso', 'Value')
        # Retrieve mass value for lower trunk
        mass = self.get_single_value(self.dfweight, 'lower_trunk', 'Value')
        # Retrieve crotch height value
        crotch_height = self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        # Retrieve ankle height value
        ankle_height = self.get_single_value(self.dfheight, 'ankle', 'Value')
        # Retrieve shank height value
        shank = self.get_single_value(self.dfheight, 'shank', 'Value')
        # Retrieve thigh height value
        thigh = self.get_single_value(self.dfheight, 'thigh', 'Value')
        # Retrieve buttock circumference value
        buttock_circ=self.get_single_value(self.dfcircbase,'buttock','Value')
        # Return all parameters as a lowertorsoParameters instance
        return lowertorsoParameters(waistcirc,waistbreadth,waistdepth,buttock_circ,hipbreadth,buttockdepth,lowertorso,mass,crotch_height,ankle_height,shank,thigh)
    
    # Function to calculate lower trunk inertia with support for custom measurements
    def calculate_lowertrunk_inertia_custom(self):
        """
        Calculate lower trunk inertia using custom or default measurements.
        
        :param com_uppertorso: Center of mass of the upper torso.
        """
        # Use custom waist circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            waistcirc = self.custom_measures.get('waist_circumference') or self.get_single_value(self.dfcirc, 'waist', 'Value')
        else:
            waistcirc = self.get_single_value(self.dfcircbase, 'waist', 'Value')
        
        # Use custom waist breadth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            waistbreadth = self.custom_measures.get('waistbreadth') or self.get_single_value(self.dfaddmeasures, 'waistbreadth', 'Value')
        else:
            waistbreadth = self.get_single_value(self.dfaddmeasuresbase, 'waistbreadth', 'Value')
        
        # Use custom waist depth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            waistdepth = self.custom_measures.get('waistdepth') or self.get_single_value(self.dfaddmeasures, 'waistdepth', 'Value')
        else:
            waistdepth = self.get_single_value(self.dfaddmeasuresbase, 'waistdepth', 'Value')
        
        # Use custom hip breadth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            hipbreadth = self.custom_measures.get('hipbreadth') or self.get_single_value(self.dfaddmeasures, 'hipbreadth', 'Value')
        else:
            hipbreadth = self.get_single_value(self.dfaddmeasuresbase, 'hipbreadth', 'Value')
        
        # Use custom buttock depth if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            buttockdepth = self.custom_measures.get('buttockdepth') or self.get_single_value(self.dfaddmeasures, 'buttockdepth', 'Value')
        else:
            buttockdepth = self.get_single_value(self.dfaddmeasuresbase, 'buttockdepth', 'Value')
        
        # Retrieve lower torso height value from custom data
        lowertorso = self.get_single_value(self.heightcustom, 'lower_torso', 'Value')
        
        # Retrieve mass value for lower trunk
        mass = self.get_single_value(self.dfweight, 'lower_trunk', 'Value')
        
        # Use custom crotch height if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            crotch_height = self.custom_measures.get('crotchheight') or self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        else:
            crotch_height = self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        
        # Retrieve ankle height value from custom data
        ankle_height = self.get_single_value(self.heightcustom, 'ankle', 'Value')
        
        # Retrieve shank height value from custom data
        shank = self.get_single_value(self.heightcustom, 'shank', 'Value')
        
        # Retrieve thigh height value from custom data
        thigh = self.get_single_value(self.heightcustom, 'thigh', 'Value')
        
        # Use custom buttock circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            buttock_circ = self.custom_measures.get('buttock_circumference') or self.get_single_value(self.dfcirc, 'buttock', 'Value')
        else:
            buttock_circ = self.get_single_value(self.dfcircbase, 'buttock', 'Value')
        
        # Return all parameters as a lowertorsoParameters instance
        return lowertorsoParameters(waistcirc, waistbreadth, waistdepth, buttock_circ, hipbreadth, buttockdepth, lowertorso, mass, crotch_height, ankle_height, shank, thigh)
    
    # Function to calculate thigh inertia using predefined data
    def calculate_thigh_inertia(self):
        # Retrieve thigh height value
        thigh = self.get_single_value(self.dfheight, 'thigh', 'Value')
        # Retrieve thigh circumference value
        thighcirc = self.get_single_value(self.dfcircbase, 'thigh', 'Value')
        # Retrieve lower thigh circumference value
        lowthighcirc = self.get_single_value(self.dfcircbase, 'lowerthigh', 'Value')
        # Retrieve mass value for thigh
        mass = self.get_single_value(self.dfweight, 'thigh', 'Value')
        # Retrieve crotch height value
        crotchheight = self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        # Retrieve ankle height value
        ankleheight = self.get_single_value(self.dfheight, 'ankle', 'Value')
        # Retrieve shank height value
        shankheight = self.get_single_value(self.dfheight, 'shank', 'Value')
        # Return all parameters as a thighParameters instance
        return thighParameters(thigh, thighcirc, lowthighcirc, mass, crotchheight, ankleheight, shankheight)
    
    # Function to calculate thigh inertia with support for custom measurements
    def calculate_thigh_inertia_custom(self):
        """
        Calculate thigh inertia using custom or default measurements.
        """
        # Retrieve thigh height value from custom data
        thigh = self.get_single_value(self.heightcustom, 'thigh', 'Value')
        
        # Use custom thigh circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            thighcirc = self.custom_measures.get('thigh_circumference') or self.get_single_value(self.dfcirc, 'thigh', 'Value')
        else:
            thighcirc = self.get_single_value(self.dfcircbase, 'thigh', 'Value')
        
        # Use custom lower thigh circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            lowthighcirc = self.custom_measures.get('lower_thigh_circumference') or self.get_single_value(self.dfcirc, 'lowerthigh', 'Value')
        else:
            lowthighcirc = self.get_single_value(self.dfcircbase, 'lowerthigh', 'Value')
        
        # Retrieve mass value for thigh
        mass = self.get_single_value(self.dfweight, 'thigh', 'Value')
        
        # Use custom calf circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            calfcirc = self.custom_measures.get('calf_circumference') or self.get_single_value(self.dfcirc, 'calf', 'Value')
        else:
            calfcirc = self.get_single_value(self.dfcircbase, 'calf', 'Value')
        
        # Use custom crotch height if provided
        crotchheight = self.custom_measures.get('crotchheight') or self.get_single_value(self.dfheight, 'crotchheight', 'Value')

        # Retrieve ankle height value from custom data
        ankleheight = self.get_single_value(self.heightcustom, 'ankle', 'Value')
        
        # Retrieve shank height value from custom data
        shankheight = self.get_single_value(self.heightcustom, 'shank', 'Value')
        
        # Return all parameters as a thighParameters instance
        return thighParameters(thigh, thighcirc, lowthighcirc, mass, crotchheight, ankleheight, shankheight)
    
    # Function to calculate shank inertia using predefined data
    def calculate_shank_inertia(self):
        # Retrieve shank height value
        shank = self.get_single_value(self.dfheight, 'shank', 'Value')
        # Retrieve calf circumference value
        calf_circumference = self.get_single_value(self.dfcircbase, 'calf', 'Value')
        # Retrieve ankle circumference value
        ankle_circumference = self.get_single_value(self.dfcircbase, 'ankle', 'Value')
        # Retrieve mass value for shank
        shank_mass = self.get_single_value(self.dfweight, 'shank', 'Value')
        # Return all parameters as a shankParameters instance
        return shankParameters(shank, calf_circumference, ankle_circumference, shank_mass)
    
    # Function to calculate shank inertia with support for custom measurements
    def calculate_shank_inertia_custom(self):
        """
        Calculate shank inertia using custom or default measurements.
        """
        # Retrieve shank height value from custom data
        shank = self.get_single_value(self.heightcustom, 'shank', 'Value')
        
        # Use custom calf circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            calf_circumference = self.custom_measures.get('calf_circumference') or self.get_single_value(self.dfcirc, 'calf', 'Value')
        else:
            calf_circumference = self.get_single_value(self.dfcircbase, 'calf', 'Value')
        
        # Use custom ankle circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            ankle_circumference = self.custom_measures.get('ankle_circumference') or self.get_single_value(self.dfcirc, 'ankle', 'Value')
        else:
            ankle_circumference = self.get_single_value(self.dfcircbase, 'ankle', 'Value')
        
        # Retrieve mass value for shank
        shank_mass = self.get_single_value(self.dfweight, 'shank', 'Value')
        
        # Return all parameters as a shankParameters instance
        return shankParameters(shank, calf_circumference, ankle_circumference, shank_mass)
    
    # Function to calculate foot inertia using predefined data
    def calculate_foot_inertia(self):
        # Retrieve foot length value
        foot = self.get_single_value(self.dfheight, 'foot', 'Value')
        # Retrieve ankle height value
        ankle_height = self.get_single_value(self.dfheight, 'ankle', 'Value')
        # Retrieve ball of foot circumference value
        balloffoot_circumference = self.get_single_value(self.dfcircbase, 'balloffoot', 'Value')
        # Retrieve mass value for foot
        foot_mass = self.get_single_value(self.dfweight, 'foot', 'Value')
        # Return all parameters as a footParameters instance
        return footParameters(foot, ankle_height, balloffoot_circumference, foot_mass)

    # Function to calculate foot inertia with support for custom measurements
    def calculate_foot_inertia_custom(self):
        """
        Calculate foot inertia using custom or default measurements.
        """
        # Retrieve foot length value from custom data
        foot = self.get_single_value(self.heightcustom, 'foot', 'Value')
        
        # Retrieve ankle height value from custom data
        ankle_height = self.get_single_value(self.heightcustom, 'ankle', 'Value')
        
        # Use custom ball of foot circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            balloffoot_circumference = self.custom_measures.get('balloffoot_circumference') or self.get_single_value(self.dfcirc, 'balloffoot', 'Value')
        else:
            balloffoot_circumference = self.get_single_value(self.dfcircbase, 'balloffoot', 'Value')
        
        # Retrieve mass value for foot
        foot_mass = self.get_single_value(self.dfweight, 'foot', 'Value')
        
        # Return all parameters as a footParameters instance
        return footParameters(foot, ankle_height, balloffoot_circumference, foot_mass)
        
    # Function to calculate upper arm inertia using predefined data
    def calculate_upperarm_inertia(self):
        # Retrieve upper arm length value
        upperarm = self.get_single_value(self.dfheight, 'upperarm', 'Value')
        # Retrieve biceps circumference value
        biceps_circumference = self.get_single_value(self.dfcirc, 'biceps', 'Value')
        # Retrieve forearm circumference value
        forearm_circumference = self.get_single_value(self.dfcirc, 'forearm', 'Value')
        # Retrieve mass value for upper arm
        upperarm_mass = self.get_single_value(self.dfweight, 'upper_arm', 'Value')
        # Return all parameters as an upperarmParameters instance
        return upperarmParameters(upperarm, biceps_circumference, forearm_circumference, upperarm_mass)

    def calculate_upperarm_inertia_custom(self):
        """
        Calculate upper arm inertia using custom or default measurements.
        """
        # Retrieve upper arm length value from custom data
        upperarm = self.get_single_value(self.heightcustom, 'upperarm', 'Value')
        
        # Use custom biceps circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            biceps_circumference = self.custom_measures.get('bicep_circumference') or self.get_single_value(self.dfcirc, 'biceps', 'Value')
        else:
            biceps_circumference = self.get_single_value(self.dfcircbase, 'biceps', 'Value')
        
        # Use custom forearm circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            forearm_circumference = self.custom_measures.get('forearm_circumference') or self.get_single_value(self.dfcirc, 'forearm', 'Value')
        else:
            forearm_circumference = self.get_single_value(self.dfcircbase, 'forearm', 'Value')
        
        # Retrieve mass value for upper arm
        upperarm_mass = self.get_single_value(self.dfweight, 'upper_arm', 'Value')
        
        # Return all parameters as an upperarmParameters instance
        return upperarmParameters(upperarm, biceps_circumference, forearm_circumference, upperarm_mass)
    
    # Function to calculate forearm inertia using predefined data
    def calculate_forearm_inertia(self):
        # Retrieve forearm length value
        forearm = self.get_single_value(self.dfheight, 'forearm', 'Value')
        # Retrieve forearm circumference value
        forearm_circumference = self.get_single_value(self.dfcircbase, 'forearm', 'Value')
        # Retrieve wrist circumference value
        wrist_circumference = self.get_single_value(self.dfcircbase, 'wrist', 'Value')
        # Retrieve mass value for forearm
        forearm_mass = self.get_single_value(self.dfweight, 'forearm', 'Value')
        # Return all parameters as a forearmParameters instance
        return forearmParameters(forearm, forearm_circumference, wrist_circumference, forearm_mass)

    # Function to calculate forearm inertia with support for custom measurements
    def calculate_forearm_inertia_custom(self):
        """
        Calculate forearm inertia using custom or default measurements.
        """
        # Retrieve forearm length value from custom data
        forearm = self.get_single_value(self.heightcustom, 'forearm', 'Value')
        
        # Use custom forearm circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            forearm_circumference = self.custom_measures.get('forearm_circumference') or self.get_single_value(self.dfcirc, 'forearm', 'Value')
        else:
            forearm_circumference = self.get_single_value(self.dfcircbase, 'forearm', 'Value')
        
        # Use custom wrist circumference if provided and 'fromobese' is False, else use default
        if not self.fromobese:
            wrist_circumference = self.custom_measures.get('wrist_circumference') or self.get_single_value(self.dfcirc, 'wrist', 'Value')
        else:
            wrist_circumference = self.get_single_value(self.dfcircbase, 'wrist', 'Value')
        
        # Retrieve mass value for forearm
        forearm_mass = self.get_single_value(self.dfweight, 'forearm', 'Value')
        
        # Return all parameters as a forearmParameters instance
        return forearmParameters(forearm, forearm_circumference, wrist_circumference, forearm_mass)
    
    # Function to calculate hand inertia using predefined data
    def calculate_hand_inertia(self):
        # Retrieve hand length value
        Hand_length = self.get_single_value(self.dfheight, 'hand', 'Value')
        # Retrieve hand mass value
        hand_mass = self.get_single_value(self.dfweight, 'hand', 'Value')
        # Return all parameters as a handParameters instance
        return handParameters(Hand_length, hand_mass)

    def calculate_hand_inertia_custom(self):
        """
        Calculate hand inertia using custom or default measurements.
        """
        # Retrieve hand length value from custom data
        Hand_length = self.get_single_value(self.heightcustom, 'hand', 'Value')
        
        # Retrieve hand mass value
        hand_mass = self.get_single_value(self.dfweight, 'hand', 'Value')
        
        # Return all parameters as a handParameters instance
        return handParameters(Hand_length, hand_mass)
           
        
class ObeseBodyInertiaPredictor:
    
    def __init__(self,data):
        """
        Initialize the class with the target height, weight, hip circumference, waist circumference and sex.
        :param height: The target height.
        :param weight: The target weight.
        :param hip: The target hip circumference.
        :param waist: The target waist circumference.
        :param sex: The sex of the person (1 for male, 0 for female).
        """
        self.height = data.get('height')
        self.weight=data.get('weight')
        self.sex= 1 if data.get('sex')== "male" else 2
        self.custom_measures=data
        self.bmi = calculate_bmi(self.weight, self.height)
        self.inertiabase, self.circbase,self.addbase = self.calculateBaseValues()
    
    
    def calculateBaseParameters(self):
        self.dfheight,self.heightcustom = self.predict_height()
        self.dfweight = self.predict_weight()
        self.dfcirc= self.predict_circumference()
        self.dfaddmeasures=self.predict_additional_measures()
        self.dfcircnocustom=self.predict_circumference_nocustom()
        self.dfaddmeasuresnocustom=self.predict_additional_measures_nocustom()
    
        head = self.calculate_head_inertia()
        upper_torso,middle_torso,lower_torso=self.caculatetorsoInertia()
        thigh,shank,foot=self.calculatelegInertia()
        upperarm,forearm,hand=self.calculatearmInertia()
        
        self.baseparameters=Segments(head,upper_torso,middle_torso,lower_torso,thigh,shank,foot,upperarm,forearm,hand)
    
    def calculateParametersFromUserInput(self):
        head = self.calculate_head_inertia_custom()
        upper_torso,middle_torso,lower_torso=self.caculatetorsoInertia_custom()
        thigh,shank,foot=self.calculatelegInertia_custom()
        upperarm,forearm,hand=self.calculatearmInertia_custom()
        self.userinputparameters=Segments(head,upper_torso,middle_torso,lower_torso,thigh,shank,foot,upperarm,forearm,hand)
    
    def AdjustInertia(self,userwithadjustedmass=Segments()):
        head = self.calculate_head_inertia_custom(userwithadjustedmass.Head.mass)
        upper_torso,middle_torso,lower_torso=self.caculatetorsoInertia_custom(userwithadjustedmass.UpperTorso.mass,
                                                                              userwithadjustedmass.MiddleTorso.mass,
                                                                              userwithadjustedmass.LowerTorso.mass)
        thigh,shank,foot=self.calculatelegInertia_custom(userwithadjustedmass.Thigh.mass,
                                                         userwithadjustedmass.Shank.mass,
                                                         userwithadjustedmass.Foot.mass)
        upperarm,forearm,hand=self.calculatearmInertia_custom(userwithadjustedmass.UpperArm.mass,
                                                              userwithadjustedmass.Forearm.mass,
                                                              userwithadjustedmass.Hand.mass)
        
        adjustedinertia=Segments(head,upper_torso,middle_torso,lower_torso,thigh,shank,foot,upperarm,forearm,hand,self.dfheight,self.dfcirc,self.dfaddmeasures)
        return adjustedinertia
    
    def get_segments_properties(self):
        # Calculate base parameters
        self.calculateBaseParameters()
        # Calculate parameters from user input
        self.calculateParametersFromUserInput()
        # Update mass
        self.userinputparameters = adjust_mass_from_custom_obese(self.baseparameters, self.userinputparameters)
        self.userinputparameters = adjust_mass(self.weight, self.userinputparameters)
        # Update inertia given the new mass
        self.userinputparameters = self.AdjustInertia(self.userinputparameters)
        return self.userinputparameters
    
    def calculate_addmeasures(self):
        self.dfaddmeasures=self.predict_additional_measures()
        return self.dfaddmeasures
    
    def calculateBaseValues(self):
        self.weightbase=calculate_weight_for_bmi(self.height, target_bmi=30)
        data_copy = self.custom_measures.copy()
        keys_to_keep = {'unit_measure', 'height', 'weight', 'sex', 'file_type', 'file_output'}
        filtered_data = {k: v for k, v in data_copy.items() if k in keys_to_keep}
        self.base=HealthyBodyInertiaPredictor(filtered_data,fromobese=True,weight=self.weightbase)
        # Calculate inertia from base and from custom values
        baseparameters=self.base.get_segments_properties()
        circbase=self.base.dfcircbase
        addbase=self.base.dfaddmeasuresbase
        return baseparameters,circbase,addbase
        
    
    def calculate_circumferences(self):
        self.dfcirc = self.predict_circumference()
        return self.dfcirc
    
    def predict_height(self):
        height_predictor = BodyLengthPredictor(self.height, self.sex,self.custom_measures)
        return height_predictor.predict_and_adjust()
    
    def predict_weight(self):
        weight_predictor = BodyMassPredictor(self.height, self.weight, self.sex)
        return weight_predictor.predict()
    
    def predict_additional_measures(self):
        add_measures=BodyAddMeasuresPredictor(self.height, self.weight, self.sex,self.custom_measures,False)
        return add_measures.predict()
    
    def predict_circumference(self):
        circ_predictor = BodyCircumferencePredictor(self.height, self.weight, self.sex,self.custom_measures,False)
        return circ_predictor.predict()
    
    def predict_additional_measures_nocustom(self):
        add_measures=BodyAddMeasuresPredictor(self.height, self.weight, self.sex,None,False)
        return add_measures.predict()
    
    def predict_circumference_nocustom(self):
        circ_predictor = BodyCircumferencePredictor(self.height, self.weight, self.sex,None,False)
        return circ_predictor.predict()
    
    def get_single_value(self, df, segment, column):
        value = df.loc[df['Segment'] == segment, column].values
        if value.size == 0:
            raise ValueError(f"Segment '{segment}' not found in the DataFrame.")
        return value[0]
    
    def calculate_head_inertia(self):
        """
        Calculate head inertia using base and custom measures.
        """
        # Get head circumference value
        head_circumference= self.get_single_value(self.dfcircnocustom, 'head', 'Value')
        
        head_mass_obese = self.get_single_value(self.dfweight, 'Head', 'Value')
        # Get head length, use custom measure if provided
        head_length = self.get_single_value(self.dfheight, 'head', 'Value')
        
        head_breadth=self.get_single_value(self.dfaddmeasuresnocustom, 'headbreadth', 'Value')
        # Return all parameters as a headObeseParameters instance
        return headObeseParameters(head_circumference, head_length, head_breadth, head_mass_obese)
    
    def calculate_head_inertia_custom(self,headmass=None):
        """
        Calculate custom head inertia using provided custom measurements.
        """
        # Get head circumference value
        head_circumference_base = self.get_single_value(self.circbase, 'head', 'Value')

        head_mass_obese =headmass or self.get_single_value(self.dfweight, 'Head', 'Value')
        # Get head length from custom height data
        head_length = self.get_single_value(self.heightcustom, 'head', 'Value')
        
        head_breadth=self.get_single_value(self.dfaddmeasures, 'headbreadth', 'Value')
        # Return all parameters as a headObeseParameters instance
        return headObeseParameters(head_circumference_base, head_length, head_breadth, head_mass_obese)
    
    def caculatetorsoInertia(self):
        """
        Calculate torso inertia using base and custom measures.
        """
        # Retrieve base circumference and breadth values
        Neckbase_circumference_base = self.get_single_value(self.circbase, 'neckbase', 'Value')
        Neckbase_circumference_obese = self.get_single_value(self.dfcircnocustom, 'neckbase', 'Value')
        Shoulder_breadth_base = self.get_single_value(self.addbase, 'biacromialbreadth', 'Value')
        Chest_depth_base = self.get_single_value(self.addbase, 'chestdepth', 'Value')
        Chest_depth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'chestdepth', 'Value')
        
        # Retrieve torso segment lengths
        upper_torso = self.get_single_value(self.dfheight, 'upper_torso', 'Value')
        middle_torso = self.get_single_value(self.dfheight, 'middle_torso', 'Value')
        lower_torso = self.get_single_value(self.dfheight, 'lower_torso', 'Value')
        
        # Retrieve additional measurements
        shoulderwaistlen = self.get_single_value(self.dfheight, 'shoulderwaistlen', 'Value')
        Chest_circumference_base = self.get_single_value(self.circbase, 'chest', 'Value')
        Chest_breadth_base = self.get_single_value(self.addbase, 'chestbreadth', 'Value')
        Chest_breadth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'chestbreadth', 'Value')
        Waist_circumference_base =self.get_single_value(self.circbase, 'waist', 'Value')
        Waist_breadth_base = self.get_single_value(self.addbase, 'waistbreadth', 'Value')
        Waist_breadth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'waistbreadth', 'Value')
        Waist_depth_base = self.get_single_value(self.addbase, 'waistdepth', 'Value')
        Waist_depth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'waistdepth', 'Value')
        Hip_breadth_base = self.get_single_value(self.addbase, 'hipbreadth', 'Value')
        Hip_breadth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'hipbreadth', 'Value')
        buttock_depth_base = self.get_single_value(self.addbase, 'buttockdepth', 'Value')
        buttock_depth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'buttockdepth', 'Value')
        
        # Retrieve mass values for torso segments
        uppertorso_mass = self.inertiabase.UpperTorso.mass
        middletorso_mass = self.inertiabase.MiddleTorso.mass
        lowertorso_mass = self.inertiabase.LowerTorso.mass
        
        # Retrieve BMI and other obese-specific measurements
        BMI_obese = self.bmi
        Waist_circumference_obese = self.get_single_value(self.dfcircnocustom, 'waist', 'Value')
        Shoulder_breadth_obese = self.get_single_value(self.dfaddmeasuresnocustom, 'biacromialbreadth', 'Value')
        Chest_circumference_obese = self.get_single_value(self.dfcircnocustom, 'chest', 'Value')
        Hip_circumference_obese = self.get_single_value(self.dfcircnocustom, 'hip', 'Value')
        Hip_circumference_base =self.get_single_value(self.circbase, 'hip', 'Value')
        torso_mass_obese = self.get_single_value(self.dfweight, 'Trunk', 'Value')
        
        # Retrieve height measurements for various segments
        crotch_height = self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        ankle_height = self.get_single_value(self.dfheight, 'ankle', 'Value')
        shank = self.get_single_value(self.dfheight, 'shank', 'Value')
        thigh = self.get_single_value(self.dfheight, 'thigh', 'Value')
        
        # Create an instance of ObeseTorsoDissection with the collected measurements
        x = ObeseTorsoDissection(
            Neckbase_circumference_base,Neckbase_circumference_obese, Shoulder_breadth_base, Shoulder_breadth_obese, 
            Chest_depth_base,Chest_depth_obese, upper_torso, middle_torso, lower_torso, shoulderwaistlen,
            Chest_circumference_base, Chest_circumference_obese, Chest_breadth_base, Chest_breadth_obese, uppertorso_mass, BMI_obese,
            Waist_circumference_base, Waist_circumference_obese,
            Waist_depth_base,Waist_depth_obese, middletorso_mass, Waist_breadth_base, Waist_breadth_obese,
            Hip_breadth_base,Hip_breadth_obese,buttock_depth_base,buttock_depth_obese,
            lowertorso_mass,Hip_circumference_base,Hip_circumference_obese,torso_mass_obese,crotch_height,ankle_height,shank, thigh
        )
        
        # Calculate and return the inertia of the torso
        return x.calculateInertiaTorso()
    
    def caculatetorsoInertia_custom(self,uppertorsomass=None,middletorsomass=None,lowertorsomass=None):
        """
        Calculate custom torso inertia using base and custom measures.
        """
        # Retrieve base circumference and breadth values
        Neckbase_circumference_base = self.get_single_value(self.circbase, 'neckbase', 'Value')
        Neckbase_circumference_obese = self.get_single_value(self.dfcirc, 'neckbase', 'Value')
        Shoulder_breadth_base = self.get_single_value(self.addbase, 'biacromialbreadth', 'Value')
        Chest_depth_base = self.get_single_value(self.addbase, 'chestdepth', 'Value')
        Chest_depth_obese = self.get_single_value(self.dfaddmeasures, 'chestdepth', 'Value')
        Chest_breadth_obese = self.get_single_value(self.dfaddmeasures, 'chestbreadth', 'Value')
        # Retrieve custom torso segment lengths
        upper_torso = self.get_single_value(self.heightcustom, 'upper_torso', 'Value')
        middle_torso = self.get_single_value(self.heightcustom, 'middle_torso', 'Value')
        lower_torso = self.get_single_value(self.heightcustom, 'lower_torso', 'Value')
        
        # Retrieve additional custom or default base model measurements
        shoulderwaistlen = self.custom_measures.get('shoulderwaistlen') or self.get_single_value(self.dfheight, 'shoulderwaistlen', 'Value')
        Chest_circumference_base = self.get_single_value(self.circbase, 'chest', 'Value')
        Chest_breadth_base = self.get_single_value(self.addbase, 'chestbreadth', 'Value')

        Waist_circumference_base = self.custom_measures.get('waist_circumference') or self.get_single_value(self.circbase, 'waist', 'Value')
        Waist_breadth_base = self.get_single_value(self.addbase, 'waistbreadth', 'Value')
        Waist_depth_base = self.get_single_value(self.addbase, 'waistdepth', 'Value')
        Waist_depth_obese = self.get_single_value(self.dfaddmeasures, 'waistdepth', 'Value')
        Waist_breadth_obese = self.get_single_value(self.dfaddmeasures, 'waistbreadth', 'Value')
        Hip_breadth_base = self.get_single_value(self.addbase, 'hipbreadth', 'Value')
        Hip_breadth_obese = self.get_single_value(self.dfaddmeasures, 'hipbreadth', 'Value')
        buttock_depth_base = self.get_single_value(self.addbase, 'buttockdepth', 'Value')
        buttock_depth_obese = self.get_single_value(self.dfaddmeasures, 'buttockdepth', 'Value')
        
        # Retrieve mass values for torso segments
        uppertorso_mass = self.inertiabase.UpperTorso.mass
        middletorso_mass = self.inertiabase.MiddleTorso.mass
        lowertorso_mass = self.inertiabase.LowerTorso.mass
        
        # Retrieve BMI and other obese-specific custom measurements
        BMI_obese = self.bmi
        Waist_circumference_obese = self.custom_measures.get('waist_circumference') or self.get_single_value(self.dfcirc, 'waist', 'Value')
        Shoulder_breadth_obese = self.custom_measures.get('shoulder-breadth') or self.get_single_value(self.dfaddmeasures, 'biacromialbreadth', 'Value')
        Chest_circumference_obese = self.custom_measures.get('chest_circumference') or self.get_single_value(self.dfcirc, 'chest', 'Value')
        Hip_circumference_obese = self.custom_measures.get('hip_circumference') or self.get_single_value(self.dfcirc, 'hip', 'Value')
        torso_mass_obese = self.get_single_value(self.dfweight, 'Trunk', 'Value')
        
        # Retrieve height measurements for various segments
        crotch_height = self.custom_measures.get('crotchheight') or self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        ankle_height = self.get_single_value(self.heightcustom, 'ankle', 'Value')
        shank = self.get_single_value(self.heightcustom, 'shank', 'Value')
        thigh = self.get_single_value(self.heightcustom, 'thigh', 'Value')
        Hip_circumference_base =self.custom_measures.get('hip_circumference') or self.get_single_value(self.circbase, 'hip', 'Value')
        
        # Create an instance of ObeseTorsoDissection with the collected measurements
        x = ObeseTorsoDissection(
            Neckbase_circumference_base,Neckbase_circumference_obese, Shoulder_breadth_base, Shoulder_breadth_obese, 
            Chest_depth_base,Chest_depth_obese, upper_torso, middle_torso, lower_torso, shoulderwaistlen,
            Chest_circumference_base, Chest_circumference_obese, Chest_breadth_base, Chest_breadth_obese, uppertorso_mass, BMI_obese,
            Waist_circumference_base, Waist_circumference_obese,
            Waist_depth_base,Waist_depth_obese, middletorso_mass, Waist_breadth_base, Waist_breadth_obese,
            Hip_breadth_base,Hip_breadth_obese,buttock_depth_base,buttock_depth_obese,
            lowertorso_mass,Hip_circumference_base,Hip_circumference_obese,torso_mass_obese,crotch_height,ankle_height,shank, thigh,
            uppertorsomass,middletorsomass,lowertorsomass
        )
        
        # Calculate and return the inertia of the torso
        return x.calculateInertiaTorso()
    
    def calculatelegInertia(self):
        """
        Calculate the inertia of the leg segment.
    
        Retrieves various parameters such as length, mass, and circumference values
        for different parts of the leg, and uses these to calculate the leg inertia.
    
        Returns:
            ObeseLegDissection instance with calculated leg inertia.
        """
    
        # Retrieve segment lengths from height data
        shank = self.get_single_value(self.dfheight, 'shank', 'Value')
        thigh = self.get_single_value(self.dfheight, 'thigh', 'Value')
        foot = self.get_single_value(self.dfheight, 'foot', 'Value')
        ankle_height = self.get_single_value(self.dfheight, 'ankle', 'Value')
    
        # Retrieve base circumferences for thigh, lower thigh, calf, ankle, and ball of foot
        thigh_circumference_base = self.get_single_value(self.circbase, 'thigh', 'Value')
        lowerthigh_circumference_base = self.get_single_value(self.circbase, 'lowerthigh', 'Value')
        lowerthigh_circumference_obese = self.get_single_value(self.dfcircnocustom, 'lowerthigh', 'Value')
        calf_circumference_base = self.get_single_value(self.circbase, 'calf', 'Value')
        ankle_circumference_base = self.get_single_value(self.circbase, 'ankle', 'Value')
        balloffoot_circumference = self.get_single_value(self.dfcircnocustom, 'balloffoot', 'Value')
    
        # Retrieve base masses for thigh, shank, and foot
        thigh_mass = self.inertiabase.Thigh.mass
        shank_mass = self.inertiabase.Shank.mass
        foot_mass = self.inertiabase.Foot.mass
    
        # Retrieve obese circumferences for thigh, calf, and ankle
        thigh_circumference_obese = self.get_single_value(self.dfcircnocustom, 'thigh', 'Value')
        calf_circumference_obese = self.get_single_value(self.dfcircnocustom, 'calf', 'Value')
        ankle_circumference_obese = self.get_single_value(self.dfcircnocustom, 'ankle', 'Value')
        hip_circumference_obese=self.get_single_value(self.dfcircnocustom, 'hip', 'Value')
    
        # Retrieve mass of the entire leg for obese subject
        leg_mass_obese = self.get_single_value(self.dfweight, 'Leg', 'Value')
    
        # Retrieve crotch height value
        crotch_height = self.get_single_value(self.dfheight, 'crotchheight', 'Value')
    
        # Create an ObeseLegDissection instance using all the retrieved parameters
        x = ObeseLegDissection(
            thigh, thigh_circumference_base, lowerthigh_circumference_base,
            calf_circumference_base, thigh_mass, thigh_circumference_obese, lowerthigh_circumference_obese,shank,
            calf_circumference_obese, ankle_circumference_obese, shank_mass, foot_mass,
            ankle_circumference_base, leg_mass_obese, ankle_height, balloffoot_circumference,
            foot, crotch_height,hip_circumference_obese,self.bmi
        )
    
        return x.calculateInertiaLeg()

    
    def calculatelegInertia_custom(self,thighmass=None,shankmass=None,footmass=None):
        """
        Calculate the inertia of the leg segment with support for custom measurements.
        
        Retrieves various parameters such as length, mass, and circumference values
        for different parts of the leg, and uses these to calculate the leg inertia.
    
        Returns:
            ObeseLegDissection instance with parameters for the leg.
        """
        # Retrieve shank height from custom data
        shank = self.get_single_value(self.heightcustom, 'shank', 'Value')
        
        # Retrieve thigh height from custom data
        thigh = self.get_single_value(self.heightcustom, 'thigh', 'Value')
        
        # Base circumferences for thigh, lower thigh, calf, and ankle
        thigh_circumference_base = self.get_single_value(self.circbase, 'thigh', 'Value')
        lowerthigh_circumference_base = self.get_single_value(self.circbase, 'lowerthigh', 'Value')
        lowerthigh_circumference_obese = self.get_single_value(self.dfcirc, 'lowerthigh', 'Value')
        calf_circumference_base = self.get_single_value(self.circbase, 'calf', 'Value')
        ankle_circumference_base = self.get_single_value(self.circbase, 'ankle', 'Value')
        
        # Retrieve thigh mass from base inertia data
        thigh_mass = self.inertiabase.Thigh.mass
        
        # Obese circumferences for thigh, calf, and ankle, using custom values if provided
        thigh_circumference_obese = self.custom_measures.get('thigh_circumference') or self.get_single_value(self.dfcirc, 'thigh', 'Value')
        calf_circumference_obese = self.custom_measures.get('calf_circumference') or self.get_single_value(self.dfcirc, 'calf', 'Value')
        ankle_circumference_obese = self.custom_measures.get('ankle_circumference') or self.get_single_value(self.dfcirc, 'ankle', 'Value')
        hip_circumference_obese = self.custom_measures.get('hip_circumference') or self.get_single_value(self.dfcirc, 'hip', 'Value')
        
        # Retrieve mass values for shank, foot, and leg from base inertia data
        shank_mass = self.inertiabase.Shank.mass
        foot_mass = self.inertiabase.Foot.mass
        leg_mass_obese = self.get_single_value(self.dfweight, 'Leg', 'Value')
        
        # Retrieve ankle height and foot length from custom data
        ankle_height = self.get_single_value(self.heightcustom, 'ankle', 'Value')
        foot = self.get_single_value(self.heightcustom, 'foot', 'Value')
        
        # Retrieve ball of foot circumference and crotch height
        balloffoot_circumference = self.get_single_value(self.dfcirc, 'balloffoot', 'Value')
        crotch_height = self.custom_measures.get('crotchheight') or self.get_single_value(self.dfheight, 'crotchheight', 'Value')
        
        # Create an ObeseLegDissection instance using all the retrieved parameters
        x = ObeseLegDissection(
            thigh, thigh_circumference_base, lowerthigh_circumference_base,
            calf_circumference_base, thigh_mass, thigh_circumference_obese, lowerthigh_circumference_obese,shank,
            calf_circumference_obese, ankle_circumference_obese, shank_mass, foot_mass,
            ankle_circumference_base, leg_mass_obese, ankle_height, balloffoot_circumference,
            foot, crotch_height,hip_circumference_obese,self.bmi,thighmass,shankmass,footmass
        )
        
        return x.calculateInertiaLeg()

    
    def calculatearmInertia(self):
        """
        Calculate the inertia of the arm using base measurements.
        
        :return: A list of inertia parameters calculated by the ObeseArm class.
        """
        # Retrieve the base and obese measurements for the arm segments
        upperarm = self.get_single_value(self.dfheight, 'upperarm', 'Value')
        biceps_circumference_base = self.get_single_value(self.circbase, 'biceps', 'Value')
        forearm_circumference_base = self.get_single_value(self.circbase, 'forearm', 'Value')
        upperarm_mass = self.inertiabase.UpperArm.mass
    
        # Retrieve obese-specific measurements for the arm segments
        forearm_circumference_obese = self.get_single_value(self.dfcircnocustom, 'forearm', 'Value')
        forearm = self.get_single_value(self.dfheight, 'forearm', 'Value')
        wrist_circumference_base = self.get_single_value(self.circbase, 'wrist', 'Value')
        forearm_mass = self.inertiabase.Forearm.mass
        hand_mass = self.inertiabase.Hand.mass
        wrist_circumference_obese = self.get_single_value(self.dfcircnocustom, 'wrist', 'Value')
        arm_mass_obese = self.get_single_value(self.dfweight, 'Arm', 'Value')
        biceps_circumference_obese = self.get_single_value(self.dfcircnocustom, 'biceps', 'Value')
        hand_length = self.get_single_value(self.dfheight, 'hand', 'Value')
    
        # Instantiate the ObeseArm class with the provided parameters
        x = ObeseArm(
            upperarm, biceps_circumference_base, forearm_circumference_base, 
            upperarm_mass, forearm_circumference_obese, forearm, wrist_circumference_base,
            forearm_mass, hand_mass, wrist_circumference_obese, arm_mass_obese,
            biceps_circumference_obese, hand_length
        )
    
        # Calculate and return the inertia values for the arm
        return x.calculateInertiaArm()
    
    def calculatearmInertia_custom(self,upperarmmass=None,forearmmass=None,handmass=None):
        """
        Calculate the inertia of the arm using custom measurements if available.
        
        :return: A list of inertia parameters calculated by the ObeseArm class.
        """
        # Retrieve custom or base measurements for the arm segments
        upperarm = self.get_single_value(self.heightcustom, 'upperarm', 'Value')
        biceps_circumference_base = self.get_single_value(self.circbase, 'biceps', 'Value')
        forearm_circumference_base = self.get_single_value(self.circbase, 'forearm', 'Value')
        upperarm_mass = self.inertiabase.UpperArm.mass
    
        # Use custom measurements if provided, otherwise use the default values
        forearm_circumference_obese = self.custom_measures.get('forearm_circumference') or self.get_single_value(self.dfcirc, 'forearm', 'Value')
        forearm = self.get_single_value(self.heightcustom, 'forearm', 'Value')
        wrist_circumference_base = self.get_single_value(self.circbase, 'wrist', 'Value')
        forearm_mass =  self.inertiabase.Forearm.mass
        hand_mass = self.inertiabase.Hand.mass
        wrist_circumference_obese = self.custom_measures.get('wrist_circumference') or self.get_single_value(self.dfcirc, 'wrist', 'Value')
        arm_mass_obese = self.get_single_value(self.dfweight, 'Arm', 'Value')
        biceps_circumference_obese = self.custom_measures.get('bicep_circumference') or self.get_single_value(self.dfcirc, 'biceps', 'Value')
        hand_length = self.get_single_value(self.heightcustom, 'hand', 'Value')
    
        # Instantiate the ObeseArm class with the provided parameters
        x = ObeseArm(
            upperarm, biceps_circumference_base, forearm_circumference_base, 
            upperarm_mass, forearm_circumference_obese, forearm, wrist_circumference_base,
            forearm_mass, hand_mass, wrist_circumference_obese, arm_mass_obese,
            biceps_circumference_obese, hand_length,upperarmmass,forearmmass,handmass
        )
    
        # Calculate and return the inertia values for the arm
        return x.calculateInertiaArm()
