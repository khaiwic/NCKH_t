# Nhận xét phản biện báo cáo nghiên cứu khoa học sinh viên

- **Đề tài:** Nghiên cứu các dạng bài toán quy hoạch quỹ đạo trong điều khiển robot.
- **Tệp được đánh giá:** [main.tex](main.tex).
- **Ngày đánh giá:** 02/11/2026.
- **Góc nhìn:** Thành viên hội đồng nghiệm thu kết quả nghiên cứu đề tài sinh viên.
- **Phạm vi:** Đọc nội dung nguồn, đối chiếu mã và hồ sơ mô phỏng Chương 4 đang có. Không biên dịch lại, không chạy lại mô phỏng và chưa đánh giá trực quan toàn bộ PDF.
- **Trạng thái:** Nhận xét phản biện tham khảo, không thay thế kết luận của hội đồng hoặc tiêu chí nghiệm thu chính thức.

## 1. Đánh giá tổng thể

Bản hiện tại có nền tảng lý thuyết khá, có dữ liệu mô phỏng để đối chiếu, nhưng cần bổ sung và chỉnh lý đáng kể trước khi có thể kết luận hoàn thành đầy đủ mục tiêu nghiên cứu. Điểm yếu lớn nhất nằm ở sự thống nhất giữa phương pháp trình bày, phần đã triển khai và bằng chứng đánh giá.

Quan điểm phản biện là **đề nghị bổ sung trước khi xác nhận hoàn thành đầy đủ**. Việc nghiệm thu cuối cùng còn phải đối chiếu đề cương, sản phẩm đã đăng ký và tiêu chí chính thức của đơn vị.

## 2. Những điểm được đánh giá tốt

- Báo cáo phân biệt tương đối rõ đường đi, quỹ đạo và điều khiển bám; chú ý kích thước robot, mở rộng vật cản và kiểm tra lại sau làm mượt.
- Các phần Dijkstra, A*, PRM, RRT* và APF đã nêu điều kiện áp dụng và giới hạn của các bảo đảm lý thuyết khá thận trọng.
- Chương 4 công khai kết quả không đạt, giữ các lượt thất bại trong thống kê, phân biệt trạng thái thật của mô hình với Odometry. Đây là cách báo cáo khoa học phù hợp.
- Có hồ sơ dữ liệu gồm cấu hình, tham số từng lượt, nhật ký và chỉ tiêu tổng hợp. Các giá trị trong bảng Chương 4 khớp với [summary.json](../output/simulation_ch4/summary.json); mã mô phỏng tại thời điểm rà soát cũng khớp mã băm lưu trong cấu hình.

## 3. Các vấn đề cần giải trình và bổ sung

### 3.1. [Nghiêm trọng] Phương pháp Bézier trong báo cáo chưa thống nhất với phương pháp tạo ra kết quả

**Vị trí:** main.tex, dòng 1004 và phần mô tả chuỗi xử lý Chương 4; [simulate_ch4.py](../code/simulation_ch4/simulate_ch4.py), dòng 146–166.

Báo cáo viết rằng **Bézier bậc 5 được chọn để xây dựng đoạn chuyển tiếp**, gắn với khả năng đặt đạo hàm bậc nhất và bậc hai tại hai đầu. Chương 4 tiếp tục dẫn việc làm mượt theo mục 2.4.

Nhưng mã tạo dữ liệu dùng **Bézier bậc 2**, với biểu thức:

    B(u) = (1-u)^2 P + 2(1-u)u B + u^2 Q.

Đây là khác biệt về phương pháp. Việc bo góc bằng đoạn bậc 2 có tiếp tuyến phù hợp **chưa đủ chứng minh liên tục độ cong tại chỗ nối với đoạn thẳng**.

**Câu hỏi phản biện:** Kết quả Chương 4 kiểm chứng phương pháp Bézier bậc 5 được chọn ở Chương 2, hay một phương án làm mượt khác?

**Yêu cầu bổ sung:** Thống nhất mô tả với cài đặt thực tế và công bố mức liên tục thực sự đạt được. Hiện chưa nên dùng kết quả Chương 4 làm bằng chứng rằng thiết kế bậc 5 hoặc yêu cầu G²/C² đã được kiểm chứng.

### 3.2. [Nghiêm trọng] Phần so sánh đa thuật toán vẫn là thiết kế thí nghiệm, chưa phải kết quả nghiên cứu

**Vị trí:** main.tex, dòng 1482–1527; mục tiêu cụ thể tại dòng 518.

Tác giả xác nhận các chỉ số chỉ được điền sau khi chạy mô phỏng. Bảng tiếp theo cũng được xác định là đối chiếu đặc tính dự kiến.

