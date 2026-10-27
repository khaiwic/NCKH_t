#include "Analog_button.h"

AnalogButton::AnalogButton(uint8_t analogPin) : _analogPin(analogPin) {
}

void AnalogButton::begin() {
    pinMode(_analogPin, INPUT);
}

bool AnalogButton::classifyRaw(int adcValue, Button &outButton) const {
    // ------------------------------------------------------------------
    // BANG MUC DIEN AP ADC MAU (gia dinh mach dung 1 dien tro keo len VCC,
    // moi nut noi tiep 1 dien tro khac nhau xuong GND - kieu mach "resistor
    // ladder" pho bien cho ban phim analog 1 chan).
    //
    // *** BAT BUOC PHAI HIEU CHINH LAI CAC GIA TRI NAY TREN MACH THAT ***
    // Cach hieu chinh: nap 1 doan code tam thoi chi co
    //     Serial.println(analogRead(ButtonPins::ANALOG_BUTTON_PIN));
    // trong loop(), mo Serial Monitor, nhan giu tung phim va ghi lai gia tri
    // ADC hien thi duoc, roi thay vao "center" tuong ung ben duoi. TOLERANCE
    // nen chon nho hon 1 nua khoang cach giua 2 muc ADC gan nhau nhat.
    // ------------------------------------------------------------------
    struct Band { int center; Button button; };
    static const Band bands[] = {
        {4095, Button::NONE},
        {3300, Button::OK},
        {2500, Button::LEFT},
        {1700, Button::RIGHT},
        {900,  Button::FORWARD},
        {100,  Button::BACKWARD},
    };
    constexpr int TOLERANCE = 150;

    for (const auto &band : bands) {
        if (abs(adcValue - band.center) <= TOLERANCE) {
            outButton = band.button;
            return true;
        }
    }
    return false; // Khong khop dai nao => dien ap bat thuong (vd. nhan 2 phim cung luc)
}

void AnalogButton::update() {
    int adcValue = analogRead(_analogPin);
    Button rawButton;
    bool validReading = classifyRaw(adcValue, rawButton);
    uint32_t now = millis();

    _newlyPressed = Button::NONE; // Reset su kien "vua nhan" cua lan goi truoc

    if (!validReading) {
        // Dien ap khong khop dai nao da dinh nghia
        if (_invalidStartTime == 0) {
            _invalidStartTime = now;
        } else if ((now - _invalidStartTime) >= INVALID_CONFIRM_MS) {
            _errorType = ButtonError::INVALID_VOLTAGE;
        }
        // Khong cap nhat _currentButton khi tin hieu khong hop le - giu nguyen
        // trang thai da xac nhan truoc do cho den khi tin hieu on dinh tro lai.
        return;
    }
    _invalidStartTime = 0; // Tin hieu hop le tro lai => xoa moc dem dien ap bat thuong

    if (rawButton != _lastRawButton) {
        _lastRawButton = rawButton;
        _lastChangeTime = now;
    }

    if ((now - _lastChangeTime) >= DEBOUNCE_MS && rawButton != _currentButton) {
        // Gia tri tho da on dinh du lau va khac trang thai da xac nhan truoc do
        _currentButton = rawButton;
        _pressStartTime = now;
        if (_currentButton != Button::NONE) {
            _newlyPressed = _currentButton; // Phat sinh su kien "vua nhan" (canh len)
        }
    }

    // Kiem tra loi "giu phim qua lau" - ap dung cho CA phim huong lan phim OK
    if (_currentButton != Button::NONE && (now - _pressStartTime) >= HOLD_ERROR_MS) {
        _errorType = ButtonError::HELD_TOO_LONG;
    }
}

Button AnalogButton::getButton() const {
    return _currentButton;
}

Button AnalogButton::getNewlyPressedButton() const {
    return _newlyPressed;
}

uint32_t AnalogButton::getHoldDurationMs() const {
    if (_currentButton == Button::NONE) return 0;
    return millis() - _pressStartTime;
}

bool AnalogButton::isError() const {
    return _errorType != ButtonError::NONE;
}

ButtonError AnalogButton::getErrorType() const {
    return _errorType;
}

void AnalogButton::clearError() {
    _errorType = ButtonError::NONE;
    _invalidStartTime = 0;
}
