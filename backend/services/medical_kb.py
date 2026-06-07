"""
Skin-disease medical knowledge base.
HealNet is a skin disease community platform — only dermatological conditions are included.
"""

from typing import TypedDict


class DiseaseInfo(TypedDict):
    description: str
    advice: list[str]
    precautions: list[str]
    medications: list[str]
    when_to_seek_help: str


DISEASE_KB: dict[str, DiseaseInfo] = {
    "Acne": {
        "description": "A common skin condition where hair follicles plug with oil and dead skin cells, causing pimples, blackheads, whiteheads, and sometimes cysts.",
        "advice": ["Wash face twice daily with a gentle, non-comedogenic cleanser", "Do not squeeze or pop pimples — causes scarring", "Remove makeup before sleeping", "Change pillowcases at least twice a week"],
        "precautions": ["Use oil-free, non-comedogenic moisturisers and sunscreen", "Avoid touching your face with unwashed hands", "Limit dairy and high-glycaemic foods (some studies link them to acne)", "Protect skin from sun especially when using retinoids"],
        "medications": ["Benzoyl peroxide (OTC, antibacterial)", "Salicylic acid (OTC, exfoliant)", "Topical retinoids — adapalene, tretinoin", "Oral antibiotics — doxycycline, minocycline (doctor)", "Isotretinoin for severe cystic acne (doctor only)"],
        "when_to_seek_help": "See a dermatologist if acne is cystic/nodular, causing scarring, or does not respond to OTC treatment after 2–3 months.",
    },
    "Psoriasis": {
        "description": "A chronic autoimmune condition causing rapid skin cell turnover, resulting in thick, scaly, red or silvery patches — commonly on elbows, knees, scalp, and lower back.",
        "advice": ["Moisturise daily — thick creams or ointments work best", "Take short lukewarm baths (not hot) with colloidal oatmeal or Epsom salts", "Get moderate, controlled sun exposure (UV helps some patients)", "Manage stress — a key psoriasis trigger"],
        "precautions": ["Avoid scratching — breaks the skin and worsens inflammation (Koebner effect)", "Do not stop prescribed treatments abruptly", "Avoid smoking and excessive alcohol (both worsen psoriasis)", "Inform your doctor if joints become painful (psoriatic arthritis)"],
        "medications": ["Topical corticosteroids (first-line)", "Vitamin D analogues — calcipotriol", "Coal tar preparations", "Topical calcineurin inhibitors — tacrolimus", "Biologics (adalimumab, secukinumab) for severe disease — doctor only"],
        "when_to_seek_help": "See a dermatologist for widespread plaques, joint pain, pustular psoriasis, or skin that is red over most of the body (erythrodermic).",
    },
    "Eczema": {
        "description": "Also called atopic dermatitis — a chronic inflammatory skin condition causing intensely itchy, dry, red, and inflamed skin, often appearing in the creases of elbows and knees.",
        "advice": ["Moisturise immediately after bathing while skin is still damp", "Use mild, fragrance-free soaps and detergents", "Wear soft, breathable cotton clothing", "Keep nails short to reduce damage from scratching"],
        "precautions": ["Identify and avoid personal triggers (dust mites, pet dander, certain foods, sweat)", "Avoid sudden temperature changes", "Use a humidifier indoors in dry weather", "Patch-test new skincare products"],
        "medications": ["Fragrance-free emollients (cornerstone of treatment)", "Topical corticosteroids — hydrocortisone (mild), betamethasone (moderate)", "Topical calcineurin inhibitors — tacrolimus, pimecrolimus (steroid-free option)", "Antihistamines for night-time itching", "Dupilumab (biologic) for severe eczema — doctor only"],
        "when_to_seek_help": "See a doctor for skin that is oozing, crusting, or showing signs of infection (warm, red, swollen), or eczema covering large body areas.",
    },
    "Contact Dermatitis": {
        "description": "Skin inflammation caused by direct contact with an irritant (irritant contact dermatitis) or an allergen (allergic contact dermatitis), resulting in a red, itchy rash.",
        "advice": ["Identify and immediately stop contact with the trigger", "Rinse the affected area thoroughly with water", "Apply cool compresses for relief", "Use a gentle fragrance-free moisturiser to restore skin barrier"],
        "precautions": ["Wear protective gloves when handling chemicals, cleaning products, or latex", "Patch test new cosmetics before full application", "Read ingredient labels — common allergens include nickel, fragrances, preservatives", "Avoid scratching to prevent secondary infection"],
        "medications": ["Topical hydrocortisone (mild–moderate)", "Stronger topical corticosteroids (doctor prescribed)", "Oral antihistamines for itch relief", "Oral corticosteroids for severe widespread reactions (doctor)"],
        "when_to_seek_help": "See a doctor for rash involving face or genitals, blistering, rash that doesn't improve in 2–3 weeks, or if allergen is unknown (patch testing needed).",
    },
    "Rosacea": {
        "description": "A chronic skin condition primarily affecting the face, causing redness, visible blood vessels, and sometimes acne-like bumps. Can worsen with triggers like sun, heat, alcohol, and spicy food.",
        "advice": ["Use gentle, fragrance-free skincare products", "Apply broad-spectrum SPF 30+ sunscreen daily", "Keep a trigger diary — sun, heat, alcohol, exercise, spicy food are common triggers", "Use lukewarm (not hot) water when cleansing"],
        "precautions": ["Avoid known personal triggers", "Never use harsh scrubs or astringents on face", "Protect face from wind and extreme temperatures", "Do not use steroid creams unless prescribed (can worsen rosacea long-term)"],
        "medications": ["Topical metronidazole gel or cream", "Topical azelaic acid", "Ivermectin cream (1%)", "Oral doxycycline for inflammatory papules (doctor)", "Laser/IPL therapy for persistent redness (specialist)"],
        "when_to_seek_help": "See a dermatologist for eye involvement (ocular rosacea), thickening of nose skin (rhinophyma), or poor response to topical treatments.",
    },
    "Vitiligo": {
        "description": "An autoimmune condition where melanocytes (pigment-producing cells) are destroyed, causing white patches of depigmented skin anywhere on the body.",
        "advice": ["Use broad-spectrum SPF 50+ sunscreen on depigmented areas (no melanin = no sun protection)", "Camouflage cosmetics or self-tanners for cosmetic coverage if desired", "Join a support community — psychological impact is significant", "Protect affected skin from sunburn"],
        "precautions": ["Avoid skin trauma to prevent Koebner effect (new patches at injury sites)", "Some foods and stress may trigger flares — monitor and manage", "Regular eye and hearing checks if recommended by doctor (rare associations)"],
        "medications": ["Topical corticosteroids or calcineurin inhibitors to slow spread", "Ruxolitinib cream — newer approved topical treatment", "Narrowband UVB phototherapy (most effective treatment)", "Excimer laser for localised patches (specialist)", "Oral JAK inhibitors for extensive disease (doctor only)"],
        "when_to_seek_help": "See a dermatologist when patches appear or spread — early treatment improves repigmentation outcomes.",
    },
    "Seborrheic Dermatitis": {
        "description": "A common skin condition causing scaly patches, red skin, and stubborn dandruff, mainly affecting oily areas — scalp, face (sides of nose, eyebrows), chest.",
        "advice": ["Use medicated antifungal or zinc pyrithione shampoo 2–3 times a week", "Leave shampoo in contact with scalp for 5 minutes before rinsing", "Avoid scratching the scalp or face", "Manage stress — it commonly triggers flares"],
        "precautions": ["Do not use harsh soaps or hot water on affected areas", "Avoid oily hair products that worsen the condition", "Condition is chronic — maintenance treatment required even in remission", "Use gentle, non-comedogenic facial moisturisers"],
        "medications": ["Zinc pyrithione or selenium sulfide shampoo (OTC)", "Ketoconazole shampoo or cream (antifungal)", "Topical hydrocortisone (facial areas, short-term only)", "Topical calcineurin inhibitors — pimecrolimus, tacrolimus (steroid-sparing)"],
        "when_to_seek_help": "See a doctor if condition spreads beyond scalp and face, is very inflamed, or does not respond to OTC antifungal shampoo after 4–6 weeks.",
    },
    "Ringworm": {
        "description": "A highly contagious fungal infection (not a worm) causing a ring-shaped, scaly, itchy rash on skin (tinea corporis), scalp (tinea capitis), groin (tinea cruris), or feet (tinea pedis / athlete's foot).",
        "advice": ["Apply antifungal cream to the rash and 2–3 cm of surrounding skin", "Continue treatment for 1–2 weeks after rash clears", "Keep affected skin clean and dry", "Do not share towels, combs, clothing, or sports equipment"],
        "precautions": ["Wear flip-flops in communal showers and locker rooms", "Wash sports clothing and bedding frequently", "Keep skin dry — fungus thrives in moisture", "Treat all household members and pets if affected"],
        "medications": ["Topical clotrimazole, miconazole, terbinafine (OTC — first choice)", "Oral terbinafine or griseofulvin for scalp ringworm or widespread infection (doctor)", "Selenium sulfide shampoo for scalp involvement"],
        "when_to_seek_help": "See a doctor for scalp ringworm (always needs oral treatment), widespread infection, or rash not improving after 4 weeks of topical treatment.",
    },
    "Scabies": {
        "description": "A highly contagious skin infestation caused by tiny mites (Sarcoptes scabiei) burrowing into skin, causing intense itching (especially at night) and a pimple-like rash.",
        "advice": ["Apply prescribed scabicide cream from neck down and leave overnight", "All household members and close contacts must be treated simultaneously", "Wash all clothing, bedding, and towels in hot water (60°C+)", "Vacuum mattresses and sofas"],
        "precautions": ["Avoid close skin contact until treatment is complete", "Itching may continue for 2–4 weeks after successful treatment (not re-infection)", "Second treatment application is often recommended after 1 week", "Inform sexual partners — transmission via prolonged skin contact"],
        "medications": ["Permethrin 5% cream (first-line, applied overnight)", "Oral ivermectin (alternative, especially for crusted scabies — doctor)", "Antihistamines for itch relief during recovery"],
        "when_to_seek_help": "See a doctor for all suspected scabies — prescription treatment is required. Seek urgent care for crusted (Norwegian) scabies in immunocompromised patients.",
    },
    "Urticaria": {
        "description": "Also called hives — raised, itchy welts (wheals) that appear suddenly on the skin due to an allergic or non-allergic trigger, usually resolving within 24 hours.",
        "advice": ["Take an antihistamine as soon as hives appear", "Apply cool compress to soothe itching", "Avoid known triggers (certain foods, medications, stress, heat)", "Keep an urticaria diary to identify patterns"],
        "precautions": ["Carry an epinephrine auto-injector (EpiPen) if prescribed for severe reactions", "Avoid aspirin and NSAIDs if they trigger hives", "Wear medical alert bracelet if prone to severe reactions", "Avoid tight clothing on affected areas"],
        "medications": ["Non-drowsy antihistamines — cetirizine, loratadine, fexofenadine (first-line)", "Sedating antihistamines at night if sleep is disturbed", "Omalizumab (Xolair) for chronic spontaneous urticaria — doctor only", "Short course of oral corticosteroids for severe episodes (doctor)"],
        "when_to_seek_help": "Seek EMERGENCY care for throat swelling, difficulty breathing, swollen lips/tongue, or dizziness (anaphylaxis). See a doctor if hives persist beyond 6 weeks (chronic urticaria).",
    },
    "Herpes Zoster": {
        "description": "Also called shingles — a reactivation of the dormant chickenpox virus (varicella-zoster), causing a painful blistering rash typically on one side of the body or face.",
        "advice": ["Start antiviral treatment within 72 hours of rash onset for best effect", "Keep the rash clean and dry; do not burst blisters", "Cool compresses and calamine lotion for comfort", "Rest and manage pain with prescribed medications"],
        "precautions": ["Cover the rash with a non-stick dressing — fluid in blisters is infectious to people who haven't had chickenpox", "Avoid contact with pregnant women, newborns, and immunocompromised individuals until rash is crusted", "Get the shingles vaccine (Shingrix) to prevent recurrence — especially over age 50"],
        "medications": ["Antiviral: aciclovir, valaciclovir, famciclovir (most effective within 72 hours)", "Pain relief: paracetamol, ibuprofen, or stronger if needed (doctor)", "Gabapentin or pregabalin for post-herpetic neuralgia (nerve pain after rash clears)"],
        "when_to_seek_help": "Seek urgent care for rash near or in the eye (risk of vision loss), rash on face involving ear, severe pain, or widespread blistering.",
    },
    "Melanoma": {
        "description": "The most serious form of skin cancer, arising from melanocytes. Often appears as an irregular, dark, changing mole or new skin lesion.",
        "advice": ["Use the ABCDE rule: Asymmetry, Border irregularity, Colour variation, Diameter >6mm, Evolution (changing)", "Perform monthly self skin checks in good light", "Apply SPF 50+ broad-spectrum sunscreen daily", "Avoid tanning beds completely"],
        "precautions": ["Seek shade between 10am–4pm when UV is strongest", "Wear protective clothing, a wide-brimmed hat, and UV-blocking sunglasses", "Get an annual full-body skin check from a dermatologist if at high risk", "Never ignore a mole that changes shape, colour, size, or bleeds"],
        "medications": ["Surgical excision (primary treatment — performed by surgeon)", "Immunotherapy (pembrolizumab, nivolumab) for advanced disease (oncologist)", "BRAF/MEK inhibitors for BRAF-mutant melanoma (oncologist)", "Radiation therapy for specific cases"],
        "when_to_seek_help": "See a dermatologist URGENTLY for any mole or lesion that changes, bleeds, itches, or looks unusual. Do not delay — early detection is life-saving.",
    },
    "Warts": {
        "description": "Small, rough skin growths caused by human papillomavirus (HPV), commonly appearing on hands, feet (plantar warts), and fingers. Highly contagious through skin contact.",
        "advice": ["Keep warts covered with a bandage to reduce spreading", "Do not pick or scratch warts", "Wash hands thoroughly after touching a wart", "Many warts resolve on their own within 1–2 years"],
        "precautions": ["Wear flip-flops in communal areas to avoid plantar warts", "Do not share towels, nail files, or razors", "Avoid shaving over warts", "Keep feet dry to prevent spread"],
        "medications": ["Salicylic acid (OTC — apply daily after filing with emery board)", "Cryotherapy — liquid nitrogen freezing (GP or dermatologist)", "Cantharidin (blistering agent — clinic only)", "Laser or surgical removal for stubborn warts (dermatologist)"],
        "when_to_seek_help": "See a doctor for warts on face or genitals, painful plantar warts interfering with walking, warts that spread rapidly, or no response to OTC treatment after 3 months.",
    },
    "Impetigo": {
        "description": "A highly contagious bacterial skin infection (Staphylococcus or Streptococcus) common in children, causing honey-coloured crusted sores around the mouth and nose.",
        "advice": ["Keep sores clean with mild antiseptic or saline", "Gently remove crusts with a warm damp cloth (do not pick)", "Cover sores with a loose, non-stick bandage", "Wash clothing and bedding daily at high temperature"],
        "precautions": ["Keep child home from school until sores are healed or 48h after starting antibiotics", "Do not share towels, clothing, or face cloths", "Wash hands thoroughly after touching sores", "Trim fingernails short to prevent spreading"],
        "medications": ["Topical fusidic acid or mupirocin (mild, localised impetigo)", "Oral flucloxacillin or cefalexin for widespread infection (doctor prescribed)"],
        "when_to_seek_help": "See a doctor for rapid spread, fever, blistering impetigo, or sores not healing within 7 days.",
    },
    "Chicken pox": {
        "description": "A highly contagious viral infection (varicella-zoster virus) causing an itchy blister rash all over the body, along with fever and fatigue.",
        "advice": ["Stay home to prevent spreading — contagious until all blisters crust over", "Apply calamine lotion to reduce itching", "Trim fingernails short and consider cotton gloves at night to prevent scratching", "Drink plenty of fluids and rest"],
        "precautions": ["Isolate from pregnant women, newborns, and immunocompromised individuals", "Do not scratch blisters — causes scarring and risk of bacterial infection", "Do NOT give aspirin to children with chickenpox (risk of Reye's syndrome)", "Get the varicella vaccine to prevent the disease"],
        "medications": ["Paracetamol for fever and pain (NOT aspirin in children)", "Antihistamines — chlorphenamine for itching", "Calamine lotion for topical relief", "Antiviral aciclovir (for high-risk patients — doctor prescribed)"],
        "when_to_seek_help": "Seek urgent care for breathing difficulty, blisters near the eye, signs of skin infection (hot, swollen, leaking pus), or confusion.",
    },
    "Drug Reaction": {
        "description": "An adverse skin reaction to a medication, ranging from a mild drug rash to severe conditions like Stevens-Johnson Syndrome. Usually presents within days to weeks of starting a new drug.",
        "advice": ["Stop the suspected medication immediately — consult your doctor first for essential medications", "Do not scratch — apply cool compress or calamine", "Document the drug name, dose, when reaction started, and what it looks like", "Take antihistamines for mild itching"],
        "precautions": ["Always inform all healthcare providers and pharmacists of every drug allergy or reaction", "Wear a medical alert bracelet if you have had a severe reaction", "Never take the offending drug again", "Check cross-reactivity with drugs in the same class"],
        "medications": ["Antihistamines for mild rash and itch", "Topical corticosteroids for localised rash", "Oral corticosteroids for moderate widespread reactions (doctor)", "Epinephrine (EpiPen) for anaphylaxis — emergency use"],
        "when_to_seek_help": "Seek EMERGENCY care immediately for throat/lip swelling, difficulty breathing, blistering or skin peeling (Stevens-Johnson), fever with rash, or face swelling.",
    },
    "Allergy": {
        "description": "A skin allergic reaction (allergic urticaria or angioedema) triggered by food, insect stings, latex, or environmental allergens, causing hives, swelling, or widespread rash.",
        "advice": ["Identify and strictly avoid the allergen", "Take antihistamines at the first sign of a reaction", "Keep an allergy action plan and share it with family/school/work", "Carry your prescribed emergency medications at all times"],
        "precautions": ["Carry an EpiPen if prescribed for severe reactions", "Read food ingredient labels carefully", "Inform restaurant staff of all food allergies", "Avoid cross-contamination risk foods"],
        "medications": ["Non-drowsy antihistamines — cetirizine, fexofenadine (daily for chronic allergy)", "Topical hydrocortisone for localised skin reactions", "Oral corticosteroids for severe reactions (doctor)", "Epinephrine auto-injector (EpiPen) for anaphylaxis"],
        "when_to_seek_help": "Seek EMERGENCY care immediately for throat tightening, difficulty swallowing or breathing, swollen face or lips, or sudden drop in blood pressure.",
    },
    "Fungal Infection": {
        "description": "Skin fungal infections (tinea versicolor, tinea faciei, cutaneous candidiasis) cause discoloured patches, scaling, or red itchy areas, commonly in warm moist skin folds.",
        "advice": ["Keep skin clean and thoroughly dry — especially skin folds", "Wear loose, breathable clothing", "Use antifungal powder in high-friction areas", "Avoid sharing personal items"],
        "precautions": ["Wear moisture-wicking socks and change them daily", "Shower after sweating and dry completely", "Treat all affected areas simultaneously", "For tinea versicolor — recurrence is common; maintenance treatment may be needed"],
        "medications": ["Topical antifungals: clotrimazole, miconazole, terbinafine (OTC)", "Ketoconazole shampoo used as body wash for tinea versicolor", "Oral antifungals: fluconazole or itraconazole for widespread/resistant cases (doctor)"],
        "when_to_seek_help": "See a doctor if the infection is extensive, involves the nails or scalp, or does not clear with 4 weeks of topical treatment.",
    },
}

