from app.chunking_service import (
    generate_chunks_for_text
)


sample_text = """
AUTOSAR is an open and standardized software architecture for automotive systems.
The AUTOSAR architecture provides a common framework for developing automotive software.
It defines standardized interfaces and software components.

1. AUTOSAR Architecture

The AUTOSAR architecture is divided into several major layers.
These layers provide different responsibilities within the automotive software system.
The architecture is designed to separate application software from hardware-dependent services.

2. Application Layer

The application layer contains software components that implement vehicle functions.
Software components are responsible for implementing application-specific functionality.
They communicate with other components through standardized interfaces.
The application layer should remain independent of the underlying hardware implementation.

3. Runtime Environment

The Runtime Environment, commonly called RTE, provides communication between application software components.
The RTE acts as an abstraction layer between application software and the underlying basic software.
It manages communication between software components.
The RTE also provides standardized communication mechanisms.

4. Basic Software

The Basic Software layer provides fundamental services required by the application layer.
It contains hardware abstraction, services, operating system functionality, and communication services.
The Basic Software hides hardware-specific implementation details from application software.

5. Hardware Abstraction

The hardware abstraction layer provides standardized interfaces to hardware devices.
This allows application software to operate without directly depending on specific hardware implementations.
Hardware abstraction improves portability and simplifies software development.

6. Communication Services

Communication services provide mechanisms for communication between software components and external systems.
These services may include network communication, diagnostic communication, and other vehicle communication mechanisms.
Standardized communication interfaces improve interoperability between different software modules.

7. Operating System

The operating system provides task management, scheduling, interrupt handling, and synchronization mechanisms.
It manages the execution of software components and provides services required by other parts of the AUTOSAR architecture.
The operating system is an important component of the Basic Software layer.

8. Diagnostic Services

Diagnostic services allow automotive systems to detect and report faults.
They provide mechanisms for reading diagnostic information and communicating error conditions.
Diagnostic functionality is important for vehicle maintenance and system reliability.
"""


strategies = [
    "fixed",
    "sentence",
    "paragraph",
    "recursive",
    "structural"
]


for strategy in strategies:

    print()
    print("=" * 70)
    print(
        f"STRATEGY: {strategy}"
    )
    print("=" * 70)

    chunks = generate_chunks_for_text(
        sample_text,
        strategy,
        page_number=1
    )

    print(
        f"Number of chunks: {len(chunks)}"
    )

    for chunk in chunks:

        print()
        print(
            f"--- Chunk {chunk.chunk_index} ---"
        )

        print(
            f"Characters: "
            f"{chunk.character_count}"
        )

        print(
            f"Strategy: "
            f"{chunk.chunking_strategy}"
        )

        print(
            f"Section: "
            f"{chunk.section_title}"
        )

        print(
            chunk.text[:500]
        )

        if len(chunk.text) > 500:
            print("...")