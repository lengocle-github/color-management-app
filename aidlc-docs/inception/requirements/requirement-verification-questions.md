# Requirements Verification Questions

Vui lòng trả lời các câu hỏi sau bằng cách điền ký tự lựa chọn (A, B, C...) sau tag [Answer]:

---

## Question 1
Bạn đang sử dụng card Colorful iGame model nào?

A) iGame RTX 4090 series (Vulcan, Neptune, Advanced)

B) iGame RTX 4080/4080 SUPER series

C) iGame RTX 4070/4070 Ti/4070 SUPER series

D) iGame RTX 4060/4060 Ti series

E) iGame RTX 3000 series (3060, 3070, 3080, 3090)

F) COLORFIRE series (RTX 4060 MEOW, etc.)

X) Other (please describe after [Answer]: tag below)

[Answer]: Colorful iGame GeForce RTX 5070 Ultra W OC 12GB

## Question 2
Hệ điều hành bạn đang dùng trên PC có card đồ họa đó?

A) Windows 10

B) Windows 11

C) Linux (Ubuntu, Fedora, Arch, etc.)

D) Dual boot (Windows + Linux)

X) Other (please describe after [Answer]: tag below)

[Answer]: Windows 11

## Question 3
Bạn đã thử những phần mềm nào mà KHÔNG đổi được màu LED?

A) iGame Center — cài nhưng không detect được card / không có mục RGB

B) iGame Dynamik Light — không hoạt động

C) OpenRGB — không detect được card

D) Cả iGame Center lẫn OpenRGB đều không hoạt động

E) Chưa thử phần mềm nào, muốn viết tool riêng từ đầu

X) Other (please describe after [Answer]: tag below)

[Answer]: iGame Center,  OpenRGB 

## Question 4
Mục tiêu cuối cùng của bạn là gì?

A) Chỉ cần đổi được màu LED cố định (static color) — ví dụ: set xanh dương rồi để yên

B) Đổi màu LED theo điều kiện (ví dụ: đỏ khi GPU nóng, xanh khi mát)

C) Tạo hiệu ứng LED tuỳ chỉnh (breathing, rainbow, wave...)

D) Tắt LED hoàn toàn (đang bị sáng màu không mong muốn)

E) Tất cả các tính năng trên — tool hoàn chỉnh điều khiển RGB

X) Other (please describe after [Answer]: tag below)

[Answer]: E

## Question 5
Ngôn ngữ lập trình bạn muốn dùng hoặc quen thuộc nhất?

A) Python

B) C/C++

C) Rust

D) Node.js / TypeScript

E) Không có ưu tiên — AI chọn ngôn ngữ phù hợp nhất

X) Other (please describe after [Answer]: tag below)

[Answer]: E

## Question 6
Bạn muốn tool này hoạt động như thế nào?

A) Command-line tool (CLI) — chạy lệnh để set màu

B) GUI application — có giao diện đồ hoạ

C) Background service/daemon — tự động đổi màu theo điều kiện

D) CLI + daemon kết hợp

X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 7: Security Extensions
Có cần áp dụng các quy tắc bảo mật (security baseline) cho project này không?

A) Yes — áp dụng tất cả quy tắc bảo mật (khuyến nghị cho ứng dụng production)

B) No — bỏ qua quy tắc bảo mật (phù hợp cho PoC, prototype, experimental)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 8: Property-Based Testing Extension
Có cần áp dụng property-based testing (PBT) cho project này không?

A) Yes — áp dụng tất cả quy tắc PBT (khuyến nghị cho project có business logic, data transformations)

B) Partial — chỉ áp dụng PBT cho pure functions và serialization

C) No — bỏ qua PBT (phù hợp cho CRUD đơn giản, UI-only, integration layer mỏng)

X) Other (please describe after [Answer]: tag below)

[Answer]: A
