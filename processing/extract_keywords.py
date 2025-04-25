from yake import KeywordExtractor

def extract_keywords(text, max_keywords=5):
    extractor = KeywordExtractor()
    keywords = extractor.extract_keywords(text)
    return [kw[0] for kw in keywords[:max_keywords]]