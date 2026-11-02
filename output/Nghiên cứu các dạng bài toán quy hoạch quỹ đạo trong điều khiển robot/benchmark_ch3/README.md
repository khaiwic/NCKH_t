# Dữ liệu so sánh thuật toán cho mục 3.4

Đây là kết quả chạy mô phỏng hình học trên máy tính Windows, không phải phép đo trên Colab, ESP32 hay robot thật. Ngày thực hiện: 02/11/2026.

## Chạy lại

Từ thư mục dự án, chạy:

    python -B code/benchmark_ch3/benchmark_ch3.py

Cần Python, NumPy và Matplotlib. Kiểm tra thuật toán và hình học mà không chạy toàn bộ phép đo:

    python -B code/benchmark_ch3/benchmark_ch3.py --validate-only

Mã nguồn nằm tại ../../code/benchmark_ch3/benchmark_ch3.py. Các mã minh họa Dijkstra/A* bốn hướng trước đây và dữ liệu Chương 4 được giữ nguyên. Bộ so sánh này dùng riêng các cài đặt trên cùng giao diện, lưới tám hướng và cùng kiểm tra va chạm.

## Thiết lập và giới hạn

- 3 bản đồ cố định, 5 thuật toán, 30 lượt mỗi cặp: tổng 450 lượt.
- Miền 6 x 4 m; lưới 0,10 m; S=(0,35; 1,95), G=(5,65; 1,95) m. Tọa độ mọi hình chữ nhật nằm trong config.json.
- Robot là đĩa bán kính giả định 0,11 m. Mở rộng hộp chữ nhật thêm 0,26 m khi quy hoạch và 0,21 m khi kiểm tra làm mượt. Đây là bao bảo thủ của tổng Minkowski với đĩa, có dư ở góc.
- Dijkstra/A*: tám hướng, cấm cắt góc; A* dùng octile. Tạo lưới nằm trong thời gian đo.
- PRM: 500 mẫu tự do, 12 láng giềng, dựng lại roadmap từng lượt, truy vấn Dijkstra. Tách build_ms/query_ms; tổng thời gian còn gồm khởi tạo và dựng kết quả.
- RRT*: 1500 vòng lặp, bước 0,40 m, goal bias 5%, gamma=6 cho bán kính láng giềng. Chọn kết nối đích tốt nhất ở cuối ngân sách, không dừng ở nghiệm đầu tiên.
- APF cơ bản: k_att=1, k_rep=0,035, rho0=0,60 m, bước tối đa 0,03 m, tối đa 3000 bước; giảm bước nếu cạnh không an toàn. Lực đẩy chỉ xét vật cản nội bộ; biên bản đồ được kiểm tra như ràng buộc chuyển động. Không có sửa GNRON, lực ảo hoặc thoát bẫy ngẫu nhiên. Dừng không tiến triển nếu khoảng cách đích giảm dưới 0,001 m trong cửa sổ 100 bước; đây là tiêu chí thực dụng, không phải chứng minh cực tiểu.
- Cùng giới hạn tìm đường 2 giây. Mỗi cặp thuật toán/bản đồ có một lượt khởi động không tính. Hoán đổi thứ tự thuật toán theo seed; seed chính thức 20261102..20261131.
- Dijkstra, A* và APF là tất định trong cấu hình này: 30 lần chạy trên cùng bản đồ không phải 30 môi trường độc lập và không chứng minh xác suất thành công tổng quát.
- Hậu xử lý chung: nối tắt có kiểm tra, Bézier bậc 2 với khoảng lùi tối đa 0,15 m và tối đa 40% hai đoạn kề, giảm nửa tối đa 14 lần. Đường cong dùng 301 điểm. Kiểm tra dây cung cộng cận sai lệch đường bậc 2 so với dây cung. Không tự suy ra G2/C2.
- J_kappa tính bằng đạo hàm Bézier và tích phân hình thang; không phải jerk. Khoảng hở tính theo thân bao đĩa tới vật cản gốc hoặc biên bản đồ, lấy mẫu dày tối đa 0,002 m.

## Cách đo và thống kê

- planning_ms và post_ms dùng perf_counter_ns: thời gian trôi qua, có ảnh hưởng của lập lịch Windows, không phải CPU thuần. Không tính vẽ hình hay đọc/ghi dữ liệu.
- planning_ms tổng hợp trên mọi lượt. post_ms trên lượt tìm thấy đường; các chỉ tiêu hình học trên lượt đạt sau hậu xử lý. Lượt thất bại giữ nguyên trạng thái, để null cho chỉ tiêu không xác định.
- Bảng hình học trong báo cáo dùng trung bình; CSV/summary giữ đầy đủ độ lệch chuẩn mẫu. Không gán đường dài bằng 0 cho APF thất bại.
- Tỷ lệ đạt ở Chương 3 là quy hoạch hình học; không thay thế tỷ lệ hoàn thành nhiệm vụ có định vị và điều khiển ở Chương 4.
- Tất cả các đường thô được kiểm tra liên tục theo đoạn với hình chữ nhật mở rộng; đường sau xử lý được kiểm tra lại. Thân xe, khoảng dự phòng và bản đồ là giả định mô phỏng.

## Tệp minh chứng

- config.json: môi trường, tham số, seed, bản đồ và SHA-256 mã nguồn.
- per_run_metrics.csv / per_run_metrics.json: toàn bộ 450 lượt, thời gian, trạng thái, chỉ tiêu và số nút nếu có.
- paths.json: đường thô, đường nối tắt, đường sau làm mượt và ba điểm điều khiển của từng đoạn Bézier cho tất cả lượt đạt.
- summary.json: thống kê theo thuật toán và bản đồ.
- validation.json: kiểm tra cạnh xuyên vật cản, tiếp xúc biên, đường không vật cản dài 5,3 m, chi phí A*/Dijkstra bằng nhau, khoảng hở và tính lại thống kê từ CSV; đồng thời ghi lượt chọn cho hình đại diện.
- independent_audit.json: kiểm tra lại chỉ tiêu độ cong bằng tích phân Gauss từ các điểm điều khiển đã lưu.
- report_section.tex: nội dung mục 3.4 đã đưa vào main.tex.
- section_3_4_before.tex: mục 3.4 trước đợt sửa này.
- sha256.json: mã kiểm tra dữ liệu chính thức.

Hình bản đồ và hình đường đại diện được lưu vào LaRex/picture/Hinh3_8_Ban_do_so_sanh.png và Hinh3_9_Duong_di_so_sanh.png. Chọn đại diện theo trung vị trên của chiều dài sau xử lý trong các lượt đạt; không chọn theo hình đẹp nhất.

## Giai đoạn kiểm tra trước phép đo chính thức

Thư mục pilot_cpu_timer lưu nguyên kết quả thử ban đầu và bản mã tương ứng. Đồng hồ process_time_ns trên máy Windows này có lượng tử thời gian thô, làm xuất hiện thời gian 0 cho tác vụ ngắn; phép đo chính thức dùng perf_counter_ns. Cấu hình APF chính thức chỉ tạo trường đẩy từ các vật cản nội bộ theo bài toán APF cơ bản; cấu hình thử ban đầu còn bổ sung lực đẩy biên, làm xuất hiện đình trệ gần đích ngay cả ở bản đồ không có vật cản bên trong. Cấu hình cuối được ghi đầy đủ trong config.json và không hiệu chỉnh riêng giữa các bản đồ. Các bảng báo cáo chỉ dùng dữ liệu chính thức ở thư mục hiện tại.

## Ý nghĩa kết quả

Bốn phương pháp Dijkstra, A*, PRM, RRT* đạt 30/30 trên mỗi bản đồ. APF đạt ở M0, dừng không tiến triển ở M1/M2. A* nhanh hơn Dijkstra trong phép đo; RRT* cho đường sau xử lý ngắn hơn và J_kappa trung bình thấp hơn trên M1/M2. Chọn Dijkstra làm cấu hình cơ sở thuận tiện kiểm chứng là quyết định thiết kế; dữ liệu không chứng minh Dijkstra tốt nhất hoặc hiệu năng tương ứng trên ESP32.
