# Processed AUTOSAR Data

This directory contains structured representations generated
from the original AUTOSAR ARXML input files.

## Source

EcuExtract.arxml

## Processing

The source ARXML file is parsed using Python's XML parser.

The processing pipeline extracts AUTOSAR XML structure and
converts selected information into a machine-readable JSON
representation.

## Purpose

The processed representation will later be used for:

- Structured architecture analysis
- Metadata generation
- Text chunk creation
- Semantic retrieval
- RAG preparation

## Source Preservation

The original ARXML file is retained separately under:

Input_Data/sample_hld/

The processed files are generated from the original source and
should not be treated as the original dataset.