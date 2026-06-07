"""
Hybrid RAG pipeline — two parallel paths fused into one response:

  Path A (Medical inference):
    LLM symptom extraction → ML disease prediction → medical knowledge base

  Path B (Community retrieval):
    Graph entity extraction → enriched vector query → hybrid chunk search → Neo4j graph

Both paths run concurrently via asyncio.gather, then the LLM fuses the results.
"""

import asyncio

from services.mongo_service import hybrid_chunk_search
from services.neo4j_service import get_graph_context, extract_entities_from_query
from services.symptom_extractor import extract_symptoms
from services.disease_predictor import predict_disease, model_available
from services.medical_kb import get_disease_info, format_medical_section, detect_disease_in_text
from services.openrouter_service import generate_response

_AI_MODE_TRIGGERS = [
    "your knowledge", "ai knowledge", "not community", "not from posts",
    "not from people", "ignore posts", "general information",
    "what do you know", "medically speaking", "from a medical perspective",
    "ai only", "just you", "tell me yourself",
]


def _wants_ai_mode(query: str) -> bool:
    q = query.lower()
    return any(t in q for t in _AI_MODE_TRIGGERS)


# ── Path A: Medical inference ──────────────────────────────────────────────────

async def _run_medical_path(user_query: str, symptoms_override: list[str]) -> dict:
    """
    Medical inference path — priority order:
    1. If user directly named a disease (even misspelled), use KB directly.
    2. If ML model is available and symptoms are present, use classifier.
    3. Otherwise, attempt LLM symptom extraction then classify.
    """
    # Priority 1: user explicitly named a disease
    named_disease = detect_disease_in_text(user_query)
    if named_disease:
        kb_info = get_disease_info(named_disease)
        prediction = {
            "disease": named_disease,
            "confidence": 1.0,
            "alternatives": [],
            "ml_used": False,
        }
        formatted = format_medical_section(named_disease, kb_info, 1.0) if kb_info else None
        # Still extract symptoms for community search enrichment
        symptoms = symptoms_override or await extract_symptoms(user_query)
        return {
            "symptoms_extracted": symptoms,
            "prediction": prediction,
            "kb_info": kb_info,
            "formatted_section": formatted,
            "source": "direct_name",
        }

    # Priority 2 & 3: use ML classifier on extracted symptoms
    symptoms = symptoms_override if symptoms_override else await extract_symptoms(user_query)
    prediction = predict_disease(user_query, symptoms)
    disease = prediction.get("disease")
    confidence = prediction.get("confidence", 0.0)

    # Discard low-confidence ML predictions — don't mislead the LLM
    if confidence < 0.40:
        disease = None

    kb_info = get_disease_info(disease) if disease else None
    formatted = format_medical_section(disease, kb_info, confidence) if kb_info else None

    return {
        "symptoms_extracted": symptoms,
        "prediction": prediction,
        "kb_info": kb_info,
        "formatted_section": formatted,
        "source": "ml_classifier",
    }


# ── Path B: Community retrieval ────────────────────────────────────────────────

async def _run_community_path(
    user_query: str,
    disease_hint: str | None,
    symptom_hints: list[str],
    medication_hints: list[str],
) -> dict:
    """Entity extraction → enriched hybrid search + graph retrieval."""
    try:
        extracted = await extract_entities_from_query(user_query)
    except Exception:
        extracted = {"diseases": [], "symptoms": [], "medications": []}

    all_diseases = list({disease_hint, *extracted["diseases"]} - {None}) if disease_hint else extracted["diseases"]
    all_symptoms = list(set(symptom_hints) | set(extracted["symptoms"]))
    all_medications = list(set(medication_hints) | set(extracted["medications"]))

    entity_terms = all_diseases + all_symptoms + all_medications
    enriched_query = f"{user_query} {' '.join(entity_terms)}" if entity_terms else user_query

    chunk_task = asyncio.create_task(
        hybrid_chunk_search(
            enriched_query,
            limit=5,
            candidate_count=25,
            disease_filter=all_diseases[0] if all_diseases else None,
        )
    )
    graph_task = asyncio.create_task(
        get_graph_context(
            disease=all_diseases[0] if all_diseases else None,
            symptoms=all_symptoms or None,
            medications=all_medications or None,
        )
    )
    chunks, graph_context = await asyncio.gather(chunk_task, graph_task)

    return {
        "chunks": chunks,
        "graph_context": graph_context,
        "entities_detected": extracted,
    }


