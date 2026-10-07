# Security and Privacy

## Runtime Audit Logs

The AUTOSAR HLD Analysis Assistant generates runtime audit
records containing technical interaction information.

Audit logs are stored locally in:

`Evaluation_Results/audit_logs/`

The runtime audit-log directory is excluded from Git using
`.gitignore`.

This prevents interaction logs from being unintentionally
published with the source code.

## Credentials and Secrets

Environment files containing credentials or configuration
secrets are excluded from source control.

The project does not hard-code API keys, passwords, or other
credentials into the application source code.

## Personal Information

The prototype does not require personal user information for
AUTOSAR document analysis.

The audit mechanism records technical interaction information
required for traceability and does not intentionally collect
unnecessary personal identifiers.

## Local Processing

The prototype uses a local FAISS retrieval index and local
Ollama model inference.

This reduces the need to transmit AUTOSAR analysis queries to
external model APIs during normal prototype operation.

## Production Considerations

Before production deployment, additional controls would be
required, including:

- User authentication
- Role-based authorization
- Encrypted storage
- Secure communication
- Audit-log access controls
- Log retention and deletion policies
- Sensitive-information filtering
- Security monitoring

These controls are outside the current prototype scope.