import requests
import re
import json

from rapidfuzz import process, fuzz


# =========================
# NORMALIZE
# =========================

def normalize(text):
    text = str(text).upper()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# FETCH PAYSTACK BANKS
# =========================

def fetch_banks(secret_key):

    headers = {
        "Authorization": f"Bearer {secret_key}"
    }

    url = "https://api.paystack.co/bank?country=ghana"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()["data"]

    except requests.exceptions.SSLError:
        print("[FETCH_BANKS] SSL error connecting to Paystack — running on aliases only.")
        return {}

    except requests.exceptions.ConnectionError:
        print("[FETCH_BANKS] No internet — running on aliases only.")
        return {}

    except requests.exceptions.Timeout:
        print("[FETCH_BANKS] Paystack timed out — running on aliases only.")
        return {}

    except Exception as e:
        print(f"[FETCH_BANKS] Unexpected error: {e} — running on aliases only.")
        return {}

    bank_map = {}

    for bank in data:

        if not bank["active"]:
            continue

        if not bank["supports_transfer"]:
            continue

        name = normalize(bank["name"])
        code = bank["code"]

        # Don't overwrite — first occurrence (GHS) takes priority
        if name not in bank_map:
            bank_map[name] = code

    return bank_map


# =========================
# ALIASES
# Mapped to exact Paystack bank names
# =========================

