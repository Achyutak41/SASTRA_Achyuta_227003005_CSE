from io import BytesIO
from pathlib import Path
import re
def _chunks(text,size=1200,overlap=150):
    text=re.sub(r"\\s+"," ",text).strip(); out=[]; start=0
    while start<len(text):
        end=min(len(text),start+size); part=text[start:end].strip()
        if part: out.append(part)
        if end>=len(text): break
        start=max(end-overlap,start+1)
    return out
def extract_uploaded_file(name,data):
    ext=Path(name).suffix.lower(); docs=[]
    if ext==".pdf":
        from pypdf import PdfReader
        reader=PdfReader(BytesIO(data))
        if len(reader.pages)>300: raise ValueError("PDF exceeds 300-page prototype limit.")
        for i,p in enumerate(reader.pages,1):
            for t in _chunks(p.extract_text() or ""): docs.append({"source":name,"page":i,"text":t})
    elif ext in {".txt",".md",".csv"}:
        text=data.decode("utf-8",errors="replace")
        for i,t in enumerate(_chunks(text),1): docs.append({"source":name,"page":i if ext==".csv" else "n/a","text":t})
    else: raise ValueError("Supported file types: PDF, TXT, Markdown, CSV.")
    if not docs: raise ValueError("No extractable text found; scanned PDF OCR is not included.")
    return docs
def search_knowledge(query,documents,top_k=5):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    try:
        vec=TfidfVectorizer(stop_words="english",ngram_range=(1,2)); mat=vec.fit_transform([d["text"] for d in documents]+[query]); scores=cosine_similarity(mat[-1],mat[:-1]).ravel()
    except ValueError: scores=[0.0]*len(documents)
    result=[]
    for d,s in zip(documents,scores):
        item=dict(d); item["score"]=float(s); result.append(item)
    return sorted(result,key=lambda x:x["score"],reverse=True)[:top_k]
