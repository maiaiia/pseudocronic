from backend.ai_powered_functionalities.correction_pseudocode.prompts import PSEUDOCODE_RULES


def get_ocr_cleanup_prompt(raw_ocr_text: str) -> list:
    system_message = f"""Ești un expert în procesarea textului OCR pentru pseudocod românesc.

{PSEUDOCODE_RULES}

Sarcina ta:
1. Curăță textul OCR de erori comune (caractere greșite, spații în plus)
2. Formatează codul conform regulilor pseudocodului românesc
3. Corectează simbolurile speciale (←, ≠, ≤, ≥)
4. Păstrează structura și indentarea
5. NU modifica logica algoritmului, doar curăță textul

Returnează DOAR codul pseudocod curat, fără explicații suplimentare.
"""

    user_message = f"Curăță acest text OCR:\n\n{raw_ocr_text}"

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]