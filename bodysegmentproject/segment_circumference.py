import joblib
import pandas as pd
from .utils import calculate_bmi
from pathlib import Path

class BodyCircumferencePredictor:
    def __init__(self, height,weight,sex,custom_measures=None, basemodel=True):
        """
        Initialize the class with the target height, weight and sex.

        :param height: The target height.
        :param weight: The target weight.
        :param sex: 1 if male, 2 if female
        """
        self.height = height
        self.weight=weight
        self.sex=sex
        self.bmi=calculate_bmi(self.weight,self.height)
        self.basemodel=basemodel
        self.custom_measures = custom_measures if custom_measures is not None else {}
        base_path = Path(__file__).parent

        # Set the model path based on sex and presence of hip/waist measurements
        if self.sex == 1:
            folder = "Male"
        else:
            folder = "Female"

        if self.custom_measures.get('hip_circumference')==None or self.custom_measures.get('waist_circumference')==None or self.basemodel==True:
        #if self.custom_measures.get('hip_circumference')==None or self.custom_measures.get('waist_circumference')==None:
            self.model_path = base_path / folder / "segmentcircumferences"
        else:
            self.model_path = base_path / folder / "segmentcircumferenceshipwaist"
            
        if self.custom_measures.get('hip_circumference')==None or self.custom_measures.get('waist_circumference')==None or self.basemodel==True:
        #if self.custom_measures.get('hip_circumference')==None or self.custom_measures.get('waist_circumference')==None:
        
            self.body_circumferences = {
                'head':'headcircumference',
                'neck': 'neckcircumference',
                'neckbase': 'neckcircumferencebase',
                'shoulder': 'shouldercircumference',
                'chest': 'chestcircumference',
                'buttock':'buttockcircumference',
                'biceps': 'bicepscircumferenceflexed',
                'forearm': 'forearmcircumferenceflexed',
                'hand': 'handcircumference',
                'wrist': 'wristcircumference',
                'thigh': 'thighcircumference',
                'lowerthigh': 'lowerthighcircumference',
                'heelankle': 'heelanklecircumference',
                'calf': 'calfcircumference',
                'ankle': 'anklecircumference',
                'balloffoot': 'balloffootcircumference',
                'hip':'buttockcircumference',
                'waist':'waistcircumference'
            }
        else:
            self.body_circumferences = {
                'head':'headcircumference',
                'neck': 'neckcircumference',
                'neckbase': 'neckcircumferencebase',
                'shoulder': 'shouldercircumference',
                'chest': 'chestcircumference',
                'buttock':'buttockcircumference',
                'biceps': 'bicepscircumferenceflexed',
                'forearm': 'forearmcircumferenceflexed',
                'hand': 'handcircumference',
                'wrist': 'wristcircumference',
                'thigh': 'thighcircumference',
                'lowerthigh': 'lowerthighcircumference',
                'heelankle': 'heelanklecircumference',
                'calf': 'calfcircumference',
                'ankle': 'anklecircumference',
                'balloffoot': 'balloffootcircumference',
            }

    
    def predict(self):
        """
        Predict body circumferences using the loaded models.

        :return: DataFrame with segment values.
        """
        predictions = {}
        expected_model_names = list(self.body_circumferences.keys())  # Usa tutte le chiavi del dizionario delle circonferenze

        for model_name in expected_model_names:
            model_filename = f"{self.model_path}/{model_name}.joblib"
            
            model = joblib.load(model_filename)
            if self.custom_measures.get('hip_circumference')==None or self.custom_measures.get('waist_circumference')==None or self.basemodel==True:
            #if self.custom_measures.get('hip_circumference')==None or self.custom_measures.get('waist_circumference')==None:
                input_values = {'stature': self.height, 'weightkg': self.weight, 'bmi': self.bmi}
            else:
                input_values = {'stature': self.height, 'weightkg': self.weight, 'bmi': self.bmi,
                                'buttockcircumference':self.custom_measures.get('hip_circumference'),
                                'waistcircumference':self.custom_measures.get('waist_circumference')}
            # Assuming input_values is a dictionary with feature names as keys
            input_data = pd.DataFrame([input_values])
            prediction = model.predict(input_data)
            predictions[model_name] = prediction[0]
        return pd.DataFrame(list(predictions.items()), columns=['Segment', 'Value'])

