import json
import os
import pandas as pd
from scipy.io import savemat
import pandas as pd
from .predictor import *
from .utils import *
import pickle
import copy
#import openpyxl

class SubjectMeasures:
    
    def __init__(self, data,geometricmodel=True):
        """
        Initialize the class with the subject's height, weight, and sex.
        :param data: Dictionary containing subject measures.
        """
        self.data = data
        self.geometricmodel=geometricmodel

    def GetSubjectMeasures(self):
        """
        Adjust subject measures, calculate BMI, and predict body segment inertias.
        
        :return: DataFrame containing adjusted segment mass values.
        """

        local_data = copy.deepcopy(self.data)
        
        # Adjust measures to the correct units (SI or USCS)
        local_data = convert_units(local_data)
        
        # Calculate BMI and validate data format
        bmi = check_data_format_and_bmi(local_data)
        
        # Select predictor based on BMI
        if bmi < 30 or self.geometricmodel == False:
            predictor = HealthyBodyInertiaPredictor(local_data)
        else:
            predictor = ObeseBodyInertiaPredictor(local_data)
        
        self.SegmentModel=predictor.get_segments_properties()
        return predictor.get_segments_properties()
    
    def get_circumferences(self):
        """
        Adjust subject measures, calculate BMI, and predict body segment inertias.
        
        :return: DataFrame containing adjusted segment mass values.
        """
        # Adjust measures to the correct units (SI or USCS)
        local_data = copy.deepcopy(self.data)
        local_data = convert_units(local_data)
        
        # Calculate BMI and validate data format
        bmi = check_data_format_and_bmi(local_data)
        
        # Select predictor based on BMI
        if bmi < 30:
            # Use healthy body predictor for BMI less than 30
            predictor = HealthyBodyInertiaPredictor(local_data)
        else:
            # Use Obese body predictor for BMI greather than 30
            predictor = ObeseBodyInertiaPredictor(local_data)
        
        return predictor.calculate_circumferences()
    
    def get_crosssections(self):
        """
        Adjust subject measures, calculate BMI, and predict body segment inertias.
        
        :return: DataFrame containing crosssections values.
        """
        # Adjust measures to the correct units (SI or USCS)
        local_data = copy.deepcopy(self.data)
        local_data = convert_units(local_data)
        
        # Calculate BMI and validate data format
        bmi = check_data_format_and_bmi(local_data)
        
        # Select predictor based on BMI
        if bmi < 30:
            # Use healthy body predictor for BMI less than 30
            predictor = HealthyBodyInertiaPredictor(local_data)
        else:
            # Use Obese body predictor for BMI greather than 30
            predictor = ObeseBodyInertiaPredictor(local_data)
        
        return predictor.predict_additional_measures()
    
    def get_length(self):
        """
        Adjust subject measures, calculate BMI, and predict body segment inertias.
        
        :return: DataFrame containing length values.
        """
        # Adjust measures to the correct units (SI or USCS)
        local_data = copy.deepcopy(self.data)
        local_data = convert_units(local_data)
        
        # Calculate BMI and validate data format
        bmi = check_data_format_and_bmi(local_data)
        
        # Select predictor based on BMI
        if bmi < 30:
            # Use healthy body predictor for BMI less than 30
            predictor = HealthyBodyInertiaPredictor(local_data)
        else:
            # Use Obese body predictor for BMI greather than 30
            predictor = ObeseBodyInertiaPredictor(local_data)
        
        # Use custom-adjusted lengths (index 1) to stay consistent with
        # SegmentMeasures, which is computed from the same adjusted lengths.
        return predictor.predict_height()[1]
    
    def createResultTable(self):
        return self.SegmentModel.to_dataframe()
    
    def createDict(self):
        return self.SegmentModel.to_dict()
    

    def create_file(self):
        """
        Create an output file.
        - .xlsx/.pkl: keep the existing DataFrame-based tables
        - .json/.mat: export the nested dict from SegmentModel.to_dict()
        """
        output_name = self.data.get('output_file', 'output.xlsx')
        base, ext = os.path.splitext(output_name)
        ext = ext.lower()

        # Make sure SegmentModel exists once
        if not hasattr(self, "SegmentModel") or self.SegmentModel is None:
            self.GetSubjectMeasures()

        # JSON / MATLAB: export ONLY the nested dict (no DataFrames)
        if ext == '.json':
            model = self.SegmentModel.to_dict()
            with open(output_name, "w", encoding="utf-8") as f:
                json.dump(model, f, ensure_ascii=False, indent=2)
            return

        if ext == '.mat':
            model = self.SegmentModel.to_dict()
            savemat(output_name, {"segment_model": model},
                    long_field_names=True, do_compression=True)
            return

        # Everything else: keep your current DataFrame workflow
        segment_measures = self.createResultTable()
        circumferences = self.get_circumferences()
        crosssections = self.get_crosssections()
        length = self.get_length()

        self.inertia = segment_measures

        result = {
            "SegmentMeasures": segment_measures,
            "Circumferences": circumferences,
            "Length": length,
            "Additional": crosssections,
        }

        if ext == '.xlsx':
            with pd.ExcelWriter(output_name) as writer:
                for sheet_name, df in result.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        elif ext == '.pkl':
            with open(output_name, "wb") as f:
                pickle.dump({k: v.to_dict(orient='list') for k, v in result.items()}, f)

        else:
            raise ValueError(f"Unsupported file extension: {ext}")


            
