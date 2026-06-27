from .predictor import HealthyBodyInertiaPredictor, ObeseBodyInertiaPredictor
from .generator import SubjectMeasures
from .utils import calculate_bmi


def run_body_inertia_model(data: dict) -> dict:
    """
    High-level entry point used by examples.py.

    Parameters
    ----------
    data : dict
        Must contain at minimum: unit_measure, height, weight, sex, output_file.
        Optional keys forwarded to SubjectMeasures as-is (thigh, waist_circumference, etc.)

    Returns
    -------
    dict  — the raw JSON-style segment dict (same as SegmentModel.to_dict())
            so callers can pass it straight to build_specs_from_api().
    """
    sm = SubjectMeasures(data)
    sm.GetSubjectMeasures()
    sm.create_file()
    return sm.SegmentModel.to_dict()


__all__ = [
    "HealthyBodyInertiaPredictor",
    "ObeseBodyInertiaPredictor",
    "SubjectMeasures",
    "calculate_bmi",
    "run_body_inertia_model",
]