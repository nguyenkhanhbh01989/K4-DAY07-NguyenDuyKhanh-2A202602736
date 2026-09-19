# Ghi Chú Bài Học - Lab 7: Embedding & Vector Store

Tài liệu này tổng hợp lại các kiến thức cốt lõi và công việc đã thực hiện qua các Checkpoint trong dự án.

## Checkpoint 3 (1:00 - 1:45): Chunking & Similarity

### Công việc đã làm:
- Hoàn thiện file `src/chunking.py` bao gồm các class: `SentenceChunker`, `RecursiveChunker`, hàm `compute_similarity`, và `ChunkingStrategyComparator`.
- Giải quyết thành công các edge cases của regex và logic đệ quy, giúp toàn bộ 23/23 tests liên quan passing.
- Trả lời các câu hỏi lý thuyết tại mục 1 phần Warm-up trong báo cáo.

### Bài học cốt lõi:
1. **Cosine Similarity vs Euclidean Distance**: Cosine similarity phù hợp hơn cho Text Embeddings vì nó chỉ quan tâm đến **góc/hướng** giữa hai vector (phản ánh ngữ nghĩa) thay vì độ dài vector (thường bị ảnh hưởng bởi độ dài văn bản hay tần suất từ ngữ). Hai câu khác biệt hoàn toàn về từ vựng (VD: "mèo là thú cưng" và "miu là vật nuôi") vẫn có Cosine Similarity cao nhờ cùng ngữ nghĩa.
2. **Chunking Overlap**: Công thức tính số lượng chunk là `ceil((độ_dài − overlap) / (chunk_size − overlap))`. Độ chồng chéo (overlap) làm tăng số lượng chunk và chi phí lưu trữ/nhúng, nhưng cực kỳ quan trọng để **duy trì ngữ cảnh liên tục**, giúp RAG không bị mất thông tin khi truy xuất một mảnh văn bản bị cắt giữa chừng.
3. **Regex trong việc cắt câu**: Thay vì split bằng `[.!?]\s+` làm nuốt mất dấu câu, việc sử dụng **Positive Lookbehind** `(?<=\. )|(?<=\! )` giúp chia cắt thành từng câu nhưng vẫn giữ nguyên dấu câu đính kèm. 
4. **Recursive Chunking**: Thuật toán chia nhỏ đệ quy ưu tiên cắt bằng ranh giới "lớn" trước (như `\n\n`) để bảo toàn ngữ nghĩa, chỉ khi văn bản vượt `chunk_size` mới dùng separator nhỏ hơn. Điểm mấu chốt là **phải có bước gom lên (agglomerate)** các mảnh nhỏ sát lại nhau thành chunk lớn để tránh sinh ra hàng trăm mảnh vụn mất ngữ cảnh.

---

## Checkpoint 4 (1:45 - 2:30): Vector Store & RAG Agent

### Công việc đã làm:
- Hoàn thiện file `src/store.py` (`EmbeddingStore`) với các hàm `_make_record`, `_search_records`, `add_documents`, `search`, `search_with_filter`, và `delete_document`.
- Hoàn thiện file `src/agent.py` (`KnowledgeBaseAgent`) để xử lý luồng RAG.
- Chạy pass toàn bộ 42/42 tests của dự án. Chạy thành công luồng test thực tế qua lệnh `python main.py "Chunking là gì?"`.

### Bài học cốt lõi:
1. **Quản lý Record & Metadata**: Khi chuyển `Document` thành record lưu trữ, cần **copy metadata** thay vì tham chiếu trực tiếp để tránh lỗi side-effect. Đồng thời luôn phải đảm bảo tồn tại một trường `doc_id` trỏ về **file gốc** (chứ không phải id của chunk), giúp các tác vụ như `delete_document` hoạt động được chính xác.
2. **Pre-filtering vs Post-filtering**: Trong Vector Store, việc lọc siêu dữ liệu (metadata) **bắt buộc phải thực hiện trước** (pre-filter) khi search similarity. Nếu tìm top-K xong mới lọc bỏ kết quả sai, bạn có thể nhận về 0 kết quả (do k vị trí đầu đã bị chiếm bởi các chunk khác chủ đề).
3. **Clean Output**: Vector nhúng (1536 chiều) rất dài và nặng. Khi trả về kết quả tìm kiếm từ DB, luôn cần loại bỏ trường `embedding` khỏi object kết quả để làm sạch terminal và tiết kiệm bộ nhớ.
4. **Kiểm soát ảo giác (Anti-hallucination) & Truy vết (Traceability) trong RAG**:
   - Agent cần kiểm tra store rỗng và chặn ngay từ đầu để **tránh gọi LLM vô ích** gây tốn kém token.
   - Khi inject context, mỗi chunk cần được **đánh số rõ ràng và đi kèm nguồn** (ví dụ: `[1] Source: file.md`). 
   - Prompt đưa cho LLM cần có câu lệnh nghiêm ngặt yêu cầu **không được bịa đặt**, phải trả lời "không biết" nếu không tìm thấy, và **phải trích dẫn [số nguồn]** khi lấy thông tin. Điều này giúp hệ thống minh bạch và dễ dàng xác thực lại dữ liệu.