# Aliases / common spellings → canonical KB key
_ALIASES: dict[str, str] = {
    "acne": "Acne",
    "pimples": "Acne",
    "pimple": "Acne",
    "blackheads": "Acne",
    "whiteheads": "Acne",
    "zits": "Acne",
    "cystic acne": "Acne",
    "psoriasis": "Psoriasis",
    "eczema": "Eczema",
    "atopic dermatitis": "Eczema",
    "atopic eczema": "Eczema",
    "contact dermatitis": "Contact Dermatitis",
    "allergic contact dermatitis": "Contact Dermatitis",
    "irritant contact dermatitis": "Contact Dermatitis",
    "rosacea": "Rosacea",
    "vitiligo": "Vitiligo",
    "white patches": "Vitiligo",
    "seborrheic dermatitis": "Seborrheic Dermatitis",
    "seborrhoeic dermatitis": "Seborrheic Dermatitis",
    "dandruff": "Seborrheic Dermatitis",
    "ringworm": "Ringworm",
    "tinea": "Ringworm",
    "tinea corporis": "Ringworm",
    "athletes foot": "Ringworm",
    "athlete's foot": "Ringworm",
    "tinea pedis": "Ringworm",
    "jock itch": "Ringworm",
    "tinea cruris": "Ringworm",
    "scabies": "Scabies",
    "mite infestation": "Scabies",
    "hives": "Urticaria",
    "urticaria": "Urticaria",
    "wheals": "Urticaria",
    "welts": "Urticaria",
    "shingles": "Herpes Zoster",
    "herpes zoster": "Herpes Zoster",
    "zoster": "Herpes Zoster",
    "skin cancer": "Melanoma",
    "melanoma": "Melanoma",
    "skin tumour": "Melanoma",
    "suspicious mole": "Melanoma",
    "warts": "Warts",
    "wart": "Warts",
    "plantar wart": "Warts",
    "verruca": "Warts",
    "impetigo": "Impetigo",
    "school sores": "Impetigo",
    "chicken pox": "Chicken pox",
    "chickenpox": "Chicken pox",
    "varicella": "Chicken pox",
    "drug rash": "Drug Reaction",
    "drug reaction": "Drug Reaction",
    "medication rash": "Drug Reaction",
    "drug allergy": "Drug Reaction",
    "allergic reaction": "Allergy",
    "skin allergy": "Allergy",
    "allergic rash": "Allergy",
    "fungal infection": "Fungal Infection",
    "tinea versicolor": "Fungal Infection",
    "candidiasis": "Fungal Infection",
    "thrush": "Fungal Infection",
    "yeast infection": "Fungal Infection",
}