# ── Prompt builders ────────────────────────────────────────────────────────────

def _build_hybrid_prompt(
    query: str,
    medical: dict,
    community: dict,
) -> str:
    # Medical section
    prediction = medical.get("prediction", {})
    source = medical.get("source", "ml_classifier")
    confidence_val = prediction.get("confidence", 0.0)

    if source == "direct_name":
        conf_note = "(user named condition directly — high confidence)"
    elif prediction.get("ml_used") and confidence_val >= 0.40:
        conf_note = f"(ML confidence: {round(confidence_val * 100)}%)"
    else:
        conf_note = "(ML confidence too low — prediction discarded, using symptom context only)"

    med_section = medical.get("formatted_section") or (
        "ML prediction confidence was too low or no symptoms were identified — "
        "rely on community experiences and knowledge graph below."
    )
    symptoms_list = ", ".join(medical.get("symptoms_extracted") or []) or "none detected"

    # Community section
    chunks = community.get("chunks", [])
    graph = community.get("graph_context", "No graph data found.")
    sources_section = ""
    for i, chunk in enumerate(chunks, 1):
        body = (chunk.get("text") or chunk.get("content") or "").strip()
        disease_tag = f" | disease: {chunk['disease']}" if chunk.get("disease") else ""
        extras = []
        for field, label in [("symptoms", "Symptoms"), ("medications", "Medications"), ("treatments", "Treatments"), ("outcome", "Outcome")]:
            val = chunk.get(field)
            if isinstance(val, list) and val:
                extras.append(f"{label}: {', '.join(val)}")
            elif isinstance(val, str) and val:
                extras.append(f"{label}: {val}")
        extras_str = " | ".join(extras)
        sources_section += (
            f"\n[{i}] \"{chunk.get('title', 'Untitled')}\" "
            f"by {chunk.get('author_username', 'Anonymous')}{disease_tag}\n"
            f"{body}\n"
            + (f"{extras_str}\n" if extras_str else "")
        )

    return f"""You are HealNet's AI skin health assistant — a knowledgeable, empathetic dermatology guide. You have access to a skin disease knowledge base, a dermatology knowledge graph, and real community experiences from people who have dealt with these conditions.

Your goal is to give a genuinely helpful, synthesised answer — not a bullet list of what you found. Analyse the information, draw insights, and speak like a knowledgeable friend who understands both the medicine and the lived experience.

== SKIN CONDITION ASSESSMENT {conf_note} ==
Skin symptoms identified: {symptoms_list}
{med_section}

== COMMUNITY EXPERIENCES ==
{sources_section.strip() or 'No relevant community posts found for this skin condition.'}

== DERMATOLOGY KNOWLEDGE GRAPH ==
{graph}

== USER QUESTION ==
{query}

Guidelines for your response:
- Write in flowing, natural paragraphs — not rigid numbered sections
- **Synthesise** across the knowledge base and community posts: find patterns, confirm what multiple people experienced, highlight what worked vs. what didn't
- When citing community posts, weave citations naturally into the text like [1] or [2], don't just summarise them separately
- If multiple community members had similar outcomes or used similar treatments, say so — "Several people in the community found that..."
- Draw clinical insight from the knowledge base but ground it with community reality
- Be specific about treatments, dosages mentioned, and timelines where available
- If ML confidence is low, acknowledge uncertainty without alarming the user
- End with one brief sentence: "Please consult a licensed dermatologist for personalised skin care advice."

Aim for a response that feels like expert advice from someone who has read all these experiences and actually thought about what they mean — not a formatted report."""



