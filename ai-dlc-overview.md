# AI-DLC (AI Development Life Cycle) - Giải thích tổng quan

AI-DLC là một quy trình phát triển phần mềm có cấu trúc, được thiết kế để AI hỗ trợ từ ý tưởng đến triển khai. Nó gồm **3 phase chính**:

---

## 🔵 INCEPTION PHASE — "Xây cái gì và tại sao?"

Phase này tập trung vào việc lập kế hoạch, thu thập yêu cầu và quyết định kiến trúc.

| # | Stage | Khi nào chạy | Mục đích |
|---|-------|--------------|----------|
| 1 | **Workspace Detection** | LUÔN LUÔN | Quét workspace hiện tại — xác định đây là dự án mới (greenfield) hay dự án có sẵn (brownfield) |
| 2 | **Reverse Engineering** | Chỉ khi brownfield | Phân tích mã nguồn hiện có — tạo tài liệu kiến trúc, API, dependencies, tech stack |
| 3 | **Requirements Analysis** | LUÔN LUÔN | Phân tích yêu cầu — từ tối thiểu (yêu cầu đơn giản) đến toàn diện (yêu cầu phức tạp, rủi ro cao) |
| 4 | **User Stories** | Điều kiện | Tạo user stories nếu có feature ảnh hưởng đến người dùng, nhiều personas, hoặc logic phức tạp |
| 5 | **Workflow Planning** | LUÔN LUÔN | Lập kế hoạch workflow — xác định phase nào sẽ chạy, độ sâu của mỗi phase |
| 6 | **Application Design** | Điều kiện | Thiết kế component, service layer, business rules khi cần tạo component mới |
| 7 | **Units Generation** | Điều kiện | Chia hệ thống thành các đơn vị công việc (units) khi dự án phức tạp, nhiều module |

---

## 🟢 CONSTRUCTION PHASE — "Xây như thế nào?"

Phase này thiết kế chi tiết và sinh code. Mỗi **unit** được hoàn thành đầy đủ trước khi chuyển sang unit tiếp theo.

### Per-Unit Loop (lặp cho mỗi unit):

| # | Stage | Khi nào chạy | Mục đích |
|---|-------|--------------|----------|
| 1 | **Functional Design** | Điều kiện | Thiết kế data model, business logic chi tiết |
| 2 | **NFR Requirements** | Điều kiện | Xác định yêu cầu phi chức năng (performance, security, scalability) |
| 3 | **NFR Design** | Điều kiện | Thiết kế pattern để đáp ứng NFR |
| 4 | **Infrastructure Design** | Điều kiện | Thiết kế hạ tầng, cloud resources, deployment architecture |
| 5 | **Code Generation** | LUÔN LUÔN | Sinh code — gồm 2 phần: lập kế hoạch → sinh code theo kế hoạch |

### Sau khi tất cả units hoàn thành:

| # | Stage | Khi nào chạy | Mục đích |
|---|-------|--------------|----------|
| 6 | **Build and Test** | LUÔN LUÔN | Tạo hướng dẫn build, unit test, integration test, performance test |

---

## 🟡 OPERATIONS PHASE — "Triển khai và vận hành"

Hiện tại là **placeholder** (chưa triển khai đầy đủ). Trong tương lai sẽ bao gồm:

- Deployment planning
- Monitoring & observability
- Incident response
- Maintenance workflows

---

## Nguyên tắc chính

- **Adaptive** — Workflow tự điều chỉnh theo độ phức tạp, không bắt buộc chạy hết tất cả stage
- **User Control** — Mỗi stage đều chờ user phê duyệt trước khi tiến tiếp
- **Audit Trail** — Mọi input/output được ghi log đầy đủ
- **Extensions** — Có thể bật thêm module mở rộng (security baseline, property-based testing...)
- **Content Validation** — Validate mọi nội dung trước khi tạo file

---

## Tóm tắt

**Inception** = hiểu vấn đề → **Construction** = thiết kế & code → **Operations** = triển khai.

Mỗi bước đều có cơ chế kiểm soát để đảm bảo chất lượng và phù hợp với yêu cầu thực tế.