Như vậy, phần mang tên “đánh giá so sánh đa thuật toán” hiện chưa trả lời bằng dữ liệu:

- Mỗi thuật toán tìm được đường dài bao nhiêu?
- Mất bao nhiêu thời gian tính toán?
- Thành công bao nhiêu lượt?
- Sau cùng một quy trình làm mượt, độ trơn và khoảng hở khác nhau thế nào?

Trong khi đó, mục tiêu cụ thể đã đặt ra so sánh định lượng.

**Nhận định:** Bảng tổng hợp lý thuyết có giá trị khảo sát tài liệu, nhưng chưa hoàn thành mục tiêu thực nghiệm so sánh. Đây là điểm có khả năng bị chất vấn mạnh tại nghiệm thu.

**Yêu cầu bổ sung:** Hoàn thành phép so sánh trên các bản đồ chung, công bố cấu hình, ngân sách tính toán, số lượt, hạt giống ngẫu nhiên và kết quả đo. Phân biệt rõ bảng đặc tính lý thuyết với bảng kết quả mô phỏng.

### 3.3. [Nghiêm trọng] Kết quả hiện tại chưa chứng minh hệ thống đạt yêu cầu vận hành

**Vị trí:** main.tex, dòng 1879–1915.

| Chỉ tiêu | Đường thẳng | Có vật cản |
| --- | ---: | ---: |
| Thành công | 5/30 | 5/30 |
| Tỷ lệ thành công | 16,7% | 16,7% |
| Sai số vị trí cuối trung bình | 0,293 m | 0,404 m |
| Sai số ngang lớn nhất | 0,897 m | 0,677 m |
| Số lượt va chạm | 0 | 3 |

Đối chiếu dung sai đích 0,05 m và sai số ngang cho phép 0,15 m, cấu hình này **chưa đạt độ chính xác và độ tin cậy mong muốn**.

Kết quả thấp không phải lý do tự động bác bỏ nghiên cứu. Kết quả không đạt vẫn có giá trị nếu tác giả chứng minh được nguyên nhân và rút ra kết luận có căn cứ.

Điểm còn thiếu là **phép thử phân tách nguyên nhân**. Hiện bán kính bánh, khoảng cách bánh, trượt, đáp ứng động cơ và tư thế đầu cùng biến thiên. Nhận định Odometry là yếu tố cần ưu tiên có cơ sở quan sát, nhưng chưa lượng hóa được đóng góp của từng yếu tố.

**Yêu cầu bổ sung:** Có đối chứng lần lượt cho cấu hình lý tưởng, chỉ sai lệch hình học, chỉ trượt, kết hợp sai lệch và cấu hình sau hiệu chuẩn. Mục đích là làm rõ vì sao hệ thống thất bại và biện pháp nào cải thiện được kết quả.

### 3.4. [Cao] Chưa thống nhất phần nào chạy trên ESP32 và phần nào chạy trên máy tính

**Vị trí:** main.tex, dòng 1532 và dòng 1623.

Báo cáo chọn Dijkstra “để triển khai trên board ESP32-C3-MINI”. Nhưng phần kiến trúc lại mô tả tìm đường và làm mượt có thể chạy trên máy tính; chạy toàn bộ bộ quy hoạch trên vi điều khiển cần đánh giá riêng.

Hai cách tổ chức đều có thể phù hợp, nhưng báo cáo nghiệm thu phải xác định rõ:

- Kiến trúc nào đã được triển khai?
- Kiến trúc nào mới đề xuất?
- Có kết quả đo thời gian và RAM trên board hay chưa?

Hiện lập luận chọn Dijkstra chủ yếu dựa trên tính đơn giản và khả năng kiểm chứng. Điều đó phù hợp để chọn cấu hình cơ sở, **chưa chứng minh ưu thế tài nguyên trên ESP32 so với A***.

**Nhận định:** Chưa có căn cứ từ báo cáo để công nhận phần quy hoạch trên board đã được nghiệm thu thành công.

**Yêu cầu bổ sung:** Chốt sơ đồ phân chia tác vụ đã thực hiện, cung cấp mã tương ứng và số đo tài nguyên nếu tuyên bố đã triển khai bộ quy hoạch trên ESP32.

### 3.5. [Cao] Mục nội suy đa thức chưa có nội dung đúng với tiêu đề

**Vị trí:** main.tex, dòng 794–849.

Mục 2.3.1 mang tên nội suy đa thức bậc 3 và bậc 5, nhưng nội dung thực tế trình bày phương trình động lực học và phép chuyển sang không gian trạng thái.

