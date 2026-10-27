# A* trên bản đồ lưới

Chạy từ `C:\Users\ADMIN\Documents\NCKH`:

```powershell
python code/A_Star/A_Star_algorithm.py
```

Cần Python 3.10 trở lên, Matplotlib và Pillow. Nếu chưa có thư viện, chạy `python -m pip install matplotlib Pillow`.

Chương trình xuất vào `code/A_Star/output/`, không mở cửa sổ đồ họa:

- `a_star_cac_buoc_mo_rong.png`: sáu trạng thái của A*, có nhãn chi phí và đường đi cuối cùng.
- `a_star_cac_buoc_mo_rong.pdf`: hình vector để chèn vào báo cáo.
- `a_star_duong_di.png`: ảnh lớn của đường đi và các nhãn cuối.
- `a_star_qua_trinh.gif`: toàn bộ quá trình mở rộng đỉnh.
- `so_sanh_dijkstra_a_star.png`: hai thuật toán trên cùng bản đồ.
- `nhat_ky_mo_rong.csv`: đỉnh mở rộng theo từng bước, g/h/f và số đỉnh Open.
- `ket_qua.json`: bản đồ, điểm đầu/đích, đường đi, chi phí, số đỉnh mở rộng và kết quả Dijkstra đối chiếu.

## Ví dụ và ý nghĩa các nhãn

Bản đồ 9 × 13 giống ví dụ Dijkstra trong `code/Dijkstra/`: S=(7,1), G=(1,11). Tọa độ theo **(hàng, cột)** từ 0, hàng tăng từ trên xuống. Ô 0 tự do, ô 1 là vật cản. Chỉ đi bốn hướng, mỗi bước tốn 1; không đi chéo.

- `g`: chi phí tốt nhất đã tìm từ S tới ô hiện tại.
- `h`: khoảng cách Manhattan tới G, không tính vật cản.
- `f = g + h`: độ ưu tiên để chọn đỉnh tiếp theo.
- Xanh nhạt: đã mở rộng; vàng: đang chờ trong Open; xám nhạt/∞: chưa được tìm tới; xám đậm: vật cản.
- Viền cam: đỉnh vừa mở rộng. Đường xanh lá: đường ngắn nhất truy vết được.

Open dùng nhãn tạm thời. Với Manhattan trên lưới bốn hướng đơn vị, heuristic nhất quán và các đỉnh Closed không cần mở lại. Chỉ dừng khi đích được lấy khỏi hàng đợi ưu tiên, không dừng ngay khi vừa phát hiện đích. Một số ô có thể chưa được mở rộng khi thuật toán kết thúc.

Phá hòa của A*: ưu tiên f nhỏ, sau đó h nhỏ, sau đó thứ tự đưa vào hàng đợi. Thứ tự xét láng giềng: trên, phải, dưới, trái. Dijkstra đối chiếu dùng h=0 và cùng thứ tự láng giềng; số đỉnh mở rộng phụ thuộc cả heuristic và quy tắc phá hòa, không phải chỉ riêng tên thuật toán. Đường đi tối ưu có thể có nhiều nghiệm.

Hàm `a_star()` dùng thư viện chuẩn, tách khỏi phần vẽ. Thay bản đồ và S/G trong `example_map()` để tạo ví dụ mới. Chương trình độc lập với thư mục Dijkstra, không cần nhập module từ thư mục bên cạnh. Nếu thay mô hình chuyển động, trọng số hoặc heuristic thì phải xét lại điều kiện tối ưu và cơ chế mở lại đỉnh.

## Tùy chọn và kiểm tra

```powershell
python code/A_Star/A_Star_algorithm.py --all-steps
python code/A_Star/A_Star_algorithm.py --no-gif --dpi 300
python code/A_Star/A_Star_algorithm.py --output-dir code/A_Star/output_khac
python -m unittest discover -s code/A_Star -p test_A_Star_algorithm.py -v
```

`--all-steps` xuất thêm PNG từng bước vào `output/tung_buoc/`. Kiểm tra dùng BFS độc lập trên bản đồ cố định và 80 bản đồ ngẫu nhiên, đồng thời kiểm tra đầu trùng đích, không có đường và đầu vào không hợp lệ. Bản đồ mô tả chuyển động của điểm; áp dụng cho robot có kích thước cần mở rộng vật cản, kiểm tra động học và tạo quy luật thời gian.
