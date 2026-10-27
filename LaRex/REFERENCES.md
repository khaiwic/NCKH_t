# Nguồn tham khảo của dự án

## Chỉnh sửa cách trình bày profile chữ S, mục 2.3.3

Các phần 2–4 được chuyển sang văn xuôi theo yêu cầu: bỏ bảng khai triển bảy pha và các công thức tích phân/tổng hợp tham số, giữ một công thức tổng thời gian. Giữ nguyên các đề mục, giải thích bằng lời cách nối điều kiện biên, xác định thời lượng và các dạng rút gọn khi hành trình ngắn. Đối chiếu cấu trúc profile với [Modern Robotics, mục 9.1–9.2, phần 2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/9-1-and-9-2-point-to-point-trajectories-part-2-of-2/), dùng mã `lynch-park-modern-robotics` có sẵn.

Phần đánh giá phân biệt tính liên tục C² với jerk liên tục, lợi ích giảm kích thích với bảo đảm triệt rung/chống trượt, và khả năng triển khai với thời gian tính đã đo. Bỏ khẳng định thời gian dưới 10 µs do không có phép đo tương ứng. Bản trước sửa được lưu tại `.tools/scurve-prose-check/main-before.tex` và `main-before.pdf`.

Người dùng đã chọn tài liệu dưới đây làm nguồn tham khảo cho các phần tiếp theo của dự án. Khi sử dụng nội dung, kiểm tra trực tiếp tài liệu và ghi rõ trang hoặc chương liên quan.

## Nguồn và nội dung bổ sung từ mục 1.2.2 đến hết Chương I

Giữ nguyên toàn bộ tiêu đề, bổ sung phần giải thích, công thức, ví dụ và mối liên hệ giữa các mục. Nội dung trước 1.2.2 và Chương II–IV không sửa. Bổ sung hai tài liệu trong danh mục tham khảo chung. Bản trước chỉnh sửa được lưu tại `.tools/chapter1-expansion-check/main-before.tex` và `main-before.pdf`.

| Mã trích dẫn | Nguồn đối chiếu | Nội dung sử dụng |
| --- | --- | --- |
| `lavalle-planning-2006` | Steven M. LaValle, *Planning Algorithms*: [Chương 4](https://lavalle.pl/planning/ch4.pdf), [mục 4.3.2](https://lavalle.pl/planning/node161.html), [Chương 7](https://lavalle.pl/planning/ch7.pdf), [Chương 13](https://lavalle.pl/planning/ch13.pdf), [Chương 14](https://lavalle.pl/planning/ch14.pdf). | Cấu hình, vùng cấm, tổng Minkowski; quy hoạch có thời gian và ràng buộc vi phân. |
| `lynch-park-modern-robotics` | Tài liệu của tác giả: [2.5: Workspace](https://modernrobotics.northwestern.edu/nu-gm-book-resource/2-5-task-space-and-workspace/), [5.3: Singularities](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-3-singularities/), [9.1–9.2: Trajectories](https://modernrobotics.northwestern.edu/nu-gm-book-resource/9-1-and-9-2-point-to-point-trajectories-part-1-of-2/), [9.4: Time-optimal scaling](https://modernrobotics.northwestern.edu/nu-gm-book-resource/9-4-time-optimal-time-scaling-part-1-of-3/), [13.3.1: Wheeled robots](https://modernrobotics.northwestern.edu/nu-gm-book-resource/13-3-1-modeling-of-nonholonomic-wheeled-mobile-robots/). | Quy ước workspace, hạng Jacobian, điều kiện đầu cuối, quy luật thời gian và xe phi holonomic. |
| `bry-flatness-flight` | A. Bry, C. Richter, A. Bachrach, N. Roy, *Aggressive Flight of Fixed-Wing and Quadrotor Aircraft in Dense Indoor Environments*, [bản thảo tại MIT](https://groups.csail.mit.edu/rrg/papers/BryIJRR15.pdf). | Tính phẳng vi phân và quy hoạch đa thức cho robot bay. |
| `caron-contact-stability-2015` | S. Caron, Q.-C. Pham, Y. Nakamura, *Stability of Surface Contacts for Humanoid Robots: Closed-Form Formulae of the Contact Wrench Cone for Rectangular Support Areas*, 2015, [arXiv:1501.04719](https://arxiv.org/abs/1501.04719). | Điều kiện tiếp xúc, ma sát và ZMP; phân biệt cân bằng tĩnh với động. |

Ví dụ hai hướng 179°/−179°, đĩa bao robot 0,15 m và khoảng dự phòng 0,05 m, công thức khoảng dừng, phép đổi biến cho tích phân jerk và hàm mục tiêu chuẩn hóa là các minh họa/phân tích toán học tự xây dựng. Chúng không phải số đo của robot. Phần năng lượng chỉ nêu cách đặt bài toán và giới hạn của chỉ tiêu thay thế, chưa kết luận hiệu suất thực nghiệm.

Ba khung hình chờ được chèn bằng `\hinhminhhoa`: workspace/C-space, tổng Minkowski và so sánh các quy luật chuyển động. Không tạo hoặc chèn hình ảnh mới. Phạm vi Chương I được thống nhất với Chương IV: có phương án Odometry, bám đường và PID tốc độ phục vụ kiểm chứng; chưa coi phần cứng là hệ thống đã có kết quả thực nghiệm.

## Giáo trình Kỹ thuật robot — Nguyễn Trường Thịnh

- Tác giả: Nguyễn Trường Thịnh.
- Tên tài liệu: *Giáo trình Kỹ thuật robot*.
- Nhà xuất bản: Đại học Quốc gia TP. Hồ Chí Minh.
- PDF gốc: [Mở tài liệu](../608976674-GIAO-TRINH-KỸ-THUẬT-ROBOT-NGUYỄN-TRƯỜNG-THỊNH-ebookbkmt-unlocked.pdf).
- Mã trích dẫn trong `main.tex`: `nguyen-truong-thinh-ky-thuat-robot`. Dùng `\cite{nguyen-truong-thinh-ky-thuat-robot}` khi trích dẫn trong nội dung.
- Thông tin tác giả, tên và nhà xuất bản đã đối chiếu với bìa sách (trang PDF 1). Chưa xác minh năm xuất bản, nên chưa ghi năm vào danh mục.
- Mục lục ở trang PDF 2 có Chương 8: “Tạo quỹ đạo chuyển động robot”, phù hợp để tra cứu cho đề tài quy hoạch quỹ đạo.
- PDF là bản quét, có nhiều trang ghép đôi; số trang PDF có thể khác số trang in trong sách.

## Các nguồn bổ sung cho mục 3.1–3.3

Các mục này được soạn theo nguyên lý thuật toán và đối chiếu với các nguồn gốc dưới đây. Giáo trình Nguyễn Trường Thịnh vẫn được giữ trong danh mục; không gán các trình bày về PRM, RRT* hoặc GNRON cho giáo trình khi chưa kiểm tra nội dung tương ứng.

| Mã trích dẫn trong LaTeX | Nguồn | Nội dung dùng đối chiếu |
| --- | --- | --- |
| `lavalle-planning-2006` | Steven M. LaValle, *Planning Algorithms*, Cambridge University Press, 2006. [Bản của tác giả](https://lavalle.pl/planning/). | Dijkstra, A*, tìm kiếm trên đồ thị, không gian cấu hình và lấy mẫu. [Dijkstra](https://lavalle.pl/planning/node44.html), [A*](https://lavalle.pl/planning/node45.html). |
| `kavraki-prm-1996` | L. E. Kavraki, P. Švestka, J.-C. Latombe, M. H. Overmars, “Probabilistic Roadmaps for Path Planning in High-Dimensional Configuration Spaces”, 1996. [Kavraki Lab](https://www.kavrakilab.rice.edu/publications/kavraki-svestka1996probabilistic-roadmaps-for.html). | Hai giai đoạn xây dựng roadmap và truy vấn, kiểm tra đường nối cục bộ. |
| `lavalle-rrt-1998` | S. M. LaValle, *Rapidly-Exploring Random Trees: A New Tool for Path Planning*, 1998. [Báo cáo gốc](https://lavalle.pl/papers/Lav98c.pdf). | Nguyên lý phát triển cây RRT và mở rộng về phía mẫu. |
| `karaman-frazzoli-2011` | S. Karaman, E. Frazzoli, “Sampling-based Algorithms for Optimal Motion Planning”, 2011. [arXiv:1105.1186](https://arxiv.org/abs/1105.1186). | RRT*, chọn cha, nối lại nhánh, bán kính kết nối, tính đầy đủ xác suất và tối ưu tiệm cận. |
| `khatib-apf-1986` | O. Khatib, “Real-Time Obstacle Avoidance for Manipulators and Mobile Robots”, 1986. [PDF tại Stanford](https://khatib.stanford.edu/publications/pdfs/Khatib_1986_IJRR.pdf). | Nguyên lý trường thế nhân tạo và tránh vật cản cục bộ. |
| `ge-cui-2000` | S. S. Ge, Y. J. Cui, “New Potential Functions for Mobile Robot Path Planning”, 2000. [PDF tại trang tác giả ở NUS](https://bpb-us-w2.wpmucdn.com/blog.nus.edu.sg/dist/f/14858/files/2021/07/TRA-potential-00.pdf). | GNRON và thế đẩy phụ thuộc khoảng cách đích. |

Các ví dụ số về heuristic và các biểu thức đạo hàm được tính trực tiếp trong bản soạn. Quy tắc lực ảo tiếp tuyến được ghi rõ là phương án đề xuất cho mô phỏng của đề tài, cần kiểm chứng; không gán cho một thuật toán đã có bảo đảm lý thuyết hoặc kết quả thực nghiệm.

Trong mục 3.1–3.3, có 7 khung minh họa tạm thời: Dijkstra, so sánh Dijkstra/A*, PRM, RRT/RRT*, trường thế APF, cực tiểu cục bộ/GNRON, và lực ảo tiếp tuyến. Các khung dùng cùng kiểu hộp với ví dụ profile chữ S của người dùng.

## Các nguồn bổ sung cho mục 2.4 — Làm mượt đường đi

| Mã trích dẫn trong LaTeX | Nguồn đã đối chiếu | Nội dung sử dụng |
| --- | --- | --- |
| `shene-bezier-notes` | Ching-Kuang Shene, *CS3621 Introduction to Computing with Geometry*, Michigan Technological University: [Construction of Bézier Curves](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/Bezier/bezier-construct.html), [Derivatives of a Bézier Curve](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/Bezier/bezier-der.html). | Đa thức Bernstein, bao lồi, đạo hàm và điều kiện tiếp tuyến đầu cuối. Các công thức điểm điều khiển Bézier bậc 5 được suy ra trực tiếp từ đạo hàm biên. |
| `shene-bspline-notes` | Cùng bộ ghi chú: [định nghĩa đường B-Spline](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/bspline-curve.html), [hàm cơ sở](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/bspline-basis.html), [tính liên tục](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/bspline-property.html), [tính chất đường cong](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/bspline-curve-prop.html), [đạo hàm](https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-derv.html). | Cox–de Boor, vector nút, nút kẹp, tính cục bộ, bao lồi, đạo hàm và ảnh hưởng của bội nút đến tính liên tục. |
| `patrikalakis-geometric-continuity` | N. M. Patrikalakis, T. Maekawa, W. Cho, *Shape Interrogation for Computer Aided Design and Manufacturing (Hyperbook Edition)*, MIT, [mục 1.3.5](https://web.mit.edu/hyperbook/Patrikalakis-Maekawa-Cho/node13.html). | de Casteljau, ghép đường, phân biệt G² và C², ảnh hưởng của tỷ lệ tham số khi nối đoạn. |
| `lynch-park-modern-robotics` | K. M. Lynch, F. C. Park, *Modern Robotics: Mechanics, Planning, and Control*, tài liệu của tác giả: [mục 9.1–9.2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/9-1-and-9-2-point-to-point-trajectories-part-1-of-2/), [mục 13.3.1](https://modernrobotics.northwestern.edu/nu-gm-book-resource/13-3-1-modeling-of-nonholonomic-wheeled-mobile-robots/). | Tách hình học và quy luật thời gian; mô hình phi holonomic và giới hạn điều khiển của robot vi sai. |

Mục 2.4 đã được rút gọn theo yêu cầu thành đúng 5 trang, giữ nguyên toàn bộ tiêu đề chính và các đề mục a–d. Bản hiện tại giữ năm cụm công thức cốt lõi về Bézier, đạo hàm biên, Cox–de Boor, độ cong và động học tiếp tuyến; lược bỏ ví dụ số cùng các phép khai triển dài. Ràng buộc tốc độ/gia tốc bánh xe và quy trình gán thời gian được giải thích bằng lời từ mô hình ở mục 2.1. Hai hình đã chèn được giữ nguyên, cùng một khung hình chờ về tính liên tục hình học.

Ở cấu hình trình bày hiện tại, mục 2.4 chiếm trang in 37–41 (trang PDF 42–46), đã xuất riêng thành `Muc_2_4_rut_gon.pdf`. Giữ nguyên cỡ chữ và giãn dòng chung; phân trang theo nhóm nội dung. Bản trước sửa nằm tại `.tools/section24-five-pages/main-before.tex` và `main-before.pdf`. Quy trình làm mượt vẫn là phương án đề xuất cần kiểm chứng, không phải kết quả mô phỏng hoặc thực nghiệm đã có.

## Nguồn và trạng thái dữ liệu của Chương 4

Thông tin phần cứng do người dùng cung cấp trong hội thoại ngày 15/10/2026: ESP32-C3-MINI, TB6612, động cơ DC giảm tốc kim loại GA12-N20 (tên thương mại GA12 N20 Servo), tỷ số truyền 50:1, điện áp hoạt động được cung cấp 3–12 VDC, tốc độ trước hộp số 15.000 RPM, đầu ra không tải 300 RPM tại 6 VDC, tốc độ tải định mức được cung cấp 250 RPM; các dòng điện không tải/tải định mức/kẹt trục 50/95/400 mA, mô-men định mức/kẹt trục 0,35/1,30 kgf·cm, trục D đường kính 3 mm dài 10 mm, hộp số 12 × 10 mm, khối lượng khoảng 10 g. Encoder Hall hai kênh, nguồn 3,3–5 VDC, 7 chu kỳ mỗi kênh trước hộp số. Bánh cao su đường kính 44 mm, rộng 18 mm, lỗ trục D 3 mm. Các thông số này chưa được đối chiếu với datasheet của một nhà sản xuất động cơ cụ thể hoặc đo trên robot; không coi tất cả thông số tải là cùng một điểm làm việc đã xác nhận.

Khoảng cách hai bánh, kích thước khung, khối lượng robot/tải, nguồn thực tế, GPIO của đúng bo mạch, chế độ đếm encoder đã triển khai, chu kỳ điều khiển, hệ số PID và dữ liệu chạy thử chưa được cung cấp. Chương 4 mô tả phương án triển khai và biểu mẫu thực nghiệm; không ghi kết quả đo giả định.

| Mã trích dẫn | Nguồn chính thức | Nội dung sử dụng |
| --- | --- | --- |
| `lynch-park-modern-robotics` | [Mục 13.4: Odometry](https://modernrobotics.northwestern.edu/nu-gm-book-resource/13-4-odometry/). | Tích phân chuyển động bánh xe để ước lượng tư thế và sai số tích lũy. Công thức sinc được suy ra từ mô hình cung tròn với vận tốc xoắn không đổi trong chu kỳ. |
| `coulter-pure-pursuit-1992` | R. Craig Coulter, *Implementation of the Pure Pursuit Path Tracking Algorithm*, CMU-RI-TR-92-01, 1992, [PDF gốc](https://publications.ri.cmu.edu/storage/publications/pub_files/pub3/coulter_r_craig_1992_1/coulter_r_craig_1992_1.pdf), mục 2–4, trang in 4–9 (trang PDF 10–15). | Hình học điểm nhìn trước và độ cong Pure Pursuit. Bản soạn dùng trục thân xe x hướng trước, y hướng trái, khác ký hiệu trục trong hình của báo cáo; công thức được dẫn xuất theo quy ước của đề tài. |
| `espressif-c3-peripherals` | Espressif, ESP-IDF cho ESP32-C3: [LEDC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/ledc.html), [GPIO](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/gpio.html). | Phương án phát hai PWM bằng LEDC và đọc encoder qua ngắt GPIO. Chưa gán chân khi chưa có sơ đồ đúng phiên bản bo MINI. |
| `toshiba-tb6612fng` | Toshiba, [TB6612FNG datasheet](https://toshiba.semicon-storage.com/info/TB6612FNG_datasheet_en_20141001.pdf?did=10660&prodName=TB6612FNG), tr. 3–5. | Dải nguồn logic/động cơ, tín hiệu điều khiển, STBY và phân biệt phanh với đầu ra trở kháng cao. Áp dụng khi module TB6612 dùng IC TB6612FNG. |
| `ros-control-pid` | ros-controls, [control_toolbox](https://control.ros.org/jazzy/doc/control_toolbox/doc/index.html). | Cấu trúc PID và chống bão hòa tích phân bằng back-calculation. Cấu hình bù thuận, lọc vi phân trên tín hiệu đo và quy trình chỉnh định là phương án đề xuất. |
| `ros-diff-drive-controller` | ros-controls, [diff_drive_controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html). | Giao diện vận tốc thân xe, lệnh bánh và phản hồi Odometry trong hướng mở rộng ROS 2. Chưa tuyên bố đã tích hợp ROS 2 trên robot. |
| `ros-rep-105` | Wim Meeussen, [REP-105](https://github.com/ros-infrastructure/rep/blob/master/rep-0105.rst), bản nguồn trong kho ROS. | Vai trò và quan hệ các hệ map, odom, base_link. |

Các giá trị 350/700/1400 đếm mỗi vòng bánh lần lượt được suy ra cho x1/x2/x4 từ giả thiết 7 chu kỳ đầy đủ trên một vòng trước hộp số. Cần xác nhận bằng một vòng bánh đánh dấu. Bước quãng đường 0,395/0,0987 mm, tốc độ quy đổi 0,576/0,691 m/s và tải ngắt danh định 14.000 sự kiện/s là tính toán từ thông số cung cấp, không phải phép đo độ chính xác hoặc tốc độ vận hành thực.

Đường chữ S hình học bậc 5, cách tổ chức thí nghiệm, bảng chỉ tiêu, phép tính sai số và khoảng phát hiện sơ bộ được xây dựng cho đề tài. Chương 4 có năm khung hình chờ: cơ khí, kết nối điện, kiến trúc điều khiển, bố trí thử và đồ thị kết quả. Các kết luận định lượng phải chờ nhật ký và phép đo vị trí đối chứng; Odometry không được dùng làm chuẩn độc lập cho chính nó.
