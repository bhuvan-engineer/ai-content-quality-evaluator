LANGUAGE_LABELS = {
    "English": "English",
    "Hindi": "Hindi (हिंदी)",
    "Hinglish": "Hinglish (Hindi + English code-mixing)"
}

CONTENT_TYPES = ["Email", "Blog introduction", "Social media post"]

PROMPT_STYLES = ["Zero-shot", "Few-shot", "Role-based", "Constraint-based"]

def build_prompts(content_type, language, prompt_style, tone, length, audience, topic, extra_instructions=""):
    role = "You are a careful, helpful content writer."
    if prompt_style == "Role-based":
        role = f"You are an experienced {content_type.lower()} writer who understands audience, tone, and clarity."
    system = (
        f"{role} Create content in {language}. Use natural, idiomatic language appropriate for the requested language. "
        "Do not invent specific facts, dates, statistics, citations, or quotations. If information is missing, keep the wording general. "
        "Follow the user's constraints and avoid unnecessary filler."
    )
    length_guidance = {
        "Short": "Keep it concise, usually around 50–100 words.",
        "Medium": "Aim for roughly 120–200 words.",
        "Long": "Provide a detailed version, usually around 250–400 words."
    }[length]
    formats = {
        "Email": "Write an email with a suitable subject, greeting, clear body, and appropriate closing.",
        "Blog introduction": "Write an engaging blog introduction that establishes the topic and explains why it matters.",
        "Social media post": "Write a clear, engaging social media post. Use hashtags only if appropriate."
    }
    audience_line = f"Target audience: {audience.strip()}." if audience and audience.strip() else "Use a broadly appropriate audience."
    instructions = [
        f"Content type: {content_type}.",
        formats[content_type],
        f"Language: {language}.",
        f"Tone: {tone}.",
        length_guidance,
        audience_line,
        f"Topic/brief: {topic.strip()}."
    ]
    if prompt_style == "Few-shot":
        instructions.append(
            "Style example (follow the general pattern, not the exact words): "
            "'Hello everyone, we are pleased to share an update. Please review the details and contact us if you have questions.' "
            "Adapt naturally to the requested language and content type."
        )
    if prompt_style == "Constraint-based":
        instructions.append("Constraints: avoid clichés, repeated points, unsupported factual claims, and exaggerated promises. Use clear wording.")
    if extra_instructions and extra_instructions.strip():
        instructions.append("Additional instructions: " + extra_instructions.strip())
    instructions.append("Return only the finished content, without explaining your process.")
    return system, "\n".join(instructions)
