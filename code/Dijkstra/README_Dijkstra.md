# Minh họa thuật toán Dijkstra

Chạy từ thư mục dự án:

```powershell
python code/Dijkstra_algorithm.py
```

Cần Python 3.10 trở lên, Matplotlib và Pillow. Nếu máy chưa có thư viện:

```powershell
python -m pip install matplotlib Pillow
```

Chương trình không mở cửa sổ đồ họa. Kết quả nằm tại `code/output/dijkstra/`:

- `dijkstra_cac_buoc_mo_rong.png`: sáu trạng thái đại diện, gồm nhãn chi phí và đường đi cuối cùng.
- `dijkstra_cac_buoc_mo_rong.pdf`: cùng hình, ở định dạng vector để chèn vào báo cáo.
- `dijkstra_duong_di.png`: bản đồ kết quả ở kích thước lớn.
- `dijkstra_qua_trinh.gif`: toàn bộ quá trình mở rộng đỉnh.
- `nhat_ky_mo_rong.csv`: thứ tự đỉnh được chốt, chi phí và số đỉnh còn chờ.
- `ket_qua.json`: bản đồ, điểm đầu/đích, đường đi, tổng chi phí và số đỉnh đã mở rộng.

Ví dụ dùng lưới 9 × 13, điểm đầu S tại (7, 1), đích G tại (1, 11). Tọa độ theo **(hàng, cột)**, đếm từ 0; hàng tăng từ trên xuống. Có bốn hướng đi, chi phí mỗi bước bằng 1, không đi chéo. Nhãn ô xanh là chi phí đã chốt; nhãn ô vàng là chi phí tạm thời của đỉnh đang chờ; ∞ cho biết ô chưa được tìm tới. Viền cam đánh dấu đỉnh vừa mở rộng; đường xanh lá là đường ngắn nhất tìm được. Các ô vật cản không có nhãn.

Trong hàm `example_map()`, thay giá trị 0/1 hoặc vị trí `start`, `goal` để đổi ví dụ. Hàm `dijkstra()` xử lý bản đồ chữ nhật; thuật toán tách khỏi phần vẽ. Ở bản đồ chi phí đồng nhất, BFS cũng tìm được đường ngắn nhất; chương trình này dùng hàng đợi ưu tiên để thể hiện đúng Dijkstra. Chương trình dừng khi **lấy đích ra để chốt**, nên một số ô khác vẫn có nhãn tạm thời hoặc chưa được tìm tới.

Xuất riêng từng bước hoặc đổi thư mục đích:

```powershell
python code/Dijkstra_algorithm.py --all-steps
python code/Dijkstra_algorithm.py --output-dir code/output/vi_du_khac --no-gif --dpi 300
python -m unittest discover -s code -p test_Dijkstra_algorithm.py -v
```

Kiểm tra dùng BFS độc lập trên ví dụ cố định và 40 bản đồ ngẫu nhiên, cùng các trường hợp không có đường, đầu trùng đích và đầu vào không hợp lệ. Lưới mô tả chuyển động điểm; để áp dụng cho robot có kích thước, cần mở rộng vật cản và kiểm tra động học trước khi tạo quỹ đạo thực.
