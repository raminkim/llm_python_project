def chunk_text(text, chunk_size=100, overlap=20):
    if not text or len(text.strip()) == 0:
        print("경고: 빈 텍스트를 청크로 나누려고 합니다.")
        return []
        
    # 한글 텍스트를 문자 단위로 분할
    chars = list(text)
    if not chars:
        print("경고: 문자를 찾을 수 없습니다.")
        return []
    
    chunks = []
    # 문자 단위로 청크 생성
    for i in range(0, len(chars), chunk_size):  # chunk_size - overlap 대신 chunk_size 사용
        chunk = ''.join(chars[i:i+chunk_size])
        if chunk:  # 빈 청크만 제외
            chunks.append(chunk)
            
    if not chunks:
        print(f"경고: 유효한 청크가 생성되지 않았습니다. 텍스트: {text[:100]}...")
        # 텍스트가 있는 경우 전체를 하나의 청크로 처리
        if text:
            chunks.append(text)
            
    return chunks