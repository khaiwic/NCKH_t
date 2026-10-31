# Kết quả mô phỏng cho Bảng 4.3

Đây là kết quả **chạy mô phỏng số trên máy tính**, không phải dữ liệu đo trên robot hay kết quả thực thi trên ESP32. Mô hình, mã nguồn, tham số và nhật ký được lưu để có thể chạy lại và kiểm tra số liệu. Không thay thế các tham số giả định bằng thông số được cho là đã đo.

## Chạy lại

Tại thư mục `C:\Users\ADMIN\Documents\NCKH`:

```powershell
python -B code/simulation_ch4/simulate_ch4.py
```

Cần Python, NumPy, Matplotlib. Phiên bản Python/NumPy và SHA-256 của mã nguồn nằm trong `config.json`. Chương trình chỉ ghi kết quả vào `output/simulation_ch4`, không tự sửa `main.tex`. Mã nguồn: `../../code/simulation_ch4/simulate_ch4.py`.

## Cấu hình

- Hình học danh định theo báo cáo: bán kính bánh 0,022 m, khoảng cách bánh 0,135 m. Giả định giải mã x4: 1400 đếm/vòng trục đầu ra.
- Bản đồ 4,0 × 2,4 m, lưới 0,05 m. S = (0,3; 1,2) m, G = (3,3; 1,2) m.
- Đường thẳng dài 3 m. Kịch bản còn lại thêm vật cản [1,4; 2,0] × [0,85; 1,55] m; Dijkstra tám hướng, không cắt góc, rút gọn bằng kiểm tra tầm nhìn và bo Bézier bậc hai. Đường cuối dài 3,4119835 m.
- **Giả định** thân xe là đĩa bán kính 0,11 m. Khi quy hoạch, khoảng cách tâm xe tới vật cản tối thiểu 0,26 m; kiểm tra lại đường mượt với khoảng cách tối thiểu 0,21 m. Khoảng hở thực của đường mượt được kiểm tra là 0,1657404 m.
- Pure Pursuit 20 Hz, nhìn trước 0,20 m; PI 100 Hz, Kp = 2, Ki = 8, Kd = 0, duty chuẩn hóa giới hạn ±0,8. Tốc độ encoder lấy bằng sai phân số đếm trên cửa sổ 50 ms.
- Tốc độ dọc đường tăng từ nghỉ với gia tốc 0,20 m/s², chạy đều tối đa 0,25 m/s và giảm tốc theo khoảng còn lại. Giới hạn tốc độ bánh 0,35 m/s, tốc độ góc thân xe 1,5 rad/s. Gần đích có pha căn hướng và chờ ổn định 0,5 s.
- **Giả định** truyền động bậc nhất: dΩ/dt = (g u − Ω)/τ, g danh định 25 rad/s, τ = 0,12 s. Đây không phải mô hình đã nhận dạng cho động cơ ở 7,4 V. Điện áp 7,4 V chỉ là nhãn cấu hình; không có mô hình dòng điện, mô-men hoặc sụt áp nguồn.
- Mỗi lượt lấy mẫu đều độc lập cho bán kính hai bánh ±1%, khoảng cách bánh ±1%, hệ số động cơ ±5%, hằng số thời gian ±15%; trượt mỗi bánh 0–2% cộng dao động ±0,2% ở 0,7 Hz, pha ngẫu nhiên. Lệch tọa độ y ban đầu ±0,02 m, lệch hướng ±0,05 rad. Tư thế đầu biết đúng. Các tham số của hai kịch bản được ghép cặp theo cùng seed.
- Bộ điều khiển dùng Odometry với hình học danh định và encoder lượng tử hóa. Trạng thái thật của mô hình được giữ riêng, chỉ dùng để đánh giá và phát hiện va chạm; không phản hồi vào bộ bám. Sai lệch bán kính/trượt không được bộ điều khiển biết trước.
- Không mô phỏng cảm biến vật cản, SLAM, vật cản động, quy hoạch lại, độ rơ, tải điện hoặc bánh tự lựa. Cần thay các giả định bằng kết quả nhận dạng/đo đạc trước khi dùng để dự báo xe thật.

## Lượt chạy và điều kiện đạt

30 lượt mỗi kịch bản, seed = 20261031 + j, j = 0..29. Không loại bỏ lượt không đạt. Thành công khi bộ điều khiển kết thúc trong 35 s, sai số đích thật ≤ 0,05 m, sai số hướng cuối ≤ 0,10 rad, sai số ngang cực đại ≤ 0,15 m và không va chạm. Bộ điều khiển có ngưỡng dừng trên Odometry riêng (0,015 m, 0,025 rad); dừng theo Odometry không được đồng nhất với đạt đích thật.

Kết quả: đường thẳng 5/30 đạt; có vật cản 5/30 đạt, 3 va chạm. 25 lượt đường thẳng không đạt dung sai. Kịch bản vật cản có 22 lượt kết thúc điều khiển nhưng không đạt dung sai và 3 lượt va chạm. Không có lượt hết thời gian. Kết quả thấp trong cấu hình này phản ánh sai số Odometry chưa bù; không chứng minh Dijkstra không tìm được đường hay robot thật có đúng tỷ lệ đạt này.

## Quy ước thống kê trong bảng

- RMSE vị trí: so sánh trạng thái thật mô phỏng với tham chiếu hình thang **tại cùng thời điểm**, giữ tham chiếu ở đích sau thời gian danh định. Mỗi lượt tính đến lúc kết thúc/va chạm; không kéo dài bằng mẫu giả. Không dùng Odometry làm vị trí đối chứng.
- Sai số hướng: trung bình trị tuyệt đối góc bọc về [−π, π], so với tiếp tuyến của tham chiếu thời gian. Sai số ngang: chiếu lên nhánh đường gần nhất theo tiến triển.
- Các ô `trung bình ± độ lệch chuẩn mẫu` tính trên **cả 30 lượt**, ngoại trừ thời gian hoàn thành chỉ tính trên 5 lượt thành công. Thời gian ghi trong CSV từng lượt là thời điểm kết thúc, bao gồm cả lượt thất bại; không dùng trực tiếp trung bình cột đó làm thời gian hoàn thành.
- Hàng sai số ngang lớn nhất là **cực đại trên cả 30 lượt**, không phải trung bình của cực đại từng lượt.
- Hàng khoảng hở nhỏ nhất là **cực tiểu trên cả 30 lượt**. Giá trị −0,0002488 m là bước phát hiện va chạm với độ xuyên số rất nhỏ; có 3 lượt va chạm, không được diễn giải là tất cả đều an toàn.
- Tỷ lệ bão hòa: phần trăm chu kỳ điều khiển có ít nhất một trong hai giá trị duty chưa cắt vượt/chạm giới hạn ±0,8. Kết quả 0% chỉ áp dụng mô hình giả định này.

## Tệp kết quả

- `table_4_3.csv`: số liệu làm tròn đúng như Bảng 4.3, mở được bằng Excel.
- `summary.json`: thống kê đầy đủ, gồm trung bình thời điểm kết thúc của tất cả lượt và thời gian hoàn thành riêng của lượt thành công.
- `per_run_metrics.csv`, `per_run_metrics.json`: chỉ tiêu và trạng thái của toàn bộ 60 lượt.
- `per_run_parameters.json`: thông số thực của mô hình từng lượt.
- `straight/run_01.csv` ... `run_30.csv`, `obstacle/run_01.csv` ... `run_30.csv`: nhật ký 100 Hz, gồm trạng thái thật, Odometry, encoder, vận tốc đặt/đo, PWM, sai số ngang và khoảng hở.
- `*/reference_path.csv`, `dijkstra_raw.csv`, `dijkstra_shortcuts.csv`: đường tham chiếu và các bước xử lý hình học.
- `simulation_summary.png`: đường đi của cả 30 lượt/kịch bản; đồ thị chi tiết chọn lượt có RMSE ở vị trí trung vị, không chỉ chọn lượt thành công.
- `validation.json`: kiểm tra xe đối xứng không trượt đi thẳng, kiểm tra khoảng hở đường mượt, so sánh giảm đôi bước tích phân cho lượt seed đầu mỗi kịch bản, đọc lại toàn bộ CSV và tính lại các chỉ tiêu trong bảng.
- `sha256.json`: dấu kiểm tra các tệp sinh bởi lần chạy chương trình; README này là tài liệu giải thích bổ sung.

Sai khác lớn nhất khi tính lại từ CSV nhỏ hơn 10⁻⁹. Sai khác RMSE khi giảm bước tích phân từ 0,0025 xuống 0,00125 s nhỏ hơn 10⁻⁶ m trong hai lượt kiểm tra. Đây là kiểm tra tính toán số, không phải kiểm chứng độ đúng của mô hình vật lý.
