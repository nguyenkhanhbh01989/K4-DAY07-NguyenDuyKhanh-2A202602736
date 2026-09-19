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

---

## Checkpoint 5 & 6 (2:30 - 3:25): Chunker Tùy Chỉnh, A/B Testing & Phân Tích Lỗi

### Công việc đã làm:
- Xây dựng thành công `HeadingChunker` tự động chia văn bản theo tiêu đề Markdown và kế thừa đệ quy.
- Viết kịch bản `bench.py` để nạp 159 chunks từ thư mục dữ liệu thật (`data/hoc-bong`), bóc tách Frontmatter YAML thành metadata, trải metadata ra từng chunk con.
- Đánh giá đường cơ sở (Baseline) cho 3 thuật toán và ghi nhận kết quả.
- Thực hiện **A/B Testing** (truy vấn có/không có metadata filter) và lập tài liệu phân tích lỗi cho MockEmbedder.

### Bài học cốt lõi:
1. **Chiến thuật Heading Chunker**: Việc cắt văn bản ngây thơ theo kích thước tĩnh (FixedSize) có thể cắt ngang một câu và phá nát ngữ nghĩa. Dựa vào cấu trúc tự nhiên của văn bản (các thẻ Heading `#`, `##`), việc tách theo đề mục giúp **bảo toàn trọn vẹn ngữ nghĩa**. Điểm mấu chốt: khi một phần (section) quá dài phải chia nhỏ, **luôn phải gắn lại heading vào đầu đoạn nhỏ đó**, nếu không các đoạn nhỏ sau sẽ mất hoàn toàn ngữ cảnh (không biết đang nói về chủ đề gì).
2. **Quyền năng của Metadata Filtering (Pre-filtering)**: Qua A/B test thực tế, một truy vấn (query) có thể trùng khớp từ vựng với 2 tài liệu nhưng dành cho 2 đối tượng khác nhau (VD: Sinh viên vs Giảng viên). Bằng cách truyền thêm `{"audience": "student"}`, Vector Store loại bỏ ngay các văn bản nhiễu trước khi tính Cosine Similarity. Đây là giải pháp cực kỳ hiệu quả để giải quyết lỗi **trả về sai ngữ cảnh đối tượng**.
3. **Chấm điểm 2 Mức Độ (2-level Scoring)**: Đánh giá RAG không thể chỉ dựa vào việc "doc_id lấy ra có đúng file hay không". Một file dài 10.000 chữ, lấy ra đúng file nhưng lấy nhầm phần giới thiệu thì LLM vẫn không thể trả lời được. Vì vậy, hệ thống chấm điểm phải kiểm tra mức độ nội dung: Chunk lấy ra phải **chứa đúng đoạn string mang thông tin của câu trả lời** (Gold Answer).
4. **Sự thật về MockEmbedder (Failure Case Analysis)**: Khi sử dụng `MockEmbedder` (băm MD5), kết quả vector bị nhiễu và hoàn toàn không đại diện cho độ tương đồng ngữ nghĩa. Mặc dù hệ thống logic (chunking, search, filter) viết đúng 100%, kết quả trả về của RAG vẫn sẽ thất bại vì Cosine Similarity lúc này giống hệt chọn ngẫu nhiên. Điều này chứng minh: **Chất lượng của hệ thống RAG phụ thuộc tuyệt đối vào sức mạnh của thuật toán Embedding thực tế (ví dụ: OpenAI, MiniLM) để có thể hiểu được Semantics của ngôn ngữ tự nhiên.**

---

## Tổng Kết: Chiến Thuật Khuyên Dùng Cho Dự Án RAG Tương Lai

Từ các thử nghiệm trên, đây là "kim chỉ nam" khi xây dựng bất kỳ hệ thống RAG (Retrieval-Augmented Generation) nào trong thực tế:

1. **Về Dữ liệu (Data Governance):**
   - **Luôn dọn dẹp trước khi nạp**: Loại bỏ các thẻ HTML rác, ký tự xuống dòng thừa, và các thành phần định dạng không mang ý nghĩa trước khi Vector hóa.
   - **Gắn siêu dữ liệu (Metadata) phong phú**: Đừng chỉ lưu mỗi nội dung văn bản. Việc gán thêm các trường như `source_url`, `audience`, `category`, `date_updated` giúp bạn linh hoạt lọc (filter) kết quả cực nhanh và chính xác sau này.

2. **Về Kỹ thuật Cắt (Chunking Strategy):**
   - **Tránh dùng Fixed-Size mù quáng**: Cắt theo số lượng ký tự cố định luôn là hạ sách vì nó rất dễ cắt ngang câu cú và phá vỡ ngữ nghĩa.
   - **Ưu tiên Document-Structure/Heading Chunking**: Hãy bám vào cấu trúc của tài liệu gốc (tiêu đề bài, thẻ markdown `#`). Nếu đoạn quá dài, dùng đệ quy (Recursive) nhưng **phải luôn đính kèm lại tiêu đề** ở đầu mỗi đoạn con để duy trì ngữ cảnh.
   - **Luôn dùng Overlap**: Cấu hình `overlap` (khoảng 10-20% dung lượng chunk) là tấm lưới an toàn giúp bảo vệ các câu giao nối giữa hai đoạn không bị đứt đoạn thông tin.

3. **Về Cơ chế Tìm kiếm (Vector Store):**
   - **Lọc trước, tìm sau (Pre-filtering)**: Luôn áp dụng metadata filter TRƯỚC khi chạy tìm kiếm vector (Cosine Similarity). Tránh việc top-K kết quả quý giá bị chiếm mất bởi các dữ liệu không thuộc phạm vi tìm kiếm.
   - **Giấu Vector khi xuất kết quả**: Các vector nhúng (như 1536 chiều của OpenAI) rất nặng. Sau khi tìm xong, luôn bỏ trường `embedding` đi để làm nhẹ bộ nhớ và không làm "lụt" (overflow) context window khi đưa vào Prompt.

4. **Về Ràng Buộc Tác Tử (Agent Prompting):**
   - **Cơ chế chống Ảo giác (Zero Hallucination)**: LLM rất dễ bịa chuyện (Hallucination). Prompt luôn cần câu lệnh nghiêm ngặt: *"Chỉ trả lời dựa trên ngữ cảnh được cung cấp. Nếu không có thông tin, bắt buộc nói 'Tôi không biết'."*
   - **Bắt buộc truy vết nguồn (Traceability)**: Đánh số thứ tự từng chunk đầu vào (VD: `[1] Nguồn: ...`) và yêu cầu LLM trích dẫn chính xác số `[1]` vào câu trả lời để người dùng có thể tự kiểm chứng thông tin dễ dàng.

5. **Về Đánh giá (Evaluation):**
   - **Không chấm điểm mù quáng theo doc_id**: Lấy ra đúng tên file chưa chắc đã giải quyết được vấn đề (vì có thể chunk đó nằm ở phần giới thiệu của file, không chứa đáp án). Việc chấm điểm RAG phải được tiến hành bằng việc dò tìm nội dung (string matching) để đảm bảo chunk thực sự chứa thông tin giải quyết được câu hỏi.
