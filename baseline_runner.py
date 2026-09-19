import json
from pathlib import Path
from src.chunking import ChunkingStrategyComparator

def parse_frontmatter(content):
    if not content.startswith('---\n'):
        return {}, content
    
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return {}, content
        
    frontmatter = parts[1]
    body = parts[2].strip()
    
    metadata = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            metadata[key.strip()] = val.strip().strip('"\'')
            
    return metadata, body

comp = ChunkingStrategyComparator()
docs = ['data/hoc-bong/scholarship-luatmk2026.md', 'data/hoc-bong/scholarship-ou2026.md']

print("| Tài liệu | Phương pháp | Số lượng | Kích thước trung bình |")
print("|----------|-------------|----------|-----------------------|")
for p in docs:
    with open(p, 'r', encoding='utf-8') as f:
        meta, content = parse_frontmatter(f.read())
        
    res = comp.compare(content, chunk_size=500)
    name = Path(p).stem
    print(f"| {name} | Fixed Size (500) | {res['fixed_size']['count']} | {res['fixed_size']['avg_length']:.1f} |")
    print(f"| {name} | Sentence (3) | {res['by_sentences']['count']} | {res['by_sentences']['avg_length']:.1f} |")
    print(f"| {name} | Recursive (500) | {res['recursive']['count']} | {res['recursive']['avg_length']:.1f} |")
