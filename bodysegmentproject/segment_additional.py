import joblib
import pandas as pd
from .utils import calculate_bmi
from pathlib import Path

class BodyAddMeasuresPredictor:
    def __init__(self, height, weight, sex, custom_measures=None, basemodel=True):
        """
        Initialize the class with the target height, weight and sex.

        :param height: The target height.
        :param weight: The target weight.
        :param sex: 1 if male, 2 if female
        """
        self.height = height
        self.weight = weight
        self.sex = sex
        self.bmi = calculate_bmi(self.weight, self.height)
        self.basemodel = basemodel
        base_path = Path(__file__).parent

        self.custom_measures = custom_measures if custom_measures is not None else {}

        folder = "Male" if self.sex == 1 else "Female"

        # Determine if we use hip/waist model
        use_hip_waist_model = (
            self.custom_measures.get('hip_circumference') is not None and
            self.custom_measures.get('waist_circumference') is not None and
            not self.basemodel
        )

        self.model_path = base_path / folder / (
            "segmentadditionalmeasureshipwaist" if use_hip_waist_model
            else "segmentadditionalmeasures"
        )

        # Measures to predict
        self.add_measures = [
            'biacromialbreadth',
            'headbreadth',
            'chestbreadth',
            'hipbreadth',
            'waistbreadth',
            'waistdepth',
            'chestdepth',
            'buttockdepth',
        ]

        # Load models
        self.models = {}
        for measure in self.add_measures:
            model_file = self.model_path / f"{measure}.joblib"
            
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")
            
            self.models[measure] = joblib.load(model_file)

        self.use_hip_waist_model = use_hip_waist_model  # Save this for predict()

    def predict(self):
        """
        Predict body additional measures using the loaded models.
    
        :return: DataFrame with segment values.
        """
        predictions = {}
        
        # Prepara i due tipi di input:
        base_input = pd.DataFrame({
            'stature': [self.height],
            'weightkg': self.weight,
            'bmi': self.bmi
        })
    
        if self.use_hip_waist_model:
            extended_input = pd.DataFrame({
                'stature': [self.height],
                'weightkg': self.weight,
                'bmi': self.bmi,
                'buttockcircumference': self.custom_measures.get('hip_circumference'),
                'waistcircumference': self.custom_measures.get('waist_circumference')
            })
        else:
            extended_input = base_input  # fallback per uniformità
    
        for measure, model in self.models.items():
            input_data = extended_input
    
            prediction = model.predict(input_data)
            predictions[measure] = prediction[0]
    
        return pd.DataFrame(list(predictions.items()), columns=['Segment', 'Value'])


    


