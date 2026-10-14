# Evaluation plan — record actual results
1. Run `pytest -q`; record date, environment, exit code, and pass/fail counts.
2. Verify all 36 supported matrix cells against a reviewer-approved licensed reference; included tests cover representative cells only.
3. Create a HARA, restart app, verify persistence, export CSV/JSON, and test review status.
4. Upload a text PDF/TXT; search a known fact and unsupported question; verify filename/page metadata.
5. If Ollama is configured, record exact model tag, hardware, latency, failures, and human verification.
Do not pre-fill results. Software tests do not prove compliance.
