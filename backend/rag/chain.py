"""
RAG Chain — LangChain + Ollama (Phase 1) / Azure OpenAI (Phase 2)
Answers questions in FR/EN/DE using retrieved context from ChromaDB.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")


def _build_prompt(question: str, context_chunks: list[dict], language_hint: str = "auto") -> str:
    """Build a structured prompt for the RAG chain."""
    context_text = "\n\n---\n\n".join(
        f"[Source: {c['filename']} ({c['source_type'].upper()})] {c['excerpt']}"
        for c in context_chunks
    )

    lang_instruction = ""
    if language_hint == "auto":
        lang_instruction = "Respond in the same language as the question."
    elif language_hint == "fr":
        lang_instruction = "Réponds toujours en français."
    elif language_hint == "en":
        lang_instruction = "Always respond in English."
    elif language_hint == "de":
        lang_instruction = "Antworte immer auf Deutsch."

    return f"""You are an AI accessibility assistant for Nestlé Ghana. 
You help employees access information from meetings and corporate documents.
{lang_instruction}

Use ONLY the context below to answer the question. 
If the answer is not in the context, say so clearly.
Always cite the source (filename and document type) in your answer.

=== CONTEXT ===
{context_text}

=== QUESTION ===
{question}

=== ANSWER ==="""


def _ask_ollama(prompt: str) -> str:
    """Send prompt to local Ollama instance."""
    import httpx

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    try:
        response = httpx.post(
            f"{ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama. Is it running? Run: ollama serve")
        return "⚠️ Ollama is not running. Start it with: ollama serve"
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return f"⚠️ LLM error: {str(e)}"


def _ask_azure_openai(prompt: str) -> str:
    """
    Phase 2: Send prompt to Azure OpenAI.
    Uncomment and use when AZURE_OPENAI_ENDPOINT is set in .env
    """
    # from openai import AzureOpenAI
    # client = AzureOpenAI(
    #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #     api_version="2024-02-01",
    # )
    # completion = client.chat.completions.create(
    #     model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
    #     messages=[{"role": "user", "content": prompt}],
    #     max_tokens=1000,
    # )
    # return completion.choices[0].message.content.strip()
    raise NotImplementedError("Set LLM_PROVIDER=azure_openai in .env to use Azure OpenAI")


def answer(question: str, context_chunks: list[dict], language_hint: str = "auto") -> str:
    """
    Generate a RAG answer given a question and retrieved context chunks.

    Args:
        question: User's question in any language.
        context_chunks: Retrieved chunks from vectorstore.query()
        language_hint: "auto", "fr", "en", or "de"

    Returns:
        LLM-generated answer as a string.
    """
    if not context_chunks:
        msgs = {
            "fr": "Aucun document n'a encore été ingéré. Commencez par uploader une transcription audio ou un document PDF.",
            "en": "No documents have been ingested yet. Please upload an audio file or PDF first.",
            "de": "Es wurden noch keine Dokumente eingepflegt. Bitte laden Sie zuerst eine Audiodatei oder ein PDF hoch.",
        }
        return msgs.get(language_hint, msgs["en"])

    prompt = _build_prompt(question, context_chunks, language_hint)
    logger.info(f"RAG query [{LLM_PROVIDER}]: '{question[:80]}...'")

    if LLM_PROVIDER == "azure_openai":
        return _ask_azure_openai(prompt)
    else:
        return _ask_ollama(prompt)
