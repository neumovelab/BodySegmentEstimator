import pandas as pd
import numpy as np
'''
Coefficients of the regression equation y=b0+b1*BM+b2*BH for
estimating anthropometrical data y (in units based on kg and cm) of
male adult Chinese; BM (kg) and BH (cm) are independent variables

Segmental center of mass (COM) is expressed in % of segmental length
'''
class ShanBodyCalculator:
    def __init__(self,height,weight,ethnicity,sex):
        # Initialize the calculator with height, weight and ehticity.
        self.height=height
        self.weight=weight
        self.ethnicity=ethnicity
        self.sex=sex
        

        '''
        Segments mass in Kg
        '''
        self.mass_segments_asian_male = {
            'head': [-12.4, 0.0255, 0.0991],
            'upper_trunk': [-2.95, 0.224, 0.0055],
            'middle_trunk': [2.09, 0.128, -0.0125],
            'lower_trunk': [13.1, 0.185, -0.105],
            'thigh': [4.00, 0.156, -0.036],
            'shank': [-2.75, 0.0058, 0.0336],
            'upper_arm': [0.876, 0.0375, -0.0099],
            'forearm': [-0.739, 0.0103, 0.0063],
            'hand': [-0.120, 0.0098, -0.0007],
            'foot': [-1.34, -0.0012, -0.0137],
        }
        
        self.mass_segments_asian_female = {
            'head': [0.638, 0.0293, 0.0172],
            'upper_trunk': [-11.7, 0.297, 0.0461],
            'middle_trunk': [5.44, 0.186, -0.0546],
            'lower_trunk': [2.21, 0.101, -0.0086],
            'thigh': [7.27, 0.129, -0.0485],
            'shank': [-5.73, 0.0178, 0.0481],
            'foot': [1.12, 0.0087, -0.0057],
            'upper_arm': [0.254, 0.0265, -0.0033],
            'forearm': [-0.625, 0.0083, 0.0054],
            'hand': [-0.605, 0.0022, 0.0044],
            }
        
        self.mass_segments_eur_male = {
            'head': [-7.75, 0.0586, 0.0497],
            'upper_trunk': [-4.13, 0.175, 0.0248],
            'middle_trunk': [11.7, 0.120, -0.0633],
            'lower_trunk': [13.1, 0.162, -0.0873],
            'thigh': [1.18, 0.182, -0.0259],
            'shank': [-3.53, 0.0306, 0.0268],
            'foot': [-2.25, 0.0010, 0.0182],
            'upper_arm': [-0.896, 0.0252, 0.0051],
            'forearm': [-0.731, 0.0047, 0.0084],
            'hand': [-0.325, -0.0016, 0.0051],
            }
        
        self.mass_segments_eur_female = {
            'head': [-2.95, 0.0359, 0.0322],
            'upper_trunk': [25.5, 0.228, -0.160],
            'middle_trunk': [-1.45, 0.0975, 0.0176],
            'lower_trunk': [1.10, 0.104, -0.0027],
            'thigh': [-10.9, 0.213, 0.0380],
            'shank': [-0.563, 0.0191, 0.0141],
            'foot': [-1.27, 0.0045, 0.0104],
            'upper_arm': [3.05, 0.0184, -0.0164],
            'forearm': [-0.481, 0.0087, 0.0043],
            'hand': [-1.13, 0.0031, 0.0074],
            }
        
        '''
        Segment length in cm
        '''
        
        self.body_segment_length_parameters_asian_male = {
            'head': [-28.1, 0.0233, 0.299],
            'upper_trunk': [-15.8, -0.0247, 0.267],
            'middle_trunk': [-6.13, -0.0661, 0.162],
            'lower_trunk': [38.5, 0.117, -0.14],
            'thigh': [-3.27, -0.0193, 0.271],
            'shank': [-2.73, -0.0527, 0.271],
            'foot': [7.97, 0.008, 0.0957],
            'upper_arm': [-9.88, -0.012, 0.210],
            'forearm': [-7.54, -0.0049, 0.194],
            'hand': [13.6, 0.106, -0.0092],
            }
        
        self.body_segment_length_parameters_asian_female = {
            'head': [-9.14, -0.126, 0.244],
            'upper_trunk': [-29.5, 0.0996, 0.328],
            'middle_trunk': [26.7, 0.132, -0.125],
            'lower_trunk': [38.2, 0.105, -0.130],
            'thigh': [-26.7, -0.0902, 0.440],
            'shank': [-16.2, -0.0852, 0.356],
            'foot': [17.9, 0.0644, 0.0083],
            'upper_arm': [-10.6, -0.102, 0.246],
            'forearm': [-4.035, -0.0287, 0.173],
            'hand': [-5.66, -0.0058, 0.143],
            }
        
        self.body_segment_length_parameters_eur_male = {
            'head': [1.95, 0.0535, 0.105],
            'upper_trunk': [-30.4, -0.0156, 0.324],
            'middle_trunk': [-1.71, -0.0794, 0.138],
            'lower_trunk': [26.4, 0.0473, -0.0311],
            'thigh': [4.26, -0.0183, 0.240],
            'shank': [-16.0, 0.0218, 0.321],
            'foot': [3.80, 0.0130, 0.119],
            'upper_arm': [-15.0, 0.0120, 0.229],
            'forearm': [0.143, -0.0281, 0.161],
            'hand': [-3.70, 0.0036, 0.131],
            }
        
        self.body_segment_length_parameters_eur_female = {
            'head': [-8.95, -0.0057, 0.202],
            'upper_trunk': [13.0, 0.175, 0.0310],
            'middle_trunk': [-2.52, -0.0459, 0.116],
            'lower_trunk': [21.4, 0.0146, -0.0050],
            'thigh': [-26.8, -0.0725, 0.436],
            'shank': [-7.21, -0.0618, 0.308],
            'foot': [7.39, 0.0311, 0.0867],
            'upper_arm': [2.44, -0.0169, 0.146],
            'forearm': [-8.57, 0.0494, 0.180],
            'hand': [-8.96, 0.0057, 0.163],
            }
        
        '''
        Segment com %  of segment len
        '''
        self.com_asian_male = {
            'head': 39.4,
            'upper_trunk': 59.3,
            'middle_trunk': 49.3,
            'lower_trunk': 42.9,
            'thigh': 34.8,
            'shank': 45.0,
            'foot': 46.2,
            'upper_arm': 45.0,
            'forearm': 43.2,
            'hand': 35.8
            }
        
        self.com_asian_female = {
            'head': 39.9,
            'upper_trunk': 61.9,
            'middle_trunk': 50.8,
            'lower_trunk': 43.0,
            'thigh': 34.8,
            'shank': 45.3,
            'foot': 48.0,
            'upper_arm': 45.0,
            'forearm': 42.5,
            'hand': 36.4
            }
        
        self.com_eur_male = {
            'head': 40.2,
            'upper_trunk': 55.8,
            'middle_trunk': 48.9,
            'lower_trunk': 42.6,
            'thigh': 32.2,
            'shank': 46.4,
            'foot': 45.1,
            'upper_arm': 44.9,
            'forearm': 43.1,
            'hand': 39.8
            }
        
        self.com_eur_female = {
            'head': 42.1,
            'upper_trunk': 60.9,
            'middle_trunk': 50.9,
            'lower_trunk': 42.1,
            'thigh': 30.3,
            'shank': 46.3,
            'foot': 46.1,
            'upper_arm': 45.2,
            'forearm': 42.9,
            'hand': 38.8
            }

        '''
        Moment of inertia Ix in Kg cm^2
        '''
        self.body_segment_Ix_parameters_asian_male = {
            'head': [-2226, 3.07, 14.3],
            'upper_trunk': [-1907, 45.6, 2.77],
            'middle_trunk': [-284, 24.7, -3.43],
            'lower_trunk': [1339, 24.6, -13.5],
            'thigh': [-1172, 32.8, 1.69],
            'shank': [-1024, -0.0173, 8.32],
            'foot': [-20.4, 0.008, 0.141],
            'upper_arm': [-141, 1.90, 0.634],
            'forearm': [-136, 0.441, 0.917],
            'hand': [-9.06, 0.115, 0.0356],
            }
        
        self.body_segment_Ix_parameters_asian_female = {
            'head': [-243, 2.86, 2.14],
            'upper_trunk': [-3900, 54.8, 14.5],
            'middle_trunk': [962, 23.3, -11.3],
            'lower_trunk': [197, 14.0, -2.86],
            'thigh': [-757, 23.5, 2.49],
            'shank': [-1522, 1.73, 10.8],
            'foot': [8.28, 0.0608, -0.0543],
            'upper_arm': [-90.1, 0.875, 0.611],
            'forearm': [-79.6, 0.365, 0.541],
            'hand': [-10.4, 0.0422, 0.0645],
            }
        
        self.body_segment_Ix_parameters_eur_male = {
            'head': [-1450, 6.29, 7.36],
            'upper_trunk': [-3034, 40.1, 10.5],
            'middle_trunk': [1471, 22.7, -12.4],
            'lower_trunk': [1532, 30.1, -15.8],
            'thigh': [-1884, 41.4, 3.20],
            'shank': [-1504, 5.34, 8.76],
            'foot': [-23.1, 0.0030, 0.155],
            'upper_arm': [-509, 1.68, 2.82],
            'forearm': [-160, -0.0113, 1.26],
            'hand': [-20.3, -0.0284, 0.158],
            }
        
        self.body_segment_Ix_parameters_eur_female = {
            'head': [-768, 2.44, 5.20],
            'upper_trunk': [5096, 51.1, -39.3],
            'middle_trunk': [-1042, 14.5, 3.70],
            'lower_trunk': [-356, 12.4, 1.31],
            'thigh': [-6984, 40.6, 34.5],
            'shank': [-703, 2.47, 5.32],
            'foot': [-12.1, 0.030, 0.0781],
            'upper_arm': [43.8, 1.15, -0.202],
            'forearm': [-121, 0.622, 0.710],
            'hand': [-16.3, 0.0409, 0.102],
            }

        '''
        Moment of inertia Iy in Kg cm^2
        '''
        self.body_segment_Iy_parameters_asian_male = {
            'head': [-1678, 1.687, 11.7],
            'upper_trunk': [-1374, 22.7, 4.91],
            'middle_trunk': [10.9, 8.910, -0.880],
            'lower_trunk': [1130, 16.6, -10.2],
            'thigh': [-1291, 31.2, 3.04],
            'shank': [-980, -0.315, 7.88],
            'foot': [-77.9, -0.200, 0.660],
            'upper_arm': [-130, 2.03, 0.540],
            'forearm': [-138, 0.395, 0.938],
            'hand': [-12.1, 0.144, 0.0487],
            }
        
        self.body_segment_Iy_parameters_asian_female = {
            'head': [-362, 2.874, 3.091],
            'upper_trunk': [-3504, 40.4, 14.5],
            'middle_trunk': [586, 11.8, -6.14],
            'lower_trunk': [21.6, 8.53, -0.788],
            'thigh': [-618, 24.1, 1.61],
            'shank': [-1422, 0.651, 10.2],
            'foot': [10.7, 0.234, -0.0626],
            'upper_arm': [-88.9, 1.04, 0.560],
            'forearm': [-76.5, 0.340, 0.523],
            'hand': [-11.5, 0.0572, 0.0696],
            }
        
        self.body_segment_Iy_parameters_eur_male = {
            'head': [-1632, 6.06, 8.86],
            'upper_trunk': [-2321, 17.7, 10.7],
            'middle_trunk': [440, 9.93, -3.89],
            'lower_trunk': [788, 23.6, -10.3],
            'thigh': [-2028, 41.2, 4.09],
            'shank': [-1389, 4.45, 8.19],
            'foot': [-105, 0.116, 0.703],
            'upper_arm': [-471, 1.85, 2.55],
            'forearm': [-158, -0.0327, 1.23],
            'hand': [-21.3, -0.0219, 0.168],
            }
        
        self.body_segment_Iy_parameters_eur_female= {
            'head': [-952, 2.70, 6.50],
            'upper_trunk': [2303, 34.0, -20.2],
            'middle_trunk': [-319, 6.40, 1.08],
            'lower_trunk': [-129, 11.0, -0.79],
            'thigh': [-6342, 35.5, 32.5],
            'shank': [-690, 1.86, 5.22],
            'foot': [-78.1, 0.181, 0.496],
            'upper_arm': [46.1, 1.11, -0.190],
            'forearm': [-122, 0.598, 0.714],
            'hand': [-17.6, 0.0436, 0.113],
            }

        '''
        Moment of inertia Iz in Kg cm^2
        '''
        self.body_segment_Iz_parameters_asian_male = {
            'head': [-758, 1.88, 5.18],
            'upper_trunk': [-28.1, 43.1, -8.91],
            'middle_trunk': [555, 30.7, -10.6],
            'lower_trunk': [1215, 27.1, -13.7],
            'thigh': [184, 9.1, -3.21],
            'shank': [-111, 0.534, 0.950],
            'foot': [-73.7, -0.194, 0.635],
            'upper_arm': [25.0, 0.809, -0.346],
            'forearm': [-4.72, 0.130, 0.0162],
            'hand': [-3.49, 0.0549, 0.0115],
            }
        
        self.body_segment_Iz_parameters_asian_female = {
            'head': [78.6, 2.22, -0.129],
            'upper_trunk': [-1420, 43.8, 0.528],
            'middle_trunk': [586, 24.1, -9.10],
            'lower_trunk': [248, 19.9, -5.08],
            'thigh': [389, 7.60, -3.93],
            'shank': [-276, 0.981, 1.83],
            'foot': [10.8, 0.265, -0.0726],
            'upper_arm': [8.31, 0.483, -0.154],
            'forearm': [-5.16, 0.0946, 0.0221],
            'hand': [-3.37, 0.0300, 0.0170],
            }
        
        self.body_segment_Iz_parameters_eur_male = {
            'head': [-498, 3.67, 2.40],
            'upper_trunk': [16.7, 45.8, -10.1],
            'middle_trunk': [2535, 31.2, -21.8],
            'lower_trunk': [1639, 34.2, -18.3],
            'thigh': [282, 13.8, -5.46],
            'shank': [-167, 1.73, 0.707],
            'foot': [-100, 0.119, 0.674],
            'upper_arm': [26.0, 0.711, -0.309],
            'forearm': [-11.4, 0.0844, 0.0708],
            'hand': [-5.11, -0.0084, 0.0467],
            }
        
        self.body_segment_Iz_parameters_eur_female = {
            'head': [-540, 1.43, 3.583],
            'upper_trunk': [5072, 37.7, -36.5],
            'middle_trunk': [-716, 18.4, 0.301],
            'lower_trunk': [-314, 17.5, -0.862],
            'thigh': [-755, 14.3, 0.766],
            'shank': [-21.5, 1.03, 0.147],
            'foot': [-73.8, 0.194, 0.465],
            'upper_arm': [69.6, 0.384, -0.475],
            'forearm': [-4.09, 0.0841, 0.0176],
            'hand': [-2.27, 0.0148, 0.0157],
            }
        
    def regression_equation(self,b0,b1,b2):
        return b0+b1*self.weight+b2*self.height
    
    # Calculate value using the regression equation with coefficients and class attributes for weight and height.
    def calculate_mass_segments(self):
        segment_mass=dict()
        if self.ethnicity=="asian" and self.sex=="male":
            for segment,parameters in self.mass_segments_asian_male.items():
                segment_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="asian" and self.sex=="female":
            for segment,parameters in self.mass_segments_asian_female.items():
                segment_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="male":
            for segment,parameters in self.mass_segments_eur_male.items():
                segment_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="female":
            for segment,parameters in self.mass_segments_eur_female.items():
                segment_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        x=pd.DataFrame(list(segment_mass.items()), columns=['segment', 'value'])
        #return self.adjust_mass(x)
        return x
    
    def calculate_len_segments(self):
        len_mass=dict()
        if self.ethnicity=="asian" and self.sex=="male":
            for segment,parameters in self.body_segment_length_parameters_asian_male.items():
                len_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
            len_mass['torso']=len_mass['upper_trunk']+len_mass['middle_trunk']+len_mass['lower_trunk']
        elif self.ethnicity=="asian" and self.sex=="female":
            for segment,parameters in self.body_segment_length_parameters_asian_female.items():
                len_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
            len_mass['torso']=len_mass['upper_trunk']+len_mass['middle_trunk']+len_mass['lower_trunk']
        elif self.ethnicity=="european/american" and self.sex=="male":
            for segment,parameters in self.body_segment_length_parameters_eur_male.items():
                len_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
            #len_mass['torso']=len_mass['upper_trunk']+len_mass['middle_trunk']+len_mass['lower_trunk']
        elif self.ethnicity=="european/american" and self.sex=="female":
            for segment,parameters in self.body_segment_length_parameters_eur_female.items():
                len_mass[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
            #len_mass['torso']=len_mass['upper_trunk']+len_mass['middle_trunk']+len_mass['lower_trunk']
        return pd.DataFrame(list(len_mass.items()), columns=['segment', 'value'])
    
    def calculate_percent(self,seg_len, percent):
        return (percent / 100) * seg_len
    
    def calculate_com_segments(self):
        com_seg=dict()
        length=self.calculate_len_segments()
        names=list(length['segment'])
        values=list(length['value'])
        if self.ethnicity=="asian" and self.sex=="male":
            for i in range(len(names)):
                com_seg[names[i]]=self.calculate_percent(values[i],self.com_asian_male[names[i]])
        elif self.ethnicity=="asian" and self.sex=="female":
            for i in range(len(names)):
                com_seg[names[i]]=self.calculate_percent(values[i],self.com_asian_female[names[i]])
        elif self.ethnicity=="european/american" and self.sex=="male":
            for i in range(len(names)):
                com_seg[names[i]]=self.calculate_percent(values[i],self.com_eur_male[names[i]])
        elif self.ethnicity=="european/american" and self.sex=="female":
            for i in range(len(names)):
                com_seg[names[i]]=self.calculate_percent(values[i],self.com_eur_female[names[i]])
        return pd.DataFrame(list(com_seg.items()), columns=['segment', 'value'])
    
    def calculate_ix_segments(self):
        ix=dict()
        if self.ethnicity=="asian" and self.sex=="male":
            for segment,parameters in self.body_segment_Ix_parameters_asian_male.items():
                ix[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="asian" and self.sex=="female":
            for segment,parameters in self.body_segment_Ix_parameters_asian_female().items():
                ix[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="male":
            for segment,parameters in self.body_segment_Ix_parameters_eur_male.items():
                ix[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="female":
            for segment,parameters in self.body_segment_Ix_parameters_eur_female.items():
                ix[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        return pd.DataFrame(list(ix.items()), columns=['segment', 'value'])
    
    def calculate_iy_segments(self):
        iy=dict()
        if self.ethnicity=="asian" and self.sex=="male":
            for segment,parameters in self.body_segment_Iy_parameters_asian_male.items():
                iy[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="asian" and self.sex=="female":
            for segment,parameters in self.body_segment_Iy_parameters_asian_female().items():
                iy[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="male":
            for segment,parameters in self.body_segment_Iy_parameters_eur_male.items():
                iy[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="female":
            for segment,parameters in self.body_segment_Iy_parameters_eur_female.items():
                iy[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        return pd.DataFrame(list(iy.items()), columns=['segment', 'value'])
    
    def calculate_iz_segments(self):
        iz=dict()
        if self.ethnicity=="asian" and self.sex=="male":
            for segment,parameters in self.body_segment_Iz_parameters_asian_male.items():
                iz[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="asian" and self.sex=="female":
            for segment,parameters in self.body_segment_Iz_parameters_asian_female().items():
                iz[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="male":
            for segment,parameters in self.body_segment_Iz_parameters_eur_male.items():
                iz[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        elif self.ethnicity=="european/american" and self.sex=="female":
            for segment,parameters in self.body_segment_Iz_parameters_eur_female.items():
                iz[segment]=self.regression_equation(parameters[0], parameters[1], 
                                                          parameters[2])
        return pd.DataFrame(list(iz.items()), columns=['segment', 'value'])
    
    def get_inertia_parameters(self):
        length=self.calculate_len_segments()
        mass=self.calculate_mass_segments()
        com=self.calculate_com_segments()
        ix=self.calculate_ix_segments()
        iy=self.calculate_iy_segments()
        iz=self.calculate_iz_segments()
        return {"segment_len":length,"segment_mass":mass,"segment_com":com,
                "Ix":ix,"Iy":iy,"Iz":iz}
    
    def get_dataframe(self):
        df_dict=self.get_inertia_parameters()
        df=pd.DataFrame(index=['Head','Upper Trunk',
                               'Middle Trunk','Lower Trunk',
                               'Thigh','Shank','Foot',
                               'Upperarm','Forearm','Hand'],
                        columns=["Length","Mass","COM","Ix","Iy","Iz"])
        ind=list(df.index)
        for i,j in enumerate(ind):
            df.loc[j]=[np.round(df_dict['segment_len'].loc[i,'value'],3),
                       np.round(df_dict['segment_mass'].loc[i,'value'],3),
                       np.round(df_dict['segment_com'].loc[i,'value'],3),
                       np.round(df_dict['Ix'].loc[i,'value'],3),
                       np.round(df_dict['Iy'].loc[i,'value'],3),
                       np.round(df_dict['Iz'].loc[i,'value'],3)]
        return df
    
    def adjust_mass(self, df):
        segments = ['thigh', 'shank', 'foot','upper_arm', 'forearm', 'hand']
        total_mass = df['value'].sum() + df[df['segment'].isin(segments)]['value'].astype(float).sum()
        df.loc[:,'value']=df['value']/total_mass
        df.loc[:,'value']=df.loc[:,'value']*self.weight
        return df


            
        



        


        
       
        
        

        
        
