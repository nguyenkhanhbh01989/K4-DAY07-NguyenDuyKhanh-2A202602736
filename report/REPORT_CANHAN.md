# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Cosine similarity cao (gần 1) nghĩa là hai vector có hướng gần giống nhau trong không gian vector, tức là ngữ nghĩa của hai văn bản tương đương hoặc rất gần nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Mèo là thú cưng rất đáng yêu."
- Câu B: "Loài miu là vật nuôi cực kỳ dễ thương."
- Tại sao tương đồng: Khác biệt từ vựng hoàn toàn ("Mèo" vs "loài miu", "thú cưng" vs "vật nuôi", "đáng yêu" vs "dễ thương") nhưng mang cùng một ý nghĩa, chứng tỏ embedding nắm bắt ngữ nghĩa thay vì chỉ so khớp từ vựng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Lãi suất ngân hàng tăng mạnh."
- Câu B: "Bầu trời hôm nay rất trong xanh."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau (tài chính vs thời tiết), không có điểm chung về ngữ nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity chỉ quan tâm đến góc (hướng) giữa hai vector, bỏ qua độ dài vector. Độ dài vector thường bị ảnh hưởng bởi độ dài văn bản hoặc tần suất từ ngữ, nhưng không phản ánh ngữ nghĩa; do đó cosine phản ánh độ tương đồng ý nghĩa tốt hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Sử dụng công thức ceil((độ_dài − overlap) / (chunk_size − overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23 chunks.
> *Đáp án:* 23 chunks. Đã kiểm chứng qua Python (FixedSizeChunker).

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Nếu overlap tăng lên 100, số chunk tăng lên thành 25 chunks (ceil(9900/400)). Dù tốn thêm chunk, độ chồng chéo lớn hơn giúp duy trì trọn vẹn ngữ cảnh giữa các đoạn văn liên tiếp; giảm thiểu rủi ro cắt ngang ý quan trọng khiến hệ thống RAG mất ngữ cảnh khi truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* Tôi dùng biểu thức chính quy với lookbehind tích cực `re.split(r'(?<=\. )|(?<=\! )|(?<=\? )|(?<=\.\n)', text)` để chia nhỏ thành từng câu nhưng vẫn giữ lại các dấu ngắt câu đi kèm câu trước đó. Một ngoại lệ (edge case) chưa được xử lý triệt để là các chữ viết tắt (như TS., GS.) và số thập phân, vì dấu chấm ở đó sẽ khiến câu bị cắt rời sai lệch.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?* Thuật toán thử cắt bằng separator lớn trước để giữ lại tối đa ngữ nghĩa; các mảnh lớn hơn `chunk_size` sẽ đệ quy bằng separator nhỏ hơn, và cuối cùng các mảnh nhỏ kề nhau được gom nối (agglomerate) cho sát với `chunk_size` nhất. Các base case bao gồm: văn bản trống, văn bản đã ngắn hơn `chunk_size`, và khi đã hết separator để phân chia.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?* Các chunk được chuẩn hoá qua `_make_record` (sao chép metadata và bảo đảm có khóa `doc_id` trỏ về file gốc) rồi lưu vào một list in-memory (`self._store`). Khi tìm kiếm, thuật toán tính tích vô hướng (dot product) giữa vector truy vấn và embedding của từng chunk, sau đó loại bỏ trường embedding cho gọn, sắp xếp giảm dần theo score và lấy top k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?* Hàm `search_with_filter` sẽ duyệt và lọc các chunk có metadata trùng khớp TRƯỚC, sau đó mới gọi hàm search; điều này đảm bảo các chunk không hợp lệ không chiếm mất k slot kết quả. Hàm `delete_document` xóa tài liệu bằng cách duyệt lại `self._store` và chỉ giữ lại những chunk có `metadata['doc_id']` khác với doc_id truyền vào.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?* Trước tiên hàm kiểm tra nếu store rỗng hoặc không tìm được chunk liên quan sẽ trả về câu thông báo ngay để không tốn kém gọi LLM vô ích. Nếu có kết quả, ngữ cảnh được dựng bằng cách đánh số thứ tự từng chunk kèm theo nguồn (vd: [1] Source: ...), đưa vào prompt với ràng buộc LLM không được bịa đặt và bắt buộc phải trích dẫn số thứ tự khi trả lời để truy vết nguồn gốc (Source Traceability).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42 (Hoàn thành mốc quan trọng nhất Checkpoint 4)

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Học bổng thủ khoa đầu vào dành cho đối tượng nào? | `scholarship-ou2026`: Học bổng Tài năng năm học 2026–2027... | 0.303 | Không (Điểm 0) | I cannot answer this based on the provided context. |
| 2 | Học bổng khuyến khích học tập yêu cầu điểm trung bình bao nhiêu? | `scholarship-luatmk2026`: Mức học bổng bằng 100% lương cơ sở tương đương... | 0.303 | Không (Điểm 0) | I cannot answer this based on the provided context. |
| 3 | Quyền lợi của học bổng doanh nghiệp AEON là gì? | `scholarship-haui2026`: Hướng dẫn đăng ký xét tuyển sớm... | 0.266 | Không (Điểm 0) | I cannot answer this based on the provided context. |
| 4 | Thời gian hết hạn nộp hồ sơ xin học bổng? | `scholarship-luatmk2026`: Chính sách học bổng, học phí dành cho học sinh... | 0.334 | Không (Điểm 0) | I cannot answer this based on the provided context. |
| 5 | Thủ tục xin học bổng bao gồm những giấy tờ gì? | `scholarship-harvardetest2026`: Du học Mỹ nên học ngành gì... | 0.315 | Không (Điểm 0) | I cannot answer this based on the provided context. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 0 / 5 (Do sử dụng MockEmbedder băm MD5, số liệu bị nhiễu hoàn toàn, trả về văn bản không liên quan đến ý nghĩa).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Tôi học được sự khác biệt giữa hai mức chấm điểm: không phải cứ lấy được đúng file (doc_id) là thành công. Cần phải kiểm tra xem ngữ cảnh (chunk) đó có chứa "gold answer" hay không, bởi một chunk trong file đúng vẫn có thể không chứa câu trả lời.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
