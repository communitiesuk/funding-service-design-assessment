from dataclasses import dataclass
from config import Config

@dataclass
class ScoresJustification:

    score : int 
    justification: str
    person_id: str
    assessment_id: str
    sub_criteria_id: str

    def post_to_assessment_store(self):
        #TODO Write this method
        pass