ALIASES = {

    # -------------------------
    # ABSA / BARCLAYS
    # -------------------------
    "ABSA": "Absa Bank Ghana Ltd",
    "ABSA BANK": "Absa Bank Ghana Ltd",
    "ABSA GHANA": "Absa Bank Ghana Ltd",
    "ABSA BANK GHANA": "Absa Bank Ghana Ltd",
    "BARCLAYS": "Absa Bank Ghana Ltd",
    "BARCLAYS BANK": "Absa Bank Ghana Ltd",
    "BARCLAYS BANK GHANA": "Absa Bank Ghana Ltd",
    "BARCLAYS GHANA": "Absa Bank Ghana Ltd",

    # -------------------------
    # ACCESS BANK
    # -------------------------
    "ACCESS": "Access Bank",
    "ACCESS BANK": "Access Bank",
    "ACCESS GHANA": "Access Bank",
    "ACCESS BANK GHANA": "Access Bank",
    "ACCESS BANK PLC": "Access Bank",
    "ACCESS BANK GH": "Access Bank",

    # -------------------------
    # ADB
    # -------------------------
    "ADB": "ADB Bank Limited",
    "ADB BANK": "ADB Bank Limited",
    "AGRIC DEVELOPMENT BANK": "ADB Bank Limited",
    "AGRICULTURAL DEVELOPMENT BANK": "ADB Bank Limited",
    "AGRICULTURAL DEVELOPMENT": "ADB Bank Limited",
    "AGRIBANK": "ADB Bank Limited",
    "AG BANK": "ADB Bank Limited",
    "AGRIC BANK": "ADB Bank Limited",

    # -------------------------
    # ARB APEX BANK
    # -------------------------
    "ARB": "ARB Apex Bank",
    "ARB APEX": "ARB Apex Bank",
    "ARB APEX BANK": "ARB Apex Bank",
    "APEX BANK": "ARB Apex Bank",
    "APEX": "ARB Apex Bank",

    # -------------------------
    # BANK OF AFRICA
    # -------------------------
    "BOA": "Bank of Africa Ghana",
    "BANK OF AFRICA": "Bank of Africa Ghana",
    "BOA GHANA": "Bank of Africa Ghana",
    "BANK OF AFRICA GHANA": "Bank of Africa Ghana",

    # -------------------------
    # BANK OF GHANA
    # -------------------------
    "BOG": "Bank of Ghana",
    "BANK OF GHANA": "Bank of Ghana",

    # -------------------------
    # CAL BANK
    # -------------------------
    "CAL": "CAL Bank Limited",
    "CALBANK": "CAL Bank Limited",
    "CAL BANK": "CAL Bank Limited",
    "CAL BANK LTD": "CAL Bank Limited",
    "CAL BANK GHANA": "CAL Bank Limited",
    "CALBANK PLC": "CAL Bank Limited",
    "CONTINENTAL ACCEPTANCES": "CAL Bank Limited",

    # -------------------------
    # CONSOLIDATED BANK GHANA
    # -------------------------
    "CBG": "Consolidated Bank Ghana Limited",
    "CONSOLIDATED": "Consolidated Bank Ghana Limited",
    "CONSOLIDATED BANK": "Consolidated Bank Ghana Limited",
    "CONSOLIDATED BANK GHANA": "Consolidated Bank Ghana Limited",
    "C B G": "Consolidated Bank Ghana Limited",

    # -------------------------
    # ECOBANK
    # -------------------------
    "ECOBANK": "Ecobank Ghana Limited",
    "ECO BANK": "Ecobank Ghana Limited",
    "ECOBANK GHANA": "Ecobank Ghana Limited",
    "ECOBANK LTD": "Ecobank Ghana Limited",
    "ECO BANK GHANA": "Ecobank Ghana Limited",

    # -------------------------
    # FBNBANK
    # -------------------------
    "FBN": "FBNBank Ghana Limited",
    "FBN BANK": "FBNBank Ghana Limited",
    "FBNBANK": "FBNBank Ghana Limited",
    "FIRST BANK": "FBNBank Ghana Limited",
    "FIRST BANK NIGERIA": "FBNBank Ghana Limited",
    "FBN GHANA": "FBNBank Ghana Limited",
    "FIRST BANK GHANA": "FBNBank Ghana Limited",

    # -------------------------
    # FIDELITY BANK
    # -------------------------
    "FIDELITY": "Fidelity Bank Ghana Limited",
    "FIDELITY BANK": "Fidelity Bank Ghana Limited",
    "FIDELITY GHANA": "Fidelity Bank Ghana Limited",
    "FIDELITY BANK GHANA": "Fidelity Bank Ghana Limited",
    "FBG": "Fidelity Bank Ghana Limited",

    # -------------------------
    # FIRST ATLANTIC BANK
    # -------------------------
    "FAB": "First Atlantic Bank Limited",
    "FIRST ATLANTIC": "First Atlantic Bank Limited",
    "FIRST ATLANTIC BANK": "First Atlantic Bank Limited",
    "FIRST ATLANTIC GHANA": "First Atlantic Bank Limited",
    "1ST ATLANTIC": "First Atlantic Bank Limited",
    "1ST ATLANTIC BANK": "First Atlantic Bank Limited",

    # -------------------------
    # FIRST NATIONAL BANK
    # -------------------------
    "FNB": "First National Bank Ghana Limited",
    "FIRST NATIONAL": "First National Bank Ghana Limited",
    "FIRST NATIONAL BANK": "First National Bank Ghana Limited",
    "FIRST NATIONAL BANK GHANA": "First National Bank Ghana Limited",
    "FNB GHANA": "First National Bank Ghana Limited",
    "1ST NATIONAL BANK": "First National Bank Ghana Limited",

    # -------------------------
    # GCB BANK
    # -------------------------
    "GCB": "GCB Bank Limited",
    "GCB BANK": "GCB Bank Limited",
    "G C B": "GCB Bank Limited",
    "GCB LTD": "GCB Bank Limited",
    "GCB BANK LTD": "GCB Bank Limited",
    "GHANA COMMERCIAL BANK": "GCB Bank Limited",
    "GHANA COMMERCIAL": "GCB Bank Limited",

    # -------------------------
    # GUARANTY TRUST / GT BANK
    # -------------------------
    "GT": "Guaranty Trust Bank (Ghana) Limited",
    "GTB": "Guaranty Trust Bank (Ghana) Limited",
    "GTBANK": "Guaranty Trust Bank (Ghana) Limited",
    "GT BANK": "Guaranty Trust Bank (Ghana) Limited",
    "G T BANK": "Guaranty Trust Bank (Ghana) Limited",
    "GT BANK GHANA": "Guaranty Trust Bank (Ghana) Limited",
    "GTBANK GHANA": "Guaranty Trust Bank (Ghana) Limited",
    "GUARANTY TRUST": "Guaranty Trust Bank (Ghana) Limited",
    "GUARANTY TRUST BANK": "Guaranty Trust Bank (Ghana) Limited",
    "GUARANTY TRUST GHANA": "Guaranty Trust Bank (Ghana) Limited",

    # -------------------------
    # MTN MOBILE MONEY
    # -------------------------
    "MTN": "MTN",
    "MTN MOMO": "MTN",
    "MTN MOBILE MONEY": "MTN",
    "MOMO": "MTN",

    # -------------------------
    # NATIONAL INVESTMENT BANK
    # -------------------------
    "NIB": "National Investment Bank Limited",
    "N I B": "National Investment Bank Limited",
    "NATIONAL INVESTMENT": "National Investment Bank Limited",
    "NATIONAL INVESTMENT BANK": "National Investment Bank Limited",
    "NATINVEST": "National Investment Bank Limited",

    # -------------------------
    # OMNIBSIC BANK
    # -------------------------
    "OMNI": "OmniBSCI Bank",
    "OMNIBANK": "OmniBSCI Bank",
    "OMNI BANK": "OmniBSCI Bank",
    "OMNIBSIC": "OmniBSCI Bank",
    "OMNI BSIC": "OmniBSCI Bank",
    "BSIC": "OmniBSCI Bank",
    "BSIC GHANA": "OmniBSCI Bank",
    "SAHEL SAHARA": "OmniBSCI Bank",
    "SAHEL SAHARA BANK": "OmniBSCI Bank",

    # -------------------------
    # PRUDENTIAL BANK
    # -------------------------
    "PRUDENTIAL": "Prudential Bank Limited",
    "PRUDENTIAL BANK": "Prudential Bank Limited",
    "PRUDENTIAL GHANA": "Prudential Bank Limited",
    "PRUDENTIAL BANK GHANA": "Prudential Bank Limited",

    # -------------------------
    # REPUBLIC BANK / HFC
    # -------------------------
    "REPUBLIC": "Republic Bank (GH) Limited",
    "REPUBLIC BANK": "Republic Bank (GH) Limited",
    "REPUBLIC GH": "Republic Bank (GH) Limited",
    "REPUBLIC GHANA": "Republic Bank (GH) Limited",
    "REPUBLIC BANK GHANA": "Republic Bank (GH) Limited",
    "HFC": "Republic Bank (GH) Limited",
    "HFC BANK": "Republic Bank (GH) Limited",
    "HFC BANK GHANA": "Republic Bank (GH) Limited",

    # -------------------------
    # SOCIETE GENERALE
    # -------------------------
    "SG": "Société Générale Ghana Limited",
    "SG BANK": "Société Générale Ghana Limited",
    "SG Bank": "Société Générale Ghana Limited",
    "Sg Bank": "Société Générale Ghana Limited",
    "SOC GEN": "Société Générale Ghana Limited",
    "SOCGEN": "Société Générale Ghana Limited",
    "SG GHANA": "Société Générale Ghana Limited",
    "SOCIETE GENERALE": "Société Générale Ghana Limited",
    "SOCIETE GENERAL": "Société Générale Ghana Limited",
    "SOCIETE GEN": "Société Générale Ghana Limited",
    "SOC GENERALE": "Société Générale Ghana Limited",
    "STD GEN": "Société Générale Ghana Limited",

    # -------------------------
    # STANBIC BANK
    # -------------------------
    "STANBIC": "Stanbic Bank Ghana Limited",
    "STANBIC BANK": "Stanbic Bank Ghana Limited",
    "STANBIC GHANA": "Stanbic Bank Ghana Limited",
    "STANBIC BANK GHANA": "Stanbic Bank Ghana Limited",
    "STANDARD BANK": "Stanbic Bank Ghana Limited",
    "STANDARD BANK GHANA": "Stanbic Bank Ghana Limited",

    # -------------------------
    # STANDARD CHARTERED
    # -------------------------
    "SCB": "Standard Chartered Bank Ghana Limited",
    "STANCHART": "Standard Chartered Bank Ghana Limited",
    "STAN CHART": "Standard Chartered Bank Ghana Limited",
    "STD CHARTERED": "Standard Chartered Bank Ghana Limited",
    "STANDARD CHARTERED": "Standard Chartered Bank Ghana Limited",
    "STANDARD CHARTERED BANK": "Standard Chartered Bank Ghana Limited",
    "STANDARD CHARTERED GHANA": "Standard Chartered Bank Ghana Limited",

    # -------------------------
    # UBA
    # -------------------------
    "UBA": "United Bank for Africa Ghana Limited",
    "UBA BANK": "United Bank for Africa Ghana Limited",
    "UBA GHANA": "United Bank for Africa Ghana Limited",
    "U B A": "United Bank for Africa Ghana Limited",
    "UNITED BANK AFRICA": "United Bank for Africa Ghana Limited",
    "UNITED BANK FOR AFRICA": "United Bank for Africa Ghana Limited",
    "UNITED BANK FOR AFRICA GHANA": "United Bank for Africa Ghana Limited",

    # -------------------------
    # UMB
    # -------------------------
    "UMB": "Universal Merchant Bank Ghana Limited",
    "U M B": "Universal Merchant Bank Ghana Limited",
    "UNIVERSAL MERCHANT": "Universal Merchant Bank Ghana Limited",
    "UNIVERSAL MERCHANT BANK": "Universal Merchant Bank Ghana Limited",
    "MERCHANT BANK": "Universal Merchant Bank Ghana Limited",
    "MERCHANT BANK GHANA": "Universal Merchant Bank Ghana Limited",
    "UMB GHANA": "Universal Merchant Bank Ghana Limited",

    # -------------------------
    # VODAFONE / TELECEL
    # -------------------------
    "VODAFONE": "Vodafone",
    "VODAFONE CASH": "Vodafone",
    "TELECEL": "Vodafone",
    "TELECEL CASH": "Vodafone",
    "VOD CASH": "Vodafone",

    # -------------------------
    # AIRTELTIGO
    # -------------------------
    "AIRTEL": "AirtelTigo",
    "TIGO": "AirtelTigo",
    "AIRTELTIGO": "AirtelTigo",
    "AIRTEL TIGO": "AirtelTigo",
    "AIRTEL MONEY": "AirtelTigo",
    "TIGO CASH": "AirtelTigo",
    "ATL": "AirtelTigo",

    # -------------------------
    # ZENITH BANK
    # -------------------------
    "ZENITH": "Zenith Bank Ghana",
    "ZBG": "Zenith Bank Ghana",
    "ZENITH BANK": "Zenith Bank Ghana",
    "ZENITH GHANA": "Zenith Bank Ghana",
    "ZENITH BANK GHANA": "Zenith Bank Ghana",

    # -------------------------
    # BEST POINT SAVINGS & LOANS
    # -------------------------
    "BEST POINT": "Best Point Savings & Loans",
    "BEST POINT SAVINGS": "Best Point Savings & Loans",
    "BESTPOINT": "Best Point Savings & Loans",

    # -------------------------
    # SINAPI ABA
    # -------------------------
    "SINAPI": "Sinapi ABA Savings And Loans",
    "SINAPI ABA": "Sinapi ABA Savings And Loans",
    "SINAPI ABA SAVINGS": "Sinapi ABA Savings And Loans",

    # -------------------------
    # SERVICES INTEGRITY SAVINGS
    # -------------------------
    "SERVICES INTEGRITY": "Services Integrity Savings and Loans",
    "SISL": "Services Integrity Savings and Loans",

    # -------------------------
    # ADEHYEMAN SAVINGS
    # -------------------------
    "ADEHYEMAN": "Adehyeman Savings and Loans LTD",
    "ADEHYEMAN SAVINGS": "Adehyeman Savings and Loans LTD",

    # -------------------------
    # AFFINITY GHANA
    # -------------------------
    "AFFINITY": "Affinity Ghana Savings and Loans",
    "AFFINITY BANK": "Affinity Ghana Savings and Loans",
    "AFFINITY GHANA": "Affinity Ghana Savings and Loans",
    "AFFINITY SAVINGS": "Affinity Ghana Savings and Loans",

}


