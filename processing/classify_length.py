def classify_length(text):
    word_count = len(text.split())

    if word_count < 10:
        return "short"
    elif word_count < 50:
        return "medium"
    else:
        return "long"