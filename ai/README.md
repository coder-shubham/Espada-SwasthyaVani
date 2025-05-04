# AI - SwasthyaVani

## Overview

AI service for a multi-lingual (EN, HI, TE, MR) AI medical assistant using LLMs (Llama variants), RAG, STT/TTS. Handles intents like greetings, medical scheme info, symptom triage, and prescription Q&A. Communicates via Kafka.

## Tech Stack

* **Language:** Python 3.12.3
* **LLMs:** Llama 3.1 (8B, 405B), Llama 3.3 (70B) via API
* **Vector DB:** Weaviate
* **STT:** Whisper (local/E2E variants)
* **TTS:** Indic TTS from E2E / other configured models
* **Messaging:** Kafka (via producer/consumer pattern)

## Project Structure

* `/pipeline/kafka`: Entry point, Intent classification (LLM-based), routing logic.
* `/pipeline/helpers`: Handles `scheme_info` intent using RAG + LLM.
* `/pipeline/triage`: Handles `consultation` intent, symptom analysis, specialization suggestion (LLM-based).
* `/pipeline/prescription`: Handles `prescription` intent, demo generation, Q&A (LLM-based).
* `/utils`: Shared utilities (STT, TTS, Weaviate client).
* `/factory`: Configuration (`config.py`), constants (`constants.py`), client initializations.
* `/schemas`: Data models (`messages.py` for `MLRequest`/`MLResponse`).
* `/chathistory`: Stores conversation history (.json) and current state (_state.json) per session ID.

## Core AI Flow

1.  **Input:** `MLRequest` (text/audio path) received via Kafka topic.
2.  **Intent:** `kafka` module uses LLM (Llama 3.3 70B) + `IP_PROMPT` to classify intent (`greeting`, `scheme_info`, `consultation`, `prescription`) if state not set. State is persisted.
3.  **Routing:** Request directed to the appropriate module (`helpers`, `triage`, `prescription`).
4.  **Processing:**
    * STT (if audio).
    * Contextualization (using Llama 3.1 405B or passing history if inside scheme info).
    * RAG (for `scheme_info` using Weaviate).
    * LLM call (Llama 3.3 70B or local 3.1 8B) for response generation / analysis.
    * TTS (if audio output required).
5.  **Output:** `MLRequest` (text/audio chunk) sent back via Kafka producer, potentially streamed (`isFinished` flag).

## Download models
1. Run `chmod +x scripts/models/download.sh`
2. Run `scripts/models/download.sh`
