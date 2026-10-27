#pragma once
// ============================================================================
//  Analog_button.h - Doc 5 nut nhan (Tien, Lui, Trai, Phai, OK) qua 1 chan
//                     Analog duy nhat (mach phan ap dien tro), co Debounce
//                     va phat hien 2 loai loi theo de bai muc 3.3:
//                       1) Giu 1 phim lien tuc qua 5 giay (HELD_TOO_LONG)
//                       2) Dien ap ADC khong khop dai nao da dinh nghia, vi
//                          du do nhan dong thoi 2 phim doi nghich cung luc
//                          (INVALID_VOLTAGE)
// ============================================================================

#include <Arduino.h>

enum class Button : uint8_t {
    NONE = 0,
    FORWARD,
    BACKWARD,
    LEFT,
    RIGHT,
    OK
};

enum class ButtonError : uint8_t {
    NONE = 0,
    HELD_TOO_LONG,     // Mot phim huong bat ky hoac phim OK bi giu > 5 giay
    INVALID_VOLTAGE    // Dien ap ADC khong khop dai nao (nghi nhan 2 phim cung luc)
};

class AnalogButton {
public:
    explicit AnalogButton(uint8_t analogPin);

    // Goi 1 lan trong setup()
    void begin();

    // Goi MOI vong lap trong loop() de doc va cap nhat trang thai phim
    void update();

    // Phim dang duoc giu (da qua debounce xac nhan), Button::NONE neu khong co
    Button getButton() const;

    // Phim VUA duoc xac nhan nhan trong lan update() nay (canh len sau debounce).
    // Chi co gia tri KHAC NONE dung 1 lan tai thoi diem chuyen trang thai, cac
    // lan update() sau do (khi van dang giu phim) se tra ve NONE. Dung de kich
    // hoat hanh dong "1 lan" (vi du: bat dau 1 lenh di chuyen, chuyen state...)
    // ma khong bi lap lai lien tuc trong khi nguoi dung con giu phim.
    Button getNewlyPressedButton() const;

    // Thoi gian (ms) ma phim hien tai (getButton()) da duoc giu LIEN TUC.
    // Tra ve 0 neu khong co phim nao dang duoc giu.
    uint32_t getHoldDurationMs() const;

    // true neu dang co loi (giu phim qua lau HOAC dien ap bat thuong)
    bool isError() const;

    // Loai loi cu the (de debug / hien thi rieng neu can)
    ButtonError getErrorType() const;

    // Xoa trang thai loi hien tai (goi khi he thong thoat khoi trang thai ERROR)
    void clearError();

private:
    uint8_t _analogPin;

    Button _currentButton   = Button::NONE; // Phim da duoc XAC NHAN (qua debounce)
    Button _lastRawButton   = Button::NONE; // Gia tri doc THO gan nhat (chua debounce)
    Button _newlyPressed    = Button::NONE; // Su kien "vua nhan" cua lan update() nay

    uint32_t _lastChangeTime   = 0; // Moc thoi gian gia tri THO thay doi lan cuoi (dung cho debounce)
    uint32_t _pressStartTime   = 0; // Moc thoi gian phim hien tai (_currentButton) bat dau duoc giu
    uint32_t _invalidStartTime = 0; // Moc thoi gian bat dau ghi nhan dien ap bat thuong lien tuc (0 = chua ghi nhan)

    ButtonError _errorType = ButtonError::NONE;

    static constexpr uint32_t DEBOUNCE_MS        = 30;  // Gia tri THO phai on dinh toi thieu tung nay ms moi duoc xac nhan
    static constexpr uint32_t HOLD_ERROR_MS      = 5000; // Nguong bao loi "giu phim qua lau"
    static constexpr uint32_t INVALID_CONFIRM_MS = 50;   // Dien ap bat thuong phai lien tuc tung nay ms moi bao loi (tranh nhieu tuc thoi)

    // Phan loai 1 gia tri ADC tho thanh 1 trong 6 trang thai (5 phim + NONE).
    // Tra ve true va gan outButton neu khop 1 dai da dinh nghia; tra ve false
    // neu khong khop dai nao (dien ap bat thuong).
    bool classifyRaw(int adcValue, Button &outButton) const;
};