# =========================
# BUILD SEARCH MAP
# =========================

def build_search_map(secret_key):

    official_banks = fetch_banks(secret_key)

    search_map = {}

    for name, code in official_banks.items():
        search_map[name] = code

    for alias, official_name in ALIASES.items():

        official_name = normalize(official_name)
        code = official_banks.get(official_name)

        if code:
            search_map[normalize(alias)] = code

    return search_map


# =========================
# GROQ FALLBACK
# Calls Groq to infer the canonical Ghanaian bank name
# from a free-form user input, then re-attempts lookup.
# =========================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


def _ask_groq(user_input: str, known_banks: list[str], groq_api_key: str) -> str | None:
    """
    Ask Groq to map `user_input` to the closest name in `known_banks`.
    Returns the matched bank name string, or None if Groq can't identify it.
    """

    bank_list_str = "\n".join(f"- {b}" for b in known_banks)

    prompt = (
        "You are a bank-name normalizer for Ghana. "
        "A user has provided a bank name that could not be matched automatically.\n\n"
        f"User input: \"{user_input}\"\n\n"
        "Below is the full list of known Ghanaian banks (as they appear in the system):\n"
        f"{bank_list_str}\n\n"
        "Instructions:\n"
        "1. Identify which bank on the list best matches the user input.\n"
        "2. Consider abbreviations, alternate spellings, old names, and local nicknames.\n"
        "3. Reply with ONLY a JSON object in this exact format, nothing else:\n"
        '   {"match": "<exact bank name from the list>"}\n'
        '4. If you cannot identify a match with confidence, reply:\n'
        '   {"match": null}'
    )

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,       # deterministic
        "max_tokens": 64,       # we only need a short JSON reply
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=15,
        )
        response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown code fences if the model wraps the JSON
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)
        return parsed.get("match")  # str or None

    except Exception as exc:
        print(f"[GROQ ERROR] {exc}")
        return None


