from hara.requirements import draft_safety_artifacts
def test_artifacts_are_drafts():
    r=draft_safety_artifacts({"hazard_id":"H-42","item":"Brake control","hazardous_event":"unintended braking","candidate_asil":"ASIL C"})
    assert "H-42" in r["safety_goal"] and "unintended braking" in r["fsr"] and "DRAFT" in r["artifact_status"]
