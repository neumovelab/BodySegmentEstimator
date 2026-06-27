import joblib
import pandas as pd
from pathlib import Path
import warnings

class BodyLengthPredictor:
    def __init__(self, height, sex, custom_measures=None):
        """
        Initialize the class with the target height.
        
        :param height: The target height to adjust the segments to.
        :param sex: 1 if male, 2 if female.
        :param custom_measures: Dictionary of custom segment measures.
        """
        self.height = height
        self.sex = sex
        self.custom_measures = custom_measures if custom_measures is not None else {}
        base_path = Path(__file__).parent

        # Set the model path based on sex
        if self.sex == 1:
            self.model_path = base_path / "Male" / "segmentlengthmodels"
        else:
            self.model_path = base_path / "Female" / "segmentlengthmodels"

        # Body segment mappings
        self.bodylength = {
            'head': ['stature', 'cervicaleheight'],
            'forearm': ['forearmhandlength', 'handlength'],
            'upperarm': 'acromionradialelength',
            'hand': 'handlength',
            'upper_torso': ['cervicaleheight', 'chestheight'],
            'middle_torso': ['chestheight', 'waistheightomphalion'],
            'lower_torso': ['waistheightomphalion', 'trochanterionheight'],
            'thigh': ['trochanterionheight', 'lateralfemoralepicondyleheight'],
            'shank': ['lateralfemoralepicondyleheight', 'lateralmalleolusheight'],
            'ankle': 'lateralmalleolusheight',
            'foot': 'footlength',
            'headlength': 'headlength',
            'shoulderwaistlen': ['acromialheight', 'waistheightomphalion'],
            'buttockheight': 'buttockheight',
            'crotchheight': 'crotchheight',
        }

        # Pre-load models into a dictionary to avoid repeated disk access
        self.models = {}
        for model_name in self.bodylength.keys():
            model_file = self.model_path / f"{model_name}.joblib"
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")
            self.models[model_name] = joblib.load(model_file)

    def predict_and_adjust(self):
        """
        Predict body lengths using the loaded models and adjust the predictions to match the specified height.

        :return: Two DataFrames containing adjusted segment values for the baseline and custom measures.
        """
        predictions = {}

        # Create input data with the proper feature name and normalization (training used 'stature'/10)
        input_data = pd.DataFrame({'stature': [self.height]})
        # Predict segment lengths using the pre-loaded models
        for model_name, model in self.models.items():
            prediction = model.predict(input_data)
            predictions[model_name] = prediction[0]

        # Convert predictions dictionary to a DataFrame
        df = pd.DataFrame(list(predictions.items()), columns=['Segment', 'Value'])

        # Adjust the segment values based on custom measures and the target height
        final_df = self.adjust_height(df.copy(), self.height, self.custom_measures)
        base_height = self.adjust_height_basemodel(df.copy(), self.height)

        return base_height, final_df

    @staticmethod
    def adjust_height(df, height, custom_measures):
        """
        Adjust segment values to match the target height, taking into account any custom measures.

        :param df: DataFrame with segment names and their predicted values.
        :param height: The target height.
        :param custom_measures: Dictionary of custom segment measures.
        :return: DataFrame with adjusted segment values.
        """
        segments = ['head', 'upper_torso', 'middle_torso', 'lower_torso', 'thigh', 'shank', 'ankle']

        # Warn if the sum of custom measures exceeds the target height
        total_custom_measure = sum(custom_measures.get(seg, 0) for seg in segments)
        if total_custom_measure > height:
            warnings.warn("Body segment lengths are bigger than height", UserWarning)

        # Update segment values with custom measures using vectorized mapping
        df['Value'] = df['Segment'].map(custom_measures).fillna(df['Value']).astype(float)

        # Calculate total height for the segments that need to be adjusted
        segment_mask = df['Segment'].isin(segments)
        total_height = df.loc[segment_mask, 'Value'].sum()

        # Normalize the segment values to fit the target height
        df.loc[segment_mask, 'Value'] = (df.loc[segment_mask, 'Value'] / total_height) * height

        return df

    @staticmethod
    def adjust_height_basemodel(df, height):
        """
        Adjust segment values to match the target height without custom measures.

        :param df: DataFrame with segment names and their predicted values.
        :param height: The target height.
        :return: DataFrame with adjusted segment values.
        """
        segments = ['head', 'upper_torso', 'middle_torso', 'lower_torso', 'thigh', 'shank', 'ankle']

        segment_mask = df['Segment'].isin(segments)
        total_height = df.loc[segment_mask, 'Value'].sum()

        df.loc[segment_mask, 'Value'] = (df.loc[segment_mask, 'Value'] / total_height) * height

        return df