def groq_lookup(user_input: str, search_map: dict, groq_api_key: str) -> str | None:
    """
    Use Groq to infer the bank, then resolve it through the existing search_map.
    Returns the Paystack bank code, or None if inference fails.
    """

    # Pass only the ~40 unique canonical bank names from ALIASES values —
    # NOT all search_map keys (hundreds of redundant uppercase alias variants
    # that bloat the prompt and exceed token limits).
    canonical_names = sorted({normalize(name) for name in ALIASES.values()})

    groq_suggestion = _ask_groq(user_input, canonical_names, groq_api_key)

    if not groq_suggestion:
        print(f"[GROQ NO MATCH] {user_input}")
        return None

    # Normalise the suggestion and try an exact hit first
    suggestion_norm = normalize(groq_suggestion)

    if suggestion_norm in search_map:
        print(f"[GROQ MATCH] {user_input} -> {groq_suggestion}")
        return search_map[suggestion_norm]

    # Groq returned something slightly off — run a final fuzzy pass at a
    # lower threshold since we already have high confidence from the LLM.
    result = process.extractOne(
        suggestion_norm,
        search_map.keys(),
        scorer=fuzz.token_sort_ratio,
    )

    if result:
        matched_name, score, _ = result
        if score >= 70:   # relaxed threshold: Groq already did the hard work
            print(
                f"[GROQ+FUZZY MATCH] "
                f"{user_input} -> {groq_suggestion} -> "
                f"{matched_name} ({score:.1f}%)"
            )
            return search_map[matched_name]

    print(f"[GROQ UNRESOLVED] {user_input} (Groq suggested: {groq_suggestion})")
    return None


