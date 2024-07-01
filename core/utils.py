def translated_description(s):
    if s:
        phrases = [phrase.strip() for phrase in s.split("---")]
        default_phrase = [phrase for phrase in phrases if phrase.startswith("DEFAULT:")]
        if len(default_phrase):
            return default_phrase[0].replace("DEFAULT:", "").strip()
    return s
