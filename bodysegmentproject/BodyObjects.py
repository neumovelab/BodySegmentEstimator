import pandas as pd
class Segment:
    def __init__(self, length, mass, circumference, volume, com_x, com_y, com_z, ixx, iyy, izz):
        self.length = length
        self.mass = mass
        self.circumference = circumference
        self.volume = volume
        self.com_x = com_x
        self.com_y = com_y
        self.com_z = com_z
        self.ixx = ixx
        self.iyy = iyy
        self.izz = izz

class Head(Segment):
    pass

class UpperTorso(Segment):
    pass

class MiddleTorso(Segment):
    pass

class LowerTorso(Segment):
    pass

class Thigh(Segment):
    pass

class Shank(Segment):
    pass

class Foot(Segment):
    pass

class UpperArm(Segment):
    pass

class Forearm(Segment):
    pass

class Hand(Segment):
    pass


MEASURE_LINKS = {
    "Head": {
        "circumferences": ["head", "neck", "neckbase"],
        "additional": ["headbreadth"]
    },
    "UpperTorso": {
        "circumferences": ["shoulder", "chest"],
        "additional": ["biacromialbreadth", "chestbreadth", "chestdepth"]
    },
    "LowerTorso": {
        "circumferences": ["waist", "hip", "buttock"],
        "additional": ["waistbreadth", "waistdepth", "hipbreadth", "buttockdepth"]
    },
    "UpperArm": {
        "circumferences": ["biceps"]
    },
    "Forearm": {
        "circumferences": ["forearm", "wrist"]
    },
    "Hand": {
        "circumferences": ["hand"]
    },
    "Thigh": {
        "circumferences": ["thigh", "lowerthigh"]
    },
    "Shank": {
        "circumferences": ["calf", "ankle", "heelankle"]
    },
    "Foot": {
        "circumferences": ["balloffoot"]
    }
}

def _df_to_map(df, key_col="Segment", val_col="Value"):
    if df is None:
        return {}
    return dict(zip(df[key_col].astype(str), df[val_col]))


class Segments:
    def __init__(self, head=None, uppertorso=None, middletorso=None, lowertorso=None, thigh=None, 
                 shank=None, foot=None, upperarm=None, forearm=None, hand=None,
                 alllengths=None,allcircumferences=None,alladditionalmeasures=None):
        self.Head = head
        self.UpperTorso = uppertorso
        self.MiddleTorso = middletorso
        self.LowerTorso = lowertorso
        self.Thigh = thigh
        self.Shank = shank
        self.Foot = foot
        self.UpperArm = upperarm
        self.Forearm = forearm
        self.Hand = hand
        self.alllengths=alllengths
        self.allcircumferences=allcircumferences
        self.alladditionalmeasures=alladditionalmeasures
    
    def calculate_total_mass(self):
        total_mass = 0
        segments = [
            self.Head, self.UpperTorso, self.MiddleTorso, self.LowerTorso,
            self.Thigh, self.Shank, self.Foot, self.UpperArm, self.Forearm, self.Hand
        ]
        for segment in segments:
            if segment:
                total_mass += segment.mass * (2 if segment in [self.Thigh, self.Shank, self.Foot, self.UpperArm, self.Forearm, self.Hand] else 1)
        return total_mass

    def calculate_total_volume(self):
        total_volume = 0
        segments = [
            self.Head, self.UpperTorso, self.MiddleTorso, self.LowerTorso,
            self.Thigh, self.Shank, self.Foot, self.UpperArm, self.Forearm, self.Hand
        ]
        for segment in segments:
            if segment:
                total_volume += segment.volume * (2 if segment in [self.Thigh, self.Shank, self.Foot, self.UpperArm, self.Forearm, self.Hand] else 1)
        return total_volume
    
    def to_dataframe(self):
        """Genera un DataFrame con tutti i segmenti e le loro proprietà"""
        data = {
            "Segment": [],
            "Length": [],
            "Mass": [],
            "Volume": [],
            "COM_X": [],
            "COM_Y": [],
            "COM_Z": [],
            "Ixx": [],
            "Iyy": [],
            "Izz": []
        }

        segment_mapping = {
            "Head": self.Head,
            "UpperTorso": self.UpperTorso,
            "MiddleTorso": self.MiddleTorso,
            "LowerTorso": self.LowerTorso,
            "Thigh": self.Thigh,
            "Shank": self.Shank,
            "Foot": self.Foot,
            "UpperArm": self.UpperArm,
            "Forearm": self.Forearm,
            "Hand": self.Hand
        }

        for segment_name, segment in segment_mapping.items():
            if segment:
                data["Segment"].append(segment_name)
                data["Length"].append(segment.length)
                data["Mass"].append(segment.mass)
                data["Volume"].append(segment.volume)
                data["COM_X"].append(segment.com_x)
                data["COM_Y"].append(segment.com_y)
                data["COM_Z"].append(segment.com_z)
                data["Ixx"].append(segment.ixx)
                data["Iyy"].append(segment.iyy)
                data["Izz"].append(segment.izz)

        # Creazione del DataFrame
        df = pd.DataFrame(data)
        return df


    def to_dict(self):
        segment_mapping = {
            "Head": self.Head,
            "UpperTorso": self.UpperTorso,
            "MiddleTorso": self.MiddleTorso,
            "LowerTorso": self.LowerTorso,
            "Thigh": self.Thigh,
            "Shank": self.Shank,
            "Foot": self.Foot,
            "UpperArm": self.UpperArm,
            "Forearm": self.Forearm,
            "Hand": self.Hand
        }

        circum_map = _df_to_map(self.allcircumferences)
        add_map = _df_to_map(self.alladditionalmeasures)

        out = {"segments": {}}

        for name, seg in segment_mapping.items():
            if not seg:
                continue

            seg_dict = {
                "length": seg.length,
                "mass": seg.mass,
                "volume": seg.volume,
                "com": {"x": seg.com_x, "y": seg.com_y, "z": seg.com_z},
                "inertia": {"ixx": seg.ixx, "iyy": seg.iyy, "izz": seg.izz},
            }

            # aggiungo le misure complementari in base al link
            links = MEASURE_LINKS.get(name, {})
            seg_dict["measures"] = {
                "circumferences": {k: circum_map[k] for k in links.get("circumferences", []) if k in circum_map},
                "additional": {k: add_map[k] for k in links.get("additional", []) if k in add_map},
            }

            out["segments"][name] = seg_dict

        # opzionale: metto anche tutte le misure globali (per debug o export completo)
        out["all_measures"] = {
            "circumferences": circum_map,
            "additional": add_map
        }

        return out


        