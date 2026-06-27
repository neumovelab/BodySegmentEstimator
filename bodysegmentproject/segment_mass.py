import joblib
import pandas as pd
from pathlib import Path
from .utils import calculate_bmi, adjust_mass_obese, adjust_mass_values, percent_segments, divide_segments
from .shan import ShanBodyCalculator

class BodyMassPredictor:
    def __init__(self, height: float, weight: float, sex: int,basemodel=False):
        """
        Initialize the class with the target height, weight, and sex.

        :param height: The target height.
        :param weight: The target weight.
        :param sex: 1 if male, 2 if female.
        """
        self.height = height
        self.weight = weight
        self.sex = sex
        self.bmi = calculate_bmi(self.weight, self.height)
        self.basemodel=basemodel
        base_path = Path(__file__).parent

        # Set the model path based on sex
        if self.sex == 1:
            self.model_path = base_path / "Male" / "segmentmass"
        else:
            self.model_path = base_path / "Female" / "segmentmass"

    def predict(self) -> pd.DataFrame:
        """
        Predict body mass segments and adjust the predictions based on BMI.

        :return: DataFrame with adjusted segment mass predictions.
        """
        predictions = {}
        expected_model_names = ['Leg', 'Arm', 'Trunk', 'Head']

        # Create input data with column names matching the training features.
        # input_data = pd.DataFrame([[self.weight, self.height, self.bmi]],
        #                           columns=["BMXWT", "BMXHT", "BMXBMI"])
        input_data = pd.DataFrame([[self.weight, self.height]],
                                   columns=["BMXWT", "BMXHT"])

        # Load each model and predict the segment mass.
        for model_name in expected_model_names:
            model_filename = self.model_path / f"{model_name}.joblib"
            model = joblib.load(model_filename)
            prediction = model.predict(input_data)
            predictions[model_name] = prediction[0]

        # Convert predictions dictionary to DataFrame.
        df = pd.DataFrame(list(predictions.items()), columns=['Segment', 'Value'])

        # Adjust mass predictions based on BMI threshold.
        if self.bmi < 30 or self.basemodel:
            return self.adjust_mass(df)
        else:
            return adjust_mass_obese(df, self.weight)

    def adjust_mass(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adjust the mass values using calculated segment proportions.

        :param df: DataFrame with initial segment mass predictions.
        :return: Adjusted DataFrame with corrected segment mass values.
        """
        gen = "male" if self.sex == 1 else "female"
        shg = ShanBodyCalculator(self.height, self.weight, "european/american", gen)
        msg = shg.calculate_mass_segments()
        proportion = percent_segments(msg, self.weight)
        new_df = divide_segments(proportion, df)
        return adjust_mass_values(new_df, self.weight)
