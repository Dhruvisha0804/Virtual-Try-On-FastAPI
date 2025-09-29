def extract_response_info(response, input_prompt):
    """
    Extract minimal metadata from Gemini API response.
    """
    result = {
        "responseId": getattr(response, "response_id", None),
        "inputPrompt": input_prompt,
        "outputTexts": [],
        "usage": {}
    }

    # Output texts
    if getattr(response, "candidates", None):
        for candidate in response.candidates:
            if getattr(candidate, "content", None) and getattr(candidate.content, "parts", None):
                for part in candidate.content.parts or []:
                    if getattr(part, "text", None):
                        result["outputTexts"].append(part.text)

    # Usage metadata
    usage = getattr(response, "usage_metadata", None)
    if usage:
        result["usage"]["promptTokensTotal"] = getattr(usage, "prompt_token_count", 0)
        result["usage"]["candidatesTokens"] = getattr(usage, "candidates_token_count", 0)
        result["usage"]["textTokens"] = 0
        result["usage"]["imageTokens"] = 0

        if getattr(usage, "prompt_tokens_details", None):
            for detail in usage.prompt_tokens_details or []:
                if getattr(detail, "modality", "").upper() == "TEXT":
                    result["usage"]["textTokens"] = getattr(detail, "token_count", 0)
                elif getattr(detail, "modality", "").upper() == "IMAGE":
                    result["usage"]["imageTokens"] = getattr(detail, "token_count", 0)

    return result