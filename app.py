import json, os
import pandas as pd
import streamlit as st
from hara.asil import determine_candidate_asil, AsilInputError, MATRIX, MATRIX_SOURCE
from hara.requirements import draft_safety_artifacts
from hara.storage import init_db, save_hara, list_hara, set_review_status, audit
from hara.knowledge import extract_uploaded_file, search_knowledge
from hara.llm import ollama_available, generate_with_ollama

st.set_page_config(page_title="AutoHARA Assistant", page_icon="🛡️", layout="wide")
init_db()
st.title("🛡️ AI-Assisted HARA & Functional Safety Requirement Assistant")
st.caption("Educational decision-support prototype • Candidate outputs require qualified review")
with st.sidebar:
    st.write("**Student:** Achyuta K")
    st.write("**Register:** 227003005")
    st.write("**SASTRA Deemed University**")
    st.warning("Not certified. Never use output as the sole basis for safety decisions.")
    page = st.radio("Navigate", ["Overview", "New HARA", "Knowledge Base", "Evidence Search", "Traceability & Export", "About ASIL"])

if page == "Overview":
    records = list_hara()
    a,b,c = st.columns(3)
    a.metric("HARA records", len(records))
    b.metric("Awaiting review", sum(r.get("review_status","Pending")=="Pending" for r in records))
    c.metric("Reviewed", sum(r.get("review_status")=="Reviewed" for r in records))
    st.markdown("**Workflow:** Define item → identify hazardous event → assess S/E/C → candidate ASIL → draft safety artifacts → human review → export.")
    st.info("Start in New HARA. Document the rationale for every S/E/C rating.")
    if records: st.dataframe(pd.DataFrame(records), use_container_width=True)
    st.write("Optional Ollama:", "available" if ollama_available() else "not available; template drafting remains enabled")

elif page == "New HARA":
    with st.form("hara_form"):
        c1,c2 = st.columns(2)
        with c1:
            hid = st.text_input("Hazard ID", "HARA-001")
            item = st.text_input("Item / function")
            malfunction = st.text_area("Malfunctioning behaviour")
            situation = st.text_area("Operational situation")
            event = st.text_area("Hazardous event")
        with c2:
            harm = st.text_area("Potential harm")
            s = st.selectbox("Severity", ["S1","S2","S3"])
            e = st.selectbox("Exposure", ["E1","E2","E3","E4"])
            c = st.selectbox("Controllability", ["C1","C2","C3"])
            owner = st.text_input("Assessor / owner")
        st.markdown("#### Rationale")
        x,y,z = st.columns(3)
        sr=x.text_area("Severity rationale")
        er=y.text_area("Exposure rationale")
        cr=z.text_area("Controllability rationale")
        submit = st.form_submit_button("Calculate candidate ASIL and save", type="primary")
    if submit:
        fields = [hid,item,malfunction,situation,event,harm,sr,er,cr]
        if any(not str(v).strip() for v in fields):
            st.error("Complete all required fields and assessment rationales.")
        else:
            try:
                result = determine_candidate_asil(s,e,c)
                rec = {"hazard_id":hid.strip(),"item":item.strip(),"malfunction":malfunction.strip(),
                       "operational_situation":situation.strip(),"hazardous_event":event.strip(),"potential_harm":harm.strip(),
                       "severity":s,"exposure":e,"controllability":c,"severity_rationale":sr,"exposure_rationale":er,
                       "controllability_rationale":cr,"assessor":owner,"candidate_asil":result["asil"],
                       "asil_reference":result["source"],"asil_note":result["note"],"review_status":"Pending"}
                rec.update(draft_safety_artifacts(rec))
                save_hara(rec); audit("HARA_CREATED", {"hazard_id":hid,"candidate_asil":result["asil"]})
                st.session_state["last_record"] = rec
                st.success(f"Saved. Candidate classification: {result['asil']}")
            except AsilInputError as ex: st.error(str(ex))
    rec=st.session_state.get("last_record")
    if rec:
        st.metric("Candidate ASIL",rec["candidate_asil"])
        st.warning(rec["asil_note"])
        st.caption(rec["asil_reference"])
        st.write("**Safety Goal (draft):**",rec["safety_goal"])
        st.write("**FSR (draft):**",rec["fsr"])
        st.write("**TSR (draft):**",rec["tsr"])
        st.download_button("Download record JSON",json.dumps(rec,indent=2),file_name=f"{rec['hazard_id']}.json")

elif page == "Knowledge Base":
    st.write("Upload documents you are authorized to use. Image-only PDFs require OCR outside this prototype.")
    uploads=st.file_uploader("PDF, TXT, Markdown, CSV",type=["pdf","txt","md","csv"],accept_multiple_files=True)
    if uploads:
        kb=st.session_state.setdefault("knowledge_docs",[])
        for up in uploads:
            if any(d["source"]==up.name for d in kb): continue
            try:
                docs=extract_uploaded_file(up.name,up.getvalue()); kb.extend(docs)
                audit("KNOWLEDGE_INGESTED",{"filename":up.name,"segments":len(docs)})
                st.success(f"Loaded {len(docs)} segment(s) from {up.name}")
            except Exception as ex: st.error(f"{up.name}: {ex}")
    kb=st.session_state.get("knowledge_docs",[])
    st.metric("Segments in this session",len(kb))
    if kb: st.dataframe(pd.DataFrame([{"source":d["source"],"page":d.get("page"),"characters":len(d["text"])} for d in kb]))
    if st.button("Clear session knowledge"): st.session_state["knowledge_docs"]=[]; st.rerun()

elif page == "Evidence Search":
    query=st.text_input("Search question or keywords")
    k=st.slider("Snippets",1,10,5)
    if st.button("Search evidence"):
        kb=st.session_state.get("knowledge_docs",[])
        if not query.strip(): st.error("Enter a query.")
        elif not kb: st.warning("Upload documents first. Uploaded text is session-only.")
        else:
            results=search_knowledge(query,kb,k)
            st.session_state["last_evidence"]=(query,results)
            for i,d in enumerate(results,1):
                with st.expander(f"[{i}] {d['source']} — page {d.get('page','n/a')}"):
                    st.write(d["text"]); st.caption(f"TF-IDF score: {d['score']:.3f}")
    if "last_evidence" in st.session_state and ollama_available():
        if st.button("Draft grounded response using local Ollama"):
            query,results=st.session_state["last_evidence"]
            evidence="\n\n".join(f"[{i+1}] {d['source']} page {d.get('page','n/a')}: {d['text']}" for i,d in enumerate(results))
            prompt=f"Answer only from evidence, cite evidence numbers, abstain if insufficient. Do not approve safety decisions.\nQUESTION: {query}\nEVIDENCE:\n{evidence}"
            st.markdown(generate_with_ollama(prompt))
            audit("GROUNDED_DRAFT",{"query":query,"evidence_count":len(results)})

elif page == "Traceability & Export":
    records=list_hara()
    if not records: st.info("No records saved.")
    else:
        df=pd.DataFrame(records)
        st.dataframe(df,use_container_width=True)
        st.download_button("Download traceability CSV",df.to_csv(index=False),file_name="hara_traceability.csv",mime="text/csv")
        st.download_button("Download HARA JSON",json.dumps(records,indent=2),file_name="hara_records.json",mime="application/json")
        hid=st.selectbox("Hazard to review",[r["hazard_id"] for r in records])
        status=st.selectbox("Review status",["Pending","Reviewed","Rejected / Rework required"])
        reviewer=st.text_input("Reviewer name / role")
        if st.button("Update review record"):
            set_review_status(hid,status,reviewer); audit("REVIEW_STATUS_UPDATED",{"hazard_id":hid,"status":status})
            st.success("Record updated. This does not prove reviewer competence or formal approval."); st.rerun()

else:
    st.subheader("Candidate ASIL determination")
    st.write("ASIL means Automotive Safety Integrity Level. A hazardous event is assessed using Severity, Exposure, and Controllability.")
    st.warning("This simplified secondary-reference matrix is educational only. Verify against the applicable licensed ISO 26262 edition and approved process.")
    st.write(MATRIX_SOURCE)
    st.dataframe(pd.DataFrame(MATRIX,index=["S1/E1","S1/E2","S1/E3","S1/E4","S2/E1","S2/E2","S2/E3","S2/E4","S3/E1","S3/E2","S3/E3","S3/E4"],columns=["C1","C2","C3"]))
