import sys
from pathlib import Path


from src.chunking import HeadingChunker
from src.store import EmbeddingStore
from src.models import Document
from src.agent import KnowledgeBaseAgent

def parse_markdown(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    metadata = {}
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content = parts[2].strip()
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    metadata[key.strip()] = val.strip().strip('"\'')
            
    return metadata, content.strip()

def main():
    store = EmbeddingStore()
    
    # Chiến lược riêng của R3: HeadingChunker
    chunker = HeadingChunker(chunk_size=500)
    
    data_dir = Path("data/hoc-bong")
    docs = []
    
    # 1. Đọc từng file .md, tách frontmatter thành metadata và phần thân thành content
    for path in data_dir.glob("*.md"):
        metadata, content = parse_markdown(path)
        
        # 2. Chunk phần thân, mỗi chunk thành một Document
        chunks = chunker.chunk(content)
        for i, chunk in enumerate(chunks):
            # Metadata frontmatter phải được trải vào mọi chunk, doc_id trỏ về tên file gốc
            chunk_metadata = {**metadata, "doc_id": path.stem}
            doc = Document(id=f"{path.stem}#{i}", content=chunk, metadata=chunk_metadata)
            docs.append(doc)
            
    # 3. Nạp vào EmbeddingStore
    store.add_documents(docs)
    print(f"Đã nạp {store.get_collection_size()} chunks vào EmbeddingStore từ thư mục data/hoc-bong.\n")
    
    # 5 benchmark query
    queries = [
        {
            "query": "Học bổng thủ khoa đầu vào dành cho đối tượng nào?", 
            "filter": {"audience": "student"},
            "gold": "Sinh viên mới trúng tuyển với số điểm cao nhất."
        },
        {
            "query": "Học bổng thủ khoa đầu vào dành cho đối tượng nào? (NO FILTER A/B TEST)", 
            "filter": None,
            "gold": "Sinh viên mới trúng tuyển với số điểm cao nhất."
        },
        {
            "query": "Học bổng khuyến khích học tập yêu cầu điểm trung bình bao nhiêu?",
            "filter": None,
            "gold": "Từ 3.6 trở lên."
        },
        {
            "query": "Quyền lợi của học bổng doanh nghiệp AEON là gì?",
            "filter": None,
            "gold": "Tài trợ 100% học phí và có cơ hội thực tập."
        },
        {
            "query": "Thời gian hết hạn nộp hồ sơ xin học bổng?",
            "filter": None,
            "gold": "Ngày 30/10 hàng năm."
        },
        {
            "query": "Thủ tục xin học bổng bao gồm những giấy tờ gì?",
            "filter": None,
            "gold": "Bảng điểm, đơn xin học bổng, giấy tờ chứng minh hoàn cảnh (nếu có)."
        }
    ]
    
    # 4. In top-3 kèm score và doc_id để đối chiếu với gold answer
    for i, q in enumerate(queries, 1):
        print(f"--- Query {i}: {q['query']} ---")
        print(f"Filter: {q['filter']}")
        print(f"Gold answer: {q['gold']}")
        
        results = store.search_with_filter(q['query'], top_k=3, metadata_filter=q['filter'])
        
        if not results:
            print("Không tìm thấy kết quả phù hợp.")
        else:
            for j, res in enumerate(results, 1):
                score = res.get("score", 0.0)
                doc_id = res.get("metadata", {}).get("doc_id", "Unknown")
                preview = res.get("content", "")[:100].replace('\n', ' ')
                print(f"  Top {j} [score={score:.3f} | doc_id={doc_id}]: {preview}...")
        print()

if __name__ == "__main__":
    main()
