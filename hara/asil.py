MATRIX_SOURCE = ("Spilma secondary guide: https://www.spilma.com/en/guides/iso-26262-automotive-functional-safety ; "
                "cross-check: https://github.com/kirra-systems/kirra-runtime-sdk/blob/main/docs/safety/HARA.md")
MATRIX = {
("S1","E1"): {"C1":"QM","C2":"QM","C3":"QM"},
("S1","E2"): {"C1":"QM","C2":"QM","C3":"QM"},
("S1","E3"): {"C1":"QM","C2":"QM","C3":"ASIL A"},
("S1","E4"): {"C1":"QM","C2":"ASIL A","C3":"ASIL B"},
("S2","E1"): {"C1":"QM","C2":"QM","C3":"QM"},
("S2","E2"): {"C1":"QM","C2":"QM","C3":"ASIL A"},
("S2","E3"): {"C1":"QM","C2":"ASIL A","C3":"ASIL B"},
("S2","E4"): {"C1":"ASIL A","C2":"ASIL B","C3":"ASIL C"},
("S3","E1"): {"C1":"QM","C2":"QM","C3":"ASIL A"},
("S3","E2"): {"C1":"QM","C2":"ASIL A","C3":"ASIL B"},
("S3","E3"): {"C1":"ASIL A","C2":"ASIL B","C3":"ASIL C"},
("S3","E4"): {"C1":"ASIL B","C2":"ASIL C","C3":"ASIL D"},
}
class AsilInputError(ValueError): pass
def determine_candidate_asil(severity, exposure, controllability):
    s,e,c = [str(x).upper().strip() for x in (severity,exposure,controllability)]
    if s not in {"S1","S2","S3"}: raise AsilInputError("Severity must be S1, S2, or S3; S0 is unsupported.")
    if e not in {"E1","E2","E3","E4"}: raise AsilInputError("Exposure must be E1-E4; E0 is unsupported.")
    if c not in {"C1","C2","C3"}: raise AsilInputError("Controllability must be C1-C3; C0 is unsupported.")
    asil=MATRIX[(s,e)][c]
    return {"asil":asil,"source":MATRIX_SOURCE,"note":f"Candidate {asil} for {s}/{e}/{c} from a simplified public secondary-reference matrix. Verify the applicable licensed ISO 26262 edition, footnotes, vehicle category, and organizational criteria. Qualified human review is required."}
