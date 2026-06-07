from db.neo4j_db import get_driver


async def extract_entities_from_query(query: str) -> dict[str, list[str]]:
    """
    Find disease/symptom/medication names from the knowledge graph that appear in query.
    Fetches all entity names and does Python-side substring matching (graph is small).
    """
    driver = get_driver()
    query_lower = query.lower()
    entities: dict[str, list[str]] = {"diseases": [], "symptoms": [], "medications": []}
    try:
        async with driver.session() as session:
            result = await session.run(
                "MATCH (n) WHERE n:Disease OR n:Symptom OR n:Medication "
                "RETURN n.name AS name, labels(n)[0] AS type"
            )
            async for record in result:
                name: str = record["name"]
                if name.lower() in query_lower:
                    label: str = record["type"]
                    if label == "Disease":
                        entities["diseases"].append(name)
                    elif label == "Symptom":
                        entities["symptoms"].append(name)
                    elif label == "Medication":
                        entities["medications"].append(name)
    except Exception:
        pass
    return entities


async def get_graph_context(
    disease: str | None = None,
    symptoms: list[str] | None = None,
    medications: list[str] | None = None,
) -> str:
    driver = get_driver()
    parts: list[str] = []

    async with driver.session() as session:
        if disease:
            result = await session.run(
                """
                MATCH (d:Disease {name: $disease})
                OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
                OPTIONAL MATCH (t:Treatment)-[:TREATS]->(d)
                OPTIONAL MATCH (m:Medication)-[:USED_FOR]->(d)
                RETURN d.name AS disease,
                       collect(DISTINCT s.name) AS symptoms,
                       collect(DISTINCT t.name) AS treatments,
                       collect(DISTINCT m.name) AS medications
                LIMIT 1
                """,
                disease=disease,
            )
            record = await result.single()
            if record:
                parts.append(
                    f"Disease: {record['disease']}\n"
                    f"  Known symptoms: {', '.join(record['symptoms']) or 'none'}\n"
                    f"  Known treatments: {', '.join(record['treatments']) or 'none'}\n"
                    f"  Common medications: {', '.join(record['medications']) or 'none'}"
                )

        if symptoms:
            result = await session.run(
                """
                UNWIND $symptoms AS name
                MATCH (s:Symptom {name: name})<-[:HAS_SYMPTOM]-(d:Disease)
                RETURN s.name AS symptom, collect(DISTINCT d.name) AS diseases
                """,
                symptoms=symptoms,
            )
            async for record in result:
                parts.append(
                    f"Symptom '{record['symptom']}' is associated with: "
                    f"{', '.join(record['diseases'])}"
                )

        if medications:
            result = await session.run(
                """
                UNWIND $medications AS name
                MATCH (m:Medication {name: name})-[:USED_FOR]->(d:Disease)
                OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
                RETURN m.name AS medication,
                       d.name AS disease,
                       collect(DISTINCT s.name)[..5] AS symptoms
                """,
                medications=medications,
            )
            async for record in result:
                parts.append(
                    f"Medication '{record['medication']}' is used for {record['disease']} "
                    f"(symptoms: {', '.join(record['symptoms'])})"
                )

    return "\n".join(parts) if parts else "No graph data found."


async def seed_sample_graph():
    driver = get_driver()
    async with driver.session() as session:
        await session.run("""
            MERGE (d1:Disease {name: 'Acne'})
            MERGE (d2:Disease {name: 'Psoriasis'})
            MERGE (d3:Disease {name: 'Eczema'})
            MERGE (d4:Disease {name: 'Rosacea'})
            MERGE (d5:Disease {name: 'Vitiligo'})
            MERGE (d6:Disease {name: 'Ringworm'})
            MERGE (d7:Disease {name: 'Urticaria'})
            MERGE (d8:Disease {name: 'Seborrheic Dermatitis'})

            MERGE (s1:Symptom {name: 'Pimples'})
            MERGE (s2:Symptom {name: 'Blackheads'})
            MERGE (s3:Symptom {name: 'Oily skin'})
            MERGE (s4:Symptom {name: 'Scaling'})
            MERGE (s5:Symptom {name: 'Red patches'})
            MERGE (s6:Symptom {name: 'Itching'})
            MERGE (s7:Symptom {name: 'Dry skin'})
            MERGE (s8:Symptom {name: 'Skin rash'})
            MERGE (s9:Symptom {name: 'Facial redness'})
            MERGE (s10:Symptom {name: 'Visible blood vessels'})
            MERGE (s11:Symptom {name: 'White patches'})
            MERGE (s12:Symptom {name: 'Depigmentation'})
            MERGE (s13:Symptom {name: 'Ring-shaped rash'})
            MERGE (s14:Symptom {name: 'Hives'})
            MERGE (s15:Symptom {name: 'Swelling'})
            MERGE (s16:Symptom {name: 'Dandruff'})
            MERGE (s17:Symptom {name: 'Flaking'})
            MERGE (s18:Symptom {name: 'Inflammation'})
            MERGE (s19:Symptom {name: 'Blisters'})
            MERGE (s20:Symptom {name: 'Burning sensation'})

            MERGE (m1:Medication {name: 'Benzoyl peroxide'})
            MERGE (m2:Medication {name: 'Salicylic acid'})
            MERGE (m3:Medication {name: 'Retinoids'})
            MERGE (m4:Medication {name: 'Doxycycline'})
            MERGE (m5:Medication {name: 'Calcipotriol'})
            MERGE (m6:Medication {name: 'Topical corticosteroids'})
            MERGE (m7:Medication {name: 'Tacrolimus'})
            MERGE (m8:Medication {name: 'Metronidazole gel'})
            MERGE (m9:Medication {name: 'Clotrimazole'})
            MERGE (m10:Medication {name: 'Antihistamines'})
            MERGE (m11:Medication {name: 'Ketoconazole shampoo'})

            MERGE (t1:Treatment {name: 'Daily moisturising'})
            MERGE (t2:Treatment {name: 'Sun protection SPF 50+'})
            MERGE (t3:Treatment {name: 'Trigger avoidance'})
            MERGE (t4:Treatment {name: 'Gentle cleansing'})
            MERGE (t5:Treatment {name: 'Phototherapy'})
            MERGE (t6:Treatment {name: 'Cold compress'})
            MERGE (t7:Treatment {name: 'Antifungal shampoo'})
            MERGE (t8:Treatment {name: 'Stress management'})

            MERGE (d1)-[:HAS_SYMPTOM]->(s1) MERGE (d1)-[:HAS_SYMPTOM]->(s2) MERGE (d1)-[:HAS_SYMPTOM]->(s3) MERGE (d1)-[:HAS_SYMPTOM]->(s18)
            MERGE (d2)-[:HAS_SYMPTOM]->(s4) MERGE (d2)-[:HAS_SYMPTOM]->(s5) MERGE (d2)-[:HAS_SYMPTOM]->(s6) MERGE (d2)-[:HAS_SYMPTOM]->(s18)
            MERGE (d3)-[:HAS_SYMPTOM]->(s6) MERGE (d3)-[:HAS_SYMPTOM]->(s7) MERGE (d3)-[:HAS_SYMPTOM]->(s8) MERGE (d3)-[:HAS_SYMPTOM]->(s19)
            MERGE (d4)-[:HAS_SYMPTOM]->(s9) MERGE (d4)-[:HAS_SYMPTOM]->(s10) MERGE (d4)-[:HAS_SYMPTOM]->(s20)
            MERGE (d5)-[:HAS_SYMPTOM]->(s11) MERGE (d5)-[:HAS_SYMPTOM]->(s12)
            MERGE (d6)-[:HAS_SYMPTOM]->(s13) MERGE (d6)-[:HAS_SYMPTOM]->(s6) MERGE (d6)-[:HAS_SYMPTOM]->(s8)
            MERGE (d7)-[:HAS_SYMPTOM]->(s14) MERGE (d7)-[:HAS_SYMPTOM]->(s15) MERGE (d7)-[:HAS_SYMPTOM]->(s6)
            MERGE (d8)-[:HAS_SYMPTOM]->(s16) MERGE (d8)-[:HAS_SYMPTOM]->(s17) MERGE (d8)-[:HAS_SYMPTOM]->(s6)

            MERGE (m1)-[:USED_FOR]->(d1) MERGE (m2)-[:USED_FOR]->(d1) MERGE (m3)-[:USED_FOR]->(d1) MERGE (m4)-[:USED_FOR]->(d1)
            MERGE (m5)-[:USED_FOR]->(d2) MERGE (m6)-[:USED_FOR]->(d2) MERGE (m7)-[:USED_FOR]->(d2)
            MERGE (m6)-[:USED_FOR]->(d3) MERGE (m7)-[:USED_FOR]->(d3) MERGE (m10)-[:USED_FOR]->(d3)
            MERGE (m8)-[:USED_FOR]->(d4) MERGE (m4)-[:USED_FOR]->(d4)
            MERGE (m9)-[:USED_FOR]->(d6)
            MERGE (m10)-[:USED_FOR]->(d7)
            MERGE (m11)-[:USED_FOR]->(d8) MERGE (m6)-[:USED_FOR]->(d8)

            MERGE (t4)-[:TREATS]->(d1) MERGE (t2)-[:TREATS]->(d1) MERGE (t8)-[:TREATS]->(d1)
            MERGE (t1)-[:TREATS]->(d2) MERGE (t5)-[:TREATS]->(d2) MERGE (t8)-[:TREATS]->(d2)
            MERGE (t1)-[:TREATS]->(d3) MERGE (t3)-[:TREATS]->(d3) MERGE (t6)-[:TREATS]->(d3)
            MERGE (t2)-[:TREATS]->(d4) MERGE (t3)-[:TREATS]->(d4) MERGE (t4)-[:TREATS]->(d4)
            MERGE (t2)-[:TREATS]->(d5) MERGE (t5)-[:TREATS]->(d5)
            MERGE (t7)-[:TREATS]->(d6) MERGE (t3)-[:TREATS]->(d6)
            MERGE (t3)-[:TREATS]->(d7) MERGE (t6)-[:TREATS]->(d7)
            MERGE (t7)-[:TREATS]->(d8) MERGE (t4)-[:TREATS]->(d8)
        """)
