def chunk_text(text, chunk_size=600, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if len(chunk) > 10:  # 10자 미만 청크 제외
            chunks.append(chunk)
    return chunks if chunks else ["[No valid chunks]"]  # 빈 청크 방지