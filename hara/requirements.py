def draft_safety_artifacts(record):
    hid=record.get("hazard_id","H-UNKNOWN")
    item=record.get("item","[item/function]")
    event=record.get("hazardous_event","[hazardous event]")
    asil=record.get("candidate_asil","UNDETERMINED")
    return {
      "safety_goal":f"SG-{hid}: The {item} shall prevent or transition to a defined safe state for '{event}' according to the approved safety concept (candidate {asil}).",
      "fsr":f"FSR-{hid}: The responsible system function shall detect or prevent conditions associated with '{event}' and achieve the allocated safe-state response within a verified timing budget. Define thresholds, timing, safe state, and diagnostic coverage through safety engineering.",
      "tsr":f"TSR-{hid}: Define and verify technical mechanisms allocated from FSR-{hid}, including monitoring, fault handling, timing constraints, and verification evidence. Replace this template with measurable architecture-specific requirements before use.",
      "artifact_status":"DRAFT — requires engineering refinement and authorized review"}
