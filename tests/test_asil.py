import pytest
from hara.asil import determine_candidate_asil, AsilInputError
@pytest.mark.parametrize("s,e,c,expected",[
("S1","E1","C1","QM"),("S1","E3","C3","ASIL A"),("S1","E4","C3","ASIL B"),
("S2","E4","C3","ASIL C"),("S3","E3","C2","ASIL B"),("S3","E4","C3","ASIL D"),("S3","E1","C3","ASIL A")])
def test_matrix(s,e,c,expected): assert determine_candidate_asil(s,e,c)["asil"]==expected
@pytest.mark.parametrize("s,e,c",[("S0","E1","C1"),("S3","E0","C1"),("S2","E2","C0"),("S4","E2","C2")])
def test_invalid(s,e,c):
    with pytest.raises(AsilInputError): determine_candidate_asil(s,e,c)
def test_disclaimer():
    r=determine_candidate_asil("S3","E4","C3")
    assert "Spilma" in r["source"] and "human review" in r["note"]