# =========================
# LOOKUP
# =========================

def get_bank_code(
    user_input: str,
    search_map: dict,
    min_score: int = 85,
    groq_api_key: str | None = None,
) -> str | None:
    """
    Resolve a free-form bank name to a Paystack bank code.

    Resolution order:
      1. Exact match (normalised)
      2. Fuzzy match (rapidfuzz, threshold = min_score)
      3. Groq LLM inference (only when groq_api_key is provided)
    """

    user_input_norm = normalize(user_input)

    # --------------------------------------------------
    # 1. Exact match
    # --------------------------------------------------
    if user_input_norm in search_map:
        return search_map[user_input_norm]

    # --------------------------------------------------
    # 2. Fuzzy fallback — high threshold to avoid bad guesses
    # --------------------------------------------------
    result = process.extractOne(
        user_input_norm,
        search_map.keys(),
        scorer=fuzz.token_sort_ratio,
    )

    if result:
        matched_name, score, _ = result
        if score >= min_score:
            print(
                f"[BANK GUESS] "
                f"{user_input_norm} -> "
                f"{matched_name} "
                f"({score:.1f}%)"
            )
            return search_map[matched_name]

    # --------------------------------------------------
    # 3. Groq LLM fallback
    # --------------------------------------------------
    if groq_api_key:
        print(f"[GROQ FALLBACK] Trying Groq for: {user_input}")
        code = groq_lookup(user_input, search_map, groq_api_key)
        if code:
            return code

    print(f"[UNKNOWN BANK] {user_input_norm}")
    return None