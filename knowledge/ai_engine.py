import json
from django.conf import settings
from openai import OpenAI


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_ai_structured_output(topic, context_bundle):
    if getattr(settings, "AI_MODE", "mock") == "mock":
        return _mock_ai_response(topic, context_bundle)
    if not settings.OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY ist nicht gesetzt.")

    model = getattr(settings, "OPENAI_MODEL", "gpt-5.4")

    system_prompt = (
        "Du bist ein erfahrener deutscher Datenschutzjurist. "
        "Antworte präzise, strukturiert, vorsichtig und fachlich korrekt nach DSGVO. "
        "Erfinde keine Tatsachen."
    )

    user_prompt = json.dumps(context_bundle, ensure_ascii=False, indent=2)

    if topic == "legitimate_interest":
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": system_prompt,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Führe auf Basis der folgenden Daten eine Interessenabwägung "
                                "nach Art. 6 Abs. 1 lit. f DSGVO durch. "
                                "Gib ausschließlich JSON im vorgegebenen Schema zurück.\n\n"
                                f"{user_prompt}"
                            ),
                        }
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "legitimate_interest_assessment",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "purpose": {"type": "string"},
                            "impact": {"type": "string"},
                            "safeguards": {"type": "string"},
                            "reasoning": {"type": "string"},
                            "outcome": {
                                "type": "string",
                                "enum": ["controller", "balanced", "data_subject"],
                            },
                        },
                        "required": [
                            "purpose",
                            "impact",
                            "safeguards",
                            "reasoning",
                            "outcome",
                        ],
                    },
                    "strict": True,
                }
            },
        )

        if not response.output_text:
            raise Exception("Leere Antwort von der OpenAI Responses API.")

        return json.loads(response.output_text)

    if topic == "legal_assessment":
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": system_prompt,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Erstelle eine vorsichtige juristische Bewertung nach DSGVO "
                                "auf Basis der folgenden Daten.\n\n"
                                f"{user_prompt}"
                            ),
                        }
                    ],
                },
            ],
        )

        if not response.output_text:
            raise Exception("Leere Antwort von der OpenAI Responses API.")

        return {"text": response.output_text}

def _mock_ai_response(topic, context_bundle):
    processing = getattr(context_bundle, "processing_activity", None)
    title = getattr(processing, "title", "") if processing else ""
    purpose = getattr(processing, "purpose", "") if processing else ""
    categories = getattr(processing, "personal_data_categories", "") if processing else ""
    subjects = getattr(processing, "data_subject_categories", "") if processing else ""

    if topic == "legitimate_interest":
        return {
            "purpose": (
                "TESTMODUS: Der Verantwortliche verfolgt ein berechtigtes organisatorisches "
                f"Interesse an der Verarbeitung \"{title}\". "
                f"Zweck der Verarbeitung: {purpose or 'nicht näher beschrieben'}."
            ),
            "impact": (
                "TESTMODUS: Für die betroffenen Personen bestehen Eingriffe in die informationelle "
                "Selbstbestimmung. Diese betreffen insbesondere die Kategorien "
                f"\"{subjects or 'nicht näher bezeichnete betroffene Personen'}\" "
                f"und die Datenkategorien \"{categories or 'nicht näher bezeichnet'}\"."
            ),
            "safeguards": (
                "TESTMODUS: Zugunsten der Zulässigkeit sprechen insbesondere "
                "Zugriffsbeschränkungen, Rollen- und Berechtigungskonzepte, "
                "Datenminimierung und organisatorische Schutzmaßnahmen."
            ),
            "reasoning": (
                "TESTMODUS: Bei vorläufiger Betrachtung überwiegen die Interessen des "
                "Verantwortlichen, sofern die Verarbeitung auf das erforderliche Maß begrenzt "
                "bleibt und die benannten Schutzmaßnahmen tatsächlich umgesetzt werden."
            ),
            "outcome": "controller",
        }

    if topic == "legal_assessment":
        return {
            "text": (
                "TESTMODUS: Für den Verarbeitungsvorgang "
                f"\"{title or 'unbenannt'}\" erscheint eine datenschutzrechtliche Zulässigkeit "
                "vorläufig möglich, sofern die dokumentierten Zwecke, Rechtsgrundlagen und "
                "Schutzmaßnahmen konsistent umgesetzt werden."
            )
        }

    return {}