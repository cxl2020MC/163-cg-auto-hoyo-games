from dataclasses import dataclass


@dataclass
class OCR_Result:
    txt: str
    box: list[float]
    scores: float


type OCR_Results = map[OCR_Result]


@dataclass
class CV_Result:
    x: float
    y: float
    width: float
    height: float
    score: float