def get_disease_info(disease: str) -> DiseaseInfo | None:
    if disease in DISEASE_KB:
        return DISEASE_KB[disease]
    d_lower = disease.lower()
    if d_lower in _ALIASES:
        return DISEASE_KB.get(_ALIASES[d_lower])
    for key, val in DISEASE_KB.items():
        if key.lower() == d_lower:
            return val
    for key, val in DISEASE_KB.items():
        if d_lower in key.lower() or key.lower() in d_lower:
            return val
    return None


def detect_disease_in_text(text: str) -> str | None:
    """Return canonical disease name if user directly named a skin condition."""
    text_lower = text.lower()
    for alias, canonical in _ALIASES.items():
        if alias in text_lower:
            return canonical
    for key in DISEASE_KB:
        if key.lower() in text_lower:
            return key
    return None


def format_medical_section(disease: str, info: DiseaseInfo, confidence: float) -> str:
    conf_pct = round(confidence * 100)
    lines = [
        f"Skin condition: {disease} (confidence: {conf_pct}%)",
        f"What it is: {info['description']}",
        "",
        "Care advice:",
        *[f"  • {a}" for a in info["advice"]],
        "",
        "Precautions:",
        *[f"  • {p}" for p in info["precautions"]],
        "",
        "Common treatments/medications (consult a dermatologist before use):",
        *[f"  • {m}" for m in info["medications"]],
        "",
        f"When to seek help: {info['when_to_seek_help']}",
    ]
    return "\n".join(lines)
