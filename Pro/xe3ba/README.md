# Xe 3 banh ESP32-C3 - PID Controller

Project PlatformIO cho xe 3 banh (2 banh chu dong + 1 banh mat trau), dieu
khien vi tri bang PID dua tren Encoder, nhan lenh tu 5 nut nhan Analog, ho tro
Record/Playing va trang thai loi an toan.

## 1. Cau truc thu muc

```
xe3banh_esp32c3/
├── platformio.ini
├── include/Pinconfig.h          # Namespace MotorPins, ButtonPins
├── lib/Motor/                   # Dieu khien TB6612FNG + doc Encoder
├── lib/Analog_button/           # Doc 5 nut nhan qua 1 chan ADC + debounce + loi
├── lib/PID_controller/          # PID vi tri, co anti-windup
└── src/main.cpp                 # May trang thai IDLE/RECORD/PLAYING/ERROR
```

Mo thu muc nay bang **PlatformIO** (VS Code extension) - KHONG dung Arduino
IDE thuan vi cau truc `include/` + `lib/` theo kieu nay la quy uoc rieng cua
PlatformIO.

## 2. CAC GIA DINH QUAN TRONG - doc truoc khi build

De bai khong cho mot so con so/thiet ke cu the; code da chon gia tri mac dinh
hop ly nhung **ban can kiem tra va chinh lai** truoc khi nap vao xe that:

| Muc | O dau trong code | Ghi chu |
|---|---|---|
| So do chan GPIO | `include/Pinconfig.h` | Vi du mau cho ESP32-C3 pho thong; doi chieu voi board thuc te |
| Duong kinh banh, ti so hop so, PPR Encoder, khoang cach 2 banh (wheelbase) | `src/main.cpp` → namespace `RobotConfig` | Phai do dac/tra datasheet dong co N20 that su dang dung |
| He so PID (Kp, Ki, Kd) | `src/main.cpp` → namespace `PIDConfig` | Chi la diem khoi dau, xem muc 4 ben duoi de hieu chinh |
| Nguong ADC cua 5 nut nhan | `lib/Analog_button/Analog_button.cpp` → ham `classifyRaw()` | Chi la vi du mau, **bat buoc do dac thuc te** (xem comment trong file) |
| Y nghia hanh vi cua RECORD | `src/main.cpp` (dau file) | De bai khong noi ro xe co chay ngay trong luc Record hay khong - code hien chon "chi luu lenh, khong chay", xem giai thich ben duoi |

## 3. Gia dinh ve hanh vi trang thai RECORD

De bai mo ta IDLE la "nhan phim huong se chay don lenh **ngay lap tuc**",
nhung mo ta RECORD chi noi "se luu chuoi lenh nay vao mot mang hoac
std::vector" - khong lap lai cum tu "chay ngay". Code trong repo nay hieu day
la chu y: **RECORD la che do "lap trinh"** - nhan phim huong chi ghi lenh vao
hang doi, xe dung yen; toan bo lenh chi thuc su chay khi sang PLAYING.

Neu ban muon xe **vua chay vua ghi nho** ngay trong luc RECORD (kieu "day xe
di va no nho duong di"), chi can them 1 dong `movement.start(cmd);` trong ham
`handleRecordState()` cua `src/main.cpp` (da co san vi tri + comment danh
dau). Motor/PID khong can sua gi them.

## 4. Cac buoc hieu chinh truoc khi chay that

1. **Do dac phan cung**: duong kinh banh (thuoc keo), khoang cach tam 2 banh
   (wheelbase), roi cap nhat namespace `RobotConfig` trong `main.cpp`. Tra so
   PPR cua Encoder tren datasheet dong co N20 dang dung.
2. **Hieu chinh nguong ADC cua nut nhan**: nap tam 1 doan code chi co
   `Serial.println(analogRead(ButtonPins::ANALOG_BUTTON_PIN));` trong
   `loop()`, mo Serial Monitor (115200 baud), nhan tung phim va ghi lai gia
   tri hien thi, roi cap nhat bang `bands[]` trong `Analog_button.cpp`.
3. **Kiem tra chieu quay/chieu dem Encoder**: cho chay lenh TIEN don le. Neu
   banh xe chay LUI thay vi TIEN, doi tham so `reversed` khi khoi tao `Motor`
   tuong ung trong `main.cpp`. Neu quang duong bao ve Serial luon la so am dù
   xe dang tien, cung la dau hieu can doi `reversed`.
4. **Hieu chinh PID**: bat dau tu `Kp` (tang dan cho toi khi xe bam sat quang
   duong muc tieu nhung chua rung lac manh), roi them mot chut `Kd` de giam
   dao dong/vot qua dich, cuoi cung them mot chut `Ki` nho de trieu tieu sai
   so du (steady-state error) neu xe luon dung hut mot chut truoc/sau dich.
   Tang tung thong so mot cach tu tu va quan sat qua Serial Monitor.
5. **Kiem tra chieu xoay Trai/Phai**: neu xe xoay nguoc huong mong muon, doi
   cho nhau 2 dong gan `leftTargetCm`/`rightTargetCm` trong ham
   `computeWheelTargets()` (trong `main.cpp`) cho lenh `LEFT` va `RIGHT`.

## 5. Ve driver TB6612FNG

Code chi dieu khien IN1/IN2/PWM cho moi dong co (dung nhu de bai yeu cau).
Chan **STBY** cua module TB6612FNG (neu breakout board co dua ra) can duoc
noi CUNG bang day jumper truc tiep len **3.3V**, vi project khong dieu khien
STBY bang phan mem.

## 6. Ghi chu ky thuat ve PWM (LEDC) - quan trong, giup code chay duoc

Tinh den thoi diem viet code nay (7/2026), goi `platformio/espressif32`
**chinh thuc** van dong bang Arduino-ESP32 core **2.0.17**, dung API LEDC
kieu cu (`ledcSetup` + `ledcAttachPin` + `ledcWrite(channel, ...)`). Cac ban
core 3.x (thuong cai qua fork cong dong nhu "pioarduino") da doi sang API moi
(`ledcAttach(pin, ...)` + `ledcWrite(pin, ...)`), khong con ho tro API cu.

`lib/Motor/Motor.cpp` da tu kiem tra macro `ESP_ARDUINO_VERSION_MAJOR` va tu
dong chon API phu hop - ban KHONG can sua gi ca du dang dung core 2.x (mac
dinh) hay 3.x. Da kiem thu bien dich (mock) thanh cong cho ca 2 truong hop.

## 7. Build & nap code

Trong VS Code (co extension PlatformIO): mo thu muc nay, bam **Build** (icon
dau tick) roi **Upload** (icon mui ten). Mo **Serial Monitor** (115200 baud)
de xem log trang thai.

## 8. Tom tat may trang thai

- **IDLE**: dung yen. Nhan phim huong → chay 1 lenh ngay. Nhan OK → sang RECORD.
- **RECORD**: nhan phim huong → chi luu vao hang doi (xem muc 3). Nhan OK lan
  nua → sang PLAYING.
- **PLAYING**: tu dong chay tuan tu toan bo hang doi bang PID; het hang doi →
  xoa hang doi, ve IDLE.
- **ERROR**: kich hoat ngay khi giu 1 phim > 5s HOAC dien ap ADC bat thuong
  (nghi ngo nhan 2 phim doi nghich cung luc). Dung dong co ngay, xoa het hang
  doi. Giu OK lien tuc 2s de thoat ve IDLE.