Thiếu những thành phần trực tiếp của phương pháp:

- Biểu thức đa thức bậc 3 và bậc 5.
- Các điều kiện biên.
- Cách xác định hệ số.
- Nhận xét vận tốc, gia tốc và giới hạn áp dụng.

Đồng thời, phương trình M(q)q̈ + C(q,q̇)q̇ + G(q) = τ được đặt dưới tên “mô hình động lực học của xe”, nhưng chưa giải thích tọa độ, cấu trúc tác động của hai động cơ và ràng buộc phi holonomic.

**Nhận định:** Đoạn này chưa nối được kiến thức điều khiển với bài toán đang giải. Hội đồng có thể yêu cầu tác giả tự dẫn xuất để kiểm tra mức độ hiểu.

**Yêu cầu bổ sung:** Trình bày đúng nội dung nội suy theo tiêu đề, đồng thời làm rõ vai trò và điều kiện áp dụng của mô hình động lực học nếu tiếp tục giữ lại.

### 3.6. [Cao] Mô hình sinh dữ liệu chưa được trình bày đủ trong chính báo cáo

**Vị trí:** main.tex, dòng 1877; [config.json](../output/simulation_ch4/config.json) và [README mô phỏng](../output/simulation_ch4/README.md).

Báo cáo nêu một số tham số chính và nói cấu hình đầy đủ được lưu cùng nhật ký. Hồ sơ ngoài có thêm nhiều thông tin quan trọng:

- Thân xe được giả định là đĩa bán kính 0,11 m.
- Truyền động dùng mô hình bậc nhất với hệ số và hằng số thời gian giả định.
- PI có Kp = 2, Ki = 8, duty giới hạn ±0,8.
- Pure Pursuit chạy 20 Hz; vòng PI chạy 100 Hz.
- Có quy luật phân bố và biên độ nhiễu cụ thể.

Những thông tin này quyết định trực tiếp kết quả, nhưng người chỉ đọc báo cáo chưa nắm được đầy đủ.

**Yêu cầu bổ sung:** Đưa mô hình sinh chuyển động và bảng tham số thiết yếu vào nội dung hoặc phụ lục có dẫn chiếu. Phân biệt tham số giả định với tham số đã nhận dạng hoặc đo trên xe.

**Lưu ý đánh giá:** Mô hình tính toán chạy nhất quán chưa đồng nghĩa mô hình đã đại diện đúng cho xe thật. Hồ sơ mô phỏng đã thừa nhận điều này khá rõ; báo cáo nên thể hiện tương ứng.

### 3.7. [Trung bình–cao] Quy luật tốc độ thực thi cần được phân biệt rõ với profile tham chiếu danh định

**Vị trí:** main.tex, dòng 1875 và dòng 1925–1929; simulate_ch4.py, dòng 291–299.

Chương 4 mô tả hai kịch bản dùng profile hình thang. Trong mã, tốc độ điều khiển được tính từ thời gian tăng tốc, khoảng đường còn lại ước lượng và các giới hạn lệnh; nó có thể thay đổi theo tiến triển thực tế.

Trong khi đó, RMSE theo thời gian lại đối chiếu với lịch tham chiếu danh định.

Báo cáo đã lưu ý Pure Pursuit chủ yếu bám hình học, đây là điểm đúng. Nhưng cần giải thích cụ thể hơn rằng **RMSE hiện chứa cả sai lệch hình học và sai lệch tiến độ so với lịch danh định**. Không nên dùng riêng chỉ tiêu này để kết luận chất lượng bám đường.

**Yêu cầu bổ sung:** Phân biệt lịch tham chiếu, quy luật phát lệnh và chuyển động thực tế. Có kết quả kiểm tra gia tốc lệnh và gia tốc bánh thực tế; việc đặt tham số gia tốc 0,20 m/s² chưa tự chứng minh toàn bộ lệnh sau các bước giới hạn đều tuân thủ mức đó.

### 3.8. [Trung bình–cao] Tổng quan nghiên cứu và trích dẫn chưa đủ sức thuyết phục

**Vị trí:** main.tex, dòng 91–156 và các phần trình bày phương pháp; [REFERENCES.md](REFERENCES.md).

Phần tổng quan có nhận định rộng như nghiên cứu trong nước “mới dừng lại ở mức mô phỏng”, nhưng chưa dẫn công trình cụ thể để bảo vệ nhận định.

Trong nội dung còn thiếu trích dẫn trực tiếp cho các phần Bézier/B-Spline, Pure Pursuit, Odometry và phương án xử lý GNRON. Một số nguồn đã được ghi trong REFERENCES.md, nhưng chưa được đưa vào hệ thống trích dẫn của báo cáo.

Vấn đề chính không phải số lượng tài liệu ít, mà là **người đọc chưa truy được cơ sở của một số phương pháp và kết luận quan trọng**.

**Yêu cầu bổ sung:** Khảo sát một số công trình cụ thể, chỉ rõ họ làm gì, giới hạn gì và đề tài này đóng góp ở đâu. Với đề tài sinh viên, đóng góp có thể là triển khai, tích hợp và đánh giá có hệ thống; không bắt buộc phải có thuật toán mới, nhưng phải nhận diện rõ phần việc của nhóm.

### 3.9. [Trung bình] Thiếu phần kết luận tổng thể và đối chiếu mức hoàn thành mục tiêu

**Vị trí:** Phần cuối main.tex, sau hướng phát triển và trước tài liệu tham khảo; đối chiếu mục tiêu tại dòng 502–522.

Báo cáo chưa có phần kết luận trả lời trực tiếp:

- Mục tiêu nào đã hoàn thành?
- Mục tiêu nào mới hoàn thành một phần?
- Sản phẩm nào bàn giao được?
- Kết quả nào chỉ đúng trong mô hình giả định?
- Phần nào chưa kiểm chứng trên xe?

Phạm vi còn nhắc đến tình huống động và các môi trường phức tạp, trong khi kết quả định lượng được trình bày mới gồm hai kịch bản tĩnh đơn giản.

**Yêu cầu bổ sung:** Có bảng “mục tiêu – sản phẩm – minh chứng – mức hoàn thành”. Đây là nội dung giúp hội đồng quyết định nghiệm thu và cần thiết hơn việc mở rộng thêm các hướng SLAM, micro-ROS hay MPC.

## 4. Các câu hỏi dự kiến tại buổi bảo vệ

1. Đóng góp riêng của nhóm là gì ngoài hệ thống hóa các thuật toán đã có?
2. Vì sao lý thuyết chọn Bézier bậc 5 nhưng dữ liệu được tạo bằng bậc 2?
3. Kết quả đo nào hỗ trợ lựa chọn Dijkstra thay cho A*?
4. Hệ thống chỉ đạt 16,7%: nguyên nhân nào đã được chứng minh bằng đối chứng?
5. Phần nào đã chạy trên ESP32 và có minh chứng gì?
6. Tham số mô hình nào đã đo trên xe, tham số nào đang giả định?

## 5. Thứ tự ưu tiên hoàn thiện trước nghiệm thu

1. **Thống nhất phương pháp với mã sinh kết quả:** Làm rõ bậc Bézier, mức liên tục đạt được và quy luật tốc độ thực thi.
2. **Hoàn thành so sánh định lượng đã đặt ra:** Phân biệt khảo sát lý thuyết với kết quả đo các thuật toán.
3. **Bổ sung đối chứng giải thích thất bại:** Phân tách ảnh hưởng của sai lệch hình học, trượt và các yếu tố khác; đánh giá cấu hình sau hiệu chỉnh nếu có.
4. **Chốt phạm vi triển khai thực tế:** Xác định tác vụ trên máy tính và ESP32, kết quả đã kiểm chứng và phần còn đề xuất.
5. **Hoàn chỉnh báo cáo:** Sửa nội dung mục nội suy đa thức, bổ sung mô hình và tham số, trích dẫn và kết luận đối chiếu mục tiêu.

## 6. Ý kiến nghiệm thu tham khảo

Ghi nhận công sức xây dựng lý thuyết và tính minh bạch của hồ sơ mô phỏng. Tuy nhiên, bản hiện tại chưa đủ cơ sở để xác nhận hoàn thành đầy đủ các mục tiêu đã nêu, đặc biệt là so sánh đa thuật toán, kiểm chứng phương pháp làm mượt được chọn và triển khai quy hoạch trên board.

Đề nghị bổ sung trước khi xác nhận hoàn thành đầy đủ. Không yêu cầu thay kết quả thấp bằng số liệu đẹp; yêu cầu trọng tâm là mô tả đúng phần đã làm, bảo đảm khả năng truy xuất bằng chứng và giải thích kết quả bằng các phép đối chứng phù hợp.

---

**Ghi chú:** Số dòng được ghi theo phiên bản main.tex tại thời điểm rà soát và có thể thay đổi khi báo cáo được chỉnh sửa. Trong đợt review, các tệp nguồn và dữ liệu chỉ được đọc; tệp README này được tạo riêng theo yêu cầu lưu nhận xét của người dùng.