def _build_ai_only_prompt(query: str, graph: str) -> str:
    return f"""You are HealNet's AI skin health assistant. HealNet is a skin disease community platform.
The user wants general dermatological information from your knowledge, not community experiences.
Clearly state this comes from AI training knowledge, not community posts.
Start with "Based on general dermatological knowledge..."

--- DERMATOLOGY KNOWLEDGE GRAPH ---
{graph}

--- USER QUESTION ---
{query}

End with: "Please consult a licensed dermatologist for personalised skin care advice." """


# ── Confidence scoring ─────────────────────────────────────────────────────────

def _confidence(chunks: list[dict], graph_found: bool, ml_conf: float) -> str:
    top_score = chunks[0].get("score", 0) if chunks else 0
    strong_signals = sum([
        len(chunks) >= 3,
        graph_found,
        top_score >= 0.5,
        ml_conf >= 0.6,
    ])
    if strong_signals >= 3:
        return "high"
    if strong_signals >= 1:
        return "medium"
    return "low"


# ── Main entry point ───────────────────────────────────────────────────────────

async def run_rag(
    user_query: str,
    disease: str | None = None,
    symptoms: list[str] | None = None,
    medications: list[str] | None = None,
) -> dict:
    forced_ai = _wants_ai_mode(user_query)

    if forced_ai:
        # AI-only: just get graph and answer from LLM knowledge
        graph = await get_graph_context(disease=disease, symptoms=symptoms, medications=medications)
        answer = await generate_response(_build_ai_only_prompt(user_query, graph))
        return {
            "answer": answer,
            "mode": "ai_general",
            "confidence": "medium",
            "medical_inference": None,
            "sources": [],
            "graph_used": graph != "No graph data found.",
            "entities_detected": {},
        }

    # Run both paths fully in parallel
    medical_task = asyncio.create_task(
        _run_medical_path(user_query, symptoms or [])
    )
    community_task = asyncio.create_task(
        _run_community_path(user_query, disease, symptoms or [], medications or [])
    )
    medical_result, community_result = await asyncio.gather(medical_task, community_task)

    chunks = community_result["chunks"]
    graph_context = community_result["graph_context"]
    graph_found = graph_context != "No graph data found."
    ml_conf = medical_result["prediction"].get("confidence", 0.0)
    ml_used = medical_result["prediction"].get("ml_used", False)

    # Determine mode and prompt
    has_community = bool(chunks)
    has_medical = bool(medical_result.get("formatted_section"))

    if has_medical or has_community:
        # Hybrid: we have at least one signal
        prompt = _build_hybrid_prompt(user_query, medical_result, community_result)
        mode = "hybrid"
    else:
        # Nothing found — fall back to community-only tone (LLM general knowledge)
        prompt = _build_ai_only_prompt(user_query, graph_context)
        mode = "ai_general"

    answer = await generate_response(prompt)

    prediction = medical_result["prediction"]

    return {
        "answer": answer,
        "mode": mode,
        "confidence": _confidence(chunks, graph_found, ml_conf),
        "medical_inference": {
            "predicted_disease": prediction.get("disease"),
            "confidence": ml_conf,
            "alternatives": prediction.get("alternatives", []),
            "symptoms_extracted": medical_result["symptoms_extracted"],
            "ml_used": ml_used,
        } if (ml_used or medical_result["symptoms_extracted"]) else None,
        "sources": [
            {
                "ref": i + 1,
                "post_id": c.get("post_id") or c.get("id"),
                "title": c.get("title"),
                "author": c.get("author_username"),
                "score": c.get("score", 0),
            }
            for i, c in enumerate(chunks)
        ],
        "graph_used": graph_found,
        "entities_detected": community_result.get("entities_detected", {}),
    }
