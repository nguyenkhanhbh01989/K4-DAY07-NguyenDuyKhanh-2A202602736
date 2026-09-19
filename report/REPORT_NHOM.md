# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** [ví dụ: Customer support FAQ, Luật Việt Nam, công thức nấu ăn, ...]

**Tại sao nhóm chọn chủ đề này?**
> *Viết 2-3 câu:*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| scholarship-luatmk2026 | FixedSizeChunker (`fixed_size`) | 45 | 499.7 | Dễ bị cắt ngang câu, mất ngữ cảnh. |
| scholarship-luatmk2026 | SentenceChunker (`by_sentences`) | 38 | 532.3 | Giữ trọn vẹn câu nhưng không kiểm soát tốt kích thước. |
| scholarship-luatmk2026 | RecursiveChunker (`recursive`) | 51 | 395.8 | Tốt nhất do ưu tiên ngắt đoạn văn và câu hoàn chỉnh. |
| scholarship-ou2026 | FixedSizeChunker (`fixed_size`) | 20 | 480.9 | Kém, làm đứt gãy thông tin quan trọng ở ranh giới. |
| scholarship-ou2026 | SentenceChunker (`by_sentences`) | 16 | 536.9 | Khá ổn nhưng đôi lúc sinh ra chunk quá dài. |
| scholarship-ou2026 | RecursiveChunker (`recursive`) | 20 | 431.5 | Đảm bảo cả kích thước và độ trọn vẹn ngữ nghĩa tốt nhất. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — Khánh**
- **Loại chiến lược:** custom (HeadingChunker)
- **Mô tả & lý do chọn cho chủ đề này:** Dựa trên cấu trúc tự nhiên của văn bản quy định, học bổng thường được chia sẵn theo các đề mục (Heading). Việc cắt theo Heading giúp bảo toàn trọn vẹn một ý (Ví dụ: "Điều kiện xét tuyển", "Hồ sơ cần nộp"). Khi một section quá dài, chiến lược sẽ kết hợp đệ quy nhưng luôn gắn lại tiêu đề vào các đoạn nhỏ để không bị mất ngữ cảnh gốc.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.recursive = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text: return []
        parts = re.split(r'(?=\n#+ )', "\n" + text.strip())
        chunks = []
        for part in parts:
            part = part.strip()
            if not part: continue
            if len(part) <= self.chunk_size:
                chunks.append(part)
            else:
                lines = part.split("\n", 1)
                heading = lines[0] + "\n" if lines[0].startswith("#") else ""
                content = lines[1] if len(lines) > 1 and heading else part
                sub_chunks = self.recursive.chunk(content)
                for sc in sub_chunks:
                    chunks.append(heading + sc.strip() if heading else sc.strip())
        return chunks
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Học bổng thủ khoa đầu vào dành cho đối tượng nào? | Sinh viên mới trúng tuyển với số điểm cao nhất. | `scholarship-ou2026` / `scholarship-haui2026` |
| 2 | Học bổng khuyến khích học tập yêu cầu điểm trung bình bao nhiêu? | Từ 3.6 trở lên. | `scholarship-luatmk2026` |
| 3 | Quyền lợi của học bổng doanh nghiệp AEON là gì? | Tài trợ 100% học phí và có cơ hội thực tập. | `scholarship-ftu-aeon2026` |
| 4 | Thời gian hết hạn nộp hồ sơ xin học bổng? | Ngày 30/10 hàng năm. | `scholarship-luatmk2026` |
| 5 | Thủ tục xin học bổng bao gồm những giấy tờ gì? | Bảng điểm, đơn xin học bổng, giấy tờ chứng minh hoàn cảnh (nếu có). | `scholarship-harvardetest2026` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:* Có, lọc bằng metadata đóng vai trò mang tính quyết định để chặn nhầm lẫn đối tượng. Trong kết quả A/B Test của Câu hỏi 1, khi KHÔNG dùng filter, chunk lọt Top 1 thuộc về `scholarship-haui2026`. Nhưng khi BẬT `metadata_filter={"audience": "student"}`, hệ thống lập tức loại bỏ kết quả sai kia và đẩy `scholarship-ou2026` lên Top 1 (đúng đối tượng sinh viên), chứng minh vai trò thiết yếu của Pre-filtering.

---

## 4. Thuyết trình (Demo) & Phân tích lỗi (Failure Analysis) — Nhóm (5 điểm)

**Phân tích một Failure Case điển hình:**
> - **Câu hỏi thất bại:** Câu 2 - "Học bổng khuyến khích học tập yêu cầu điểm trung bình bao nhiêu?"
> - **Nguyên nhân:** Do sử dụng MockEmbedder (băm MD5), kết quả tìm kiếm giống hệt như random. Mặc dù `doc_id` gold là `scholarship-luatmk2026` có lọt vào Top 1, nhưng đoạn chunk được lấy ra lại hoàn toàn nói về "Mức học bổng bằng 100% lương cơ sở" chứ không chứa thông tin "Từ 3.6 trở lên". Lỗi này xảy ra vì Cosine Similarity lúc này không đo độ tương đồng về mặt ngữ nghĩa (Semantics).
> - **Đề xuất sửa chữa:** Cần thay thế MockEmbedder bằng một mô hình nhúng thực thụ (Ví dụ: OpenAI hoặc `all-MiniLM-L6-v2`) để các chunk được vector hóa đúng theo ý nghĩa, từ đó đưa chunk có chứa con số "3.6" lên Top 1.

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu:* Việc chunk văn bản không chỉ là đếm số lượng ký tự, mà là việc bảo toàn cấu trúc dữ liệu. Cùng một tài liệu, nếu cắt cứng (FixedSize) có thể cắt ngang một câu chứa đáp án làm hỏng ngữ nghĩa; nhưng khi cắt theo cấu trúc Heading, ta bảo toàn được toàn vẹn thông tin gốc của đề mục đó và tránh việc mô hình LLM bị thiếu bối cảnh.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
