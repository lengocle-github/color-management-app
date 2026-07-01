# Requirements Document

## Intent Analysis

- **User Request**: Xây dựng tool điều khiển RGB LED trên card đồ họa Colorful iGame GeForce RTX 5070 Ultra W OC 12GB bằng code, vì các phần mềm hiện có (iGame Center, OpenRGB) không hoạt động được với card này.
- **Request Type**: New Project
- **Scope Estimate**: Single Component (GPU RGB controller)
- **Complexity Estimate**: Moderate — cần reverse engineering I2C/SMBus protocol, xây dựng GUI application

---

## Project Context

| Attribute | Value |
|---|---|
| GPU Model | Colorful iGame GeForce RTX 5070 Ultra W OC 12GB |
| OS | Windows 11 |
| Failed Software | iGame Center, OpenRGB (cả hai đều không detect/điều khiển được) |
| Tool Type | GUI Application |
| Language | AI chọn (không có ưu tiên cụ thể) |

---

## Functional Requirements

### FR-01: GPU RGB Detection
- Tool phải detect được card Colorful iGame RTX 5070 Ultra W OC trên hệ thống
- Hiển thị thông tin card (tên, bus address, LED controller info)

### FR-01B: Override & Clear External RGB Settings
- Khi app khởi động, phải clear/override mọi setting RGB mà ứng dụng khác (iGame Center, OpenRGB, etc.) đã apply trước đó
- Ghi đè trực tiếp vào LED controller registers để xoá trạng thái cũ
- Exclusive control mode: có thể khoá LED controller để app khác không can thiệp được
- An toàn: chỉ thao tác lên LED controller, KHÔNG ảnh hưởng đến GPU core, memory, hay clock speed
- Periodic re-write option: tự động ghi lại state mỗi N giây để chống bị override bởi app khác

### FR-02: Static Color Control
- Cho phép user set màu LED cố định (static color)
- Hỗ trợ color picker (RGB/HEX input)
- Áp dụng màu ngay lập tức

### FR-03: Dynamic Color (Condition-Based)
- Đổi màu LED theo điều kiện:
  - GPU temperature thresholds (ví dụ: xanh < 60°C, vàng 60-80°C, đỏ > 80°C)
  - GPU load percentage
  - Custom conditions do user định nghĩa

### FR-04: LED Effects
- Hỗ trợ các hiệu ứng cơ bản:
  - Breathing (fade in/out)
  - Rainbow cycle
  - Wave
  - Color cycle (transition giữa nhiều màu)
  - Strobe/Flash
  - Comet (sáng chạy theo 1 hướng rồi mờ dần)
  - Pulse (nhanh hơn breathing, nhịp tim)
  - Speed + brightness adjustment cho mỗi hiệu ứng

### FR-04B: Preset Color Themes (Bộ màu nổi tiếng)
- Hỗ trợ các bộ màu/effect preset phổ biến:
  - **Cyberpunk** — Tím neon (#b026ff) + Xanh cyan (#00fff7) + Hồng hot pink (#ff2d95)
  - **Vaporwave** — Tím pastel (#c774e8) + Hồng (#ff6ad5) + Xanh mint (#c7f0db)
  - **Aurora Borealis** — Xanh lá (#00ff87) + Xanh dương (#00d4ff) + Tím (#b24dff)
  - **Lava** — Đỏ (#ff1e00) + Cam (#ff8c00) + Vàng (#ffd700)
  - **Ocean** — Xanh đậm (#0a1628) + Xanh biển (#1e90ff) + Cyan (#00ced1)
  - **Sunset** — Cam (#ff6b35) + Hồng (#f7567c) + Tím (#6b2fa0)
  - **Matrix** — Xanh lá đậm (#003b00) + Xanh lá sáng (#00ff41) + Trắng xanh (#ccffcc)
  - **Iron Man** — Đỏ (#b22222) + Vàng gold (#ffd700) + Trắng ấm (#fff8dc)
  - **Arctic** — Trắng (#ffffff) + Xanh ice (#a5f3fc) + Xanh cobalt (#0047ab)
  - **Stealth** — Đen (#0a0a0a) + Xám (#333333) + Đỏ tối (#8b0000)
  - **RGB Classic** — Đỏ (#ff0000) → Xanh lá (#00ff00) → Xanh dương (#0000ff) cycle
  - **Pastel Dream** — Hồng nhạt (#ffc8dd) + Tím nhạt (#bde0fe) + Xanh nhạt (#a2d2ff)
  - **Fire & Ice** — Đỏ/cam gradient ↔ Xanh/cyan gradient (alternating)
  - **Galaxy** — Tím đậm (#2d1b69) + Xanh navy (#1a1a4e) + Vàng sao (#ffd700)
  - **Sakura** — Hồng cherry (#ffb7c5) + Trắng (#ffffff) + Xanh lá nhạt (#c8e6c9)
- Mỗi preset có thể kết hợp với effect (breathing, wave, cycle...)
- User có thể tạo custom theme riêng từ bất kỳ tổ hợp màu nào

### FR-05: LED Power Off
- Cho phép tắt LED hoàn toàn
- Lưu trạng thái để restore khi bật lại

### FR-06: Profile Management
- Lưu/load profiles (preset màu + hiệu ứng)
- Hỗ trợ nhiều profiles
- Auto-apply profile khi khởi động (optional)

### FR-07: GUI Interface
- Giao diện đồ hoạ trực quan
- Preview màu/hiệu ứng trước khi apply
- System tray icon (minimize to tray)
- Start with Windows option

---

## Non-Functional Requirements

### NFR-01: Communication Protocol
- Giao tiếp với GPU LED controller qua I2C/SMBus
- Phải xác định đúng I2C address và protocol cho RTX 5070 Ultra W
- Xử lý an toàn — không gửi lệnh sai gây hỏng hardware

### NFR-02: Performance
- Không gây giảm hiệu suất GPU khi chạy
- CPU usage < 1% khi idle
- Response time < 100ms khi đổi màu

### NFR-03: Stability
- Không crash khi GPU đang chạy game/heavy load
- Graceful error handling khi không thể giao tiếp với LED controller
- Auto-reconnect nếu mất kết nối

### NFR-04: Compatibility
- Windows 11 (primary target)
- NVIDIA driver compatibility (không conflict với driver)
- Chạy được song song với các app khác (game, monitoring tools)

### NFR-05: Usability
- GUI dễ sử dụng, không cần kiến thức kỹ thuật
- Hỗ trợ tiếng Việt và tiếng Anh

---

## Technical Considerations

### I2C/SMBus Communication
- RTX 5070 là card rất mới (2025), protocol có thể chưa được document
- Cần research/reverse engineer protocol từ:
  - OpenRGB source code (nếu có support tương tự cho dòng Colorful)
  - I2C bus scanning trên Windows
  - So sánh với protocol của RTX 4000 series Colorful (nếu tương tự)

### Language & Framework Recommendation
- **Khuyến nghị**: Python + PyQt6/PySide6 cho GUI
  - Python: Dễ prototype, có thư viện I2C/SMBus, cộng đồng lớn
  - PyQt6: GUI framework mature, cross-platform
  - Thay thế: C++ + Qt nếu cần performance cao hơn
- **I2C access trên Windows**: Sử dụng NVIDIA I2C API hoặc WinRing0 driver

### Risk Assessment
- **High Risk**: Protocol chưa được document cho RTX 5070 — cần reverse engineering
- **Medium Risk**: Gửi sai lệnh I2C có thể gây treo card (cần safety checks)
- **Low Risk**: GUI development, profile management

---

## Extension Configuration

| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No | Requirements Analysis |
| Property-Based Testing | Yes (Full) | Requirements Analysis |

---

## PBT Applicability Assessment

Các khu vực cần property-based testing:
- **Round-trip (PBT-02)**: Serialize/deserialize profile data, color format conversions (RGB ↔ HEX ↔ HSV)
- **Invariant (PBT-03)**: Color value clamping (0-255), temperature threshold ordering
- **Idempotence (PBT-04)**: Applying same color twice = same state
- **Stateful (PBT-06)**: Profile state management, LED controller state machine

---

## Out of Scope
- Hỗ trợ card đồ hoạ khác hãng (chỉ focus Colorful iGame RTX 5070)
- Linux support (chỉ Windows 11)
- Fan control hoặc OC features
- Network/remote control
