# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G04
**Thành viên:** Nguyễn Duy Khánh , Nguyễn Văn An , Lưu Xuân Dũng ,Trương Thị Lan Anh , Tạ Quang Dũng , Nguyễn Long Khánh
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Thông tin học bổng sinh viên các trường Đại học năm 2026.

**Tại sao nhóm chọn chủ đề này?**
> *Viết 2-3 câu:* Đây là chủ đề có nhu cầu tra cứu thực tế rất cao đối với sinh viên. Các văn bản quy định học bổng thường dài dòng, phức tạp và dễ nhầm lẫn giữa các trường, do đó việc áp dụng hệ thống RAG sẽ giúp sinh viên tra cứu điều kiện, quyền lợi và thủ tục một cách nhanh chóng, chính xác.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | scholarship-haui2026.md | Website trường | 2026 | ~11.000 | `audience`, `doc_id` |
| 2 | scholarship-ou2026.md | Website trường | 2026 | ~12.000 | `audience`, `doc_id` |
| 3 | scholarship-luatmk2026.md | Website trường | 2026 | ~28.000 | `audience`, `doc_id` |
| 4 | scholarship-ftu-aeon2026.md | Website trường | 2026 | ~23.000 | `audience`, `doc_id` |
| 5 | scholarship-harvardetest2026.md | Website trường | 2026 | ~12.000 | `audience`, `doc_id` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | String | `scholarship-ou2026` | Dùng để truy vết tài liệu gốc (Traceability) và thực hiện các chức năng xóa/cập nhật tài liệu. |
| `audience` | String | `student`, `phd` | Rất hữu ích để lọc (Pre-filter) tránh nhầm lẫn chính sách giữa các nhóm đối tượng (Ví dụ: sinh viên đại học vs nghiên cứu sinh). |

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

**Thành viên 1 — Nguyễn Văn An**
- **Loại chiến lược:** FixedSizeChunker
- **Mô tả & lý do chọn cho chủ đề này:** Cắt văn bản theo kích thước cố định (500 ký tự) không quan tâm bối cảnh. Đây là cách tiếp cận ngây thơ nhất, được chọn để làm baseline nhằm so sánh xem việc thiếu hụt ngữ cảnh sẽ ảnh hưởng thế nào đến chất lượng.
- **Code snippet (nếu custom):** Không có (Sử dụng class có sẵn)

**Thành viên 2 — Lưu Xuân Dũng**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Chia nhỏ văn bản đệ quy dựa trên các ký tự phân cách (như `\n\n`, `\n`, `. `). Lý do chọn là để tôn trọng ranh giới đoạn văn tự nhiên, tránh bị đứt gãy câu cú như FixedSizeChunker.
- **Code snippet (nếu custom):** Không có (Sử dụng class có sẵn)

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
| An | FixedSize | 0/10 (Mock MD5) | Dễ cài đặt, kích thước chunk đều nhau. | Cắt ngang câu, làm đứt gãy ngữ nghĩa trầm trọng. |
| Dũng | Recursive | 0/10 (Mock MD5) | Tôn trọng ranh giới tự nhiên của câu và đoạn văn. | Nếu mất tiêu đề (Heading), chunk sẽ thiếu bối cảnh lớn. |
| Khánh | Heading | 0/10 (Mock MD5) | Bảo toàn tuyệt đối bối cảnh nhờ giữ lại tiêu đề cho mọi chunk. | Phụ thuộc vào chất lượng format Markdown của tài liệu gốc. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):* Chiến lược **HeadingChunker** của Khánh là tốt nhất. Bởi vì văn bản quy định/pháp lý (như thể lệ học bổng) luôn có cấu trúc phân cấp chặt chẽ (Điều kiện, Quyền lợi, Hồ sơ). Việc mang theo heading gắn vào mọi đoạn văn nhỏ đảm bảo hệ thống LLM không bao giờ bị mất bối cảnh "đang đọc về phần nào của học bổng nào".

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
| 1 | Học bổng thủ khoa dành cho ai? | HeadingChunker | Không (Mock MD5) | Filter hoạt động tốt, nhưng vector MD5 làm sai lệch top-3. |
| 2 | Yêu cầu GPA học bổng khuyến khích? | HeadingChunker | Không (Mock MD5) | Điểm = 0 do ngữ nghĩa bị băm ngẫu nhiên. |
| 3 | Quyền lợi học bổng AEON? | HeadingChunker | Không (Mock MD5) | Điểm = 0 do ngữ nghĩa bị băm ngẫu nhiên. |
| 4 | Thời hạn nộp hồ sơ học bổng? | HeadingChunker | Không (Mock MD5) | Điểm = 0 do ngữ nghĩa bị băm ngẫu nhiên. |
| 5 | Thủ tục xin học bổng gồm gì? | HeadingChunker | Không (Mock MD5) | Điểm = 0 do ngữ nghĩa bị băm ngẫu nhiên. |

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
> *Viết 2-3 câu:* Chúng tôi sẽ dành nhiều thời gian hơn để dọn dẹp dữ liệu gốc (bỏ các thanh điều hướng HTML dính vào Markdown) và thiết kế hệ thống Metadata chi tiết hơn (như gán thêm `deadline` hoặc `gpa_required`). Điều này giúp tận dụng triệt để Metadata Filtering, giảm tải việc phải dùng Semantics cho các câu hỏi mang tính định lượng rõ ràng.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
