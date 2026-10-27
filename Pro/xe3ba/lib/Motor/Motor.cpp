#include "Motor.h"

// ============================================================================
//  TUONG THICH PHIEN BAN LEDC (PWM) GIUA ARDUINO-ESP32 CORE 2.x VA 3.x
// ----------------------------------------------------------------------------
//  Kiem tra thang 7/2026: goi "platformio/espressif32" CHINH THUC van dong
//  bang Arduino core 2.0.17, dung API LEDC theo "channel" (ledcSetup +
//  ledcAttachPin + ledcWrite(channel, duty)). Trong khi do, Arduino-ESP32 core
//  3.x (vi du qua fork cong dong "pioarduino") da BO cac ham nay, thay bang
//  API moi theo "pin" (ledcAttach(pin,...) + ledcWrite(pin, duty)).
//
//  De code nay chay duoc voi CA HAI truong hop ma khong can sua tay, ta kiem
//  tra macro phien ban ESP_ARDUINO_VERSION_MAJOR (co san tu Arduino.h) va
//  chon API phu hop tai thoi diem bien dich.
// ============================================================================
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
    #define MOTOR_PWM_ATTACH(pin, ch, freq, resBits)  ledcAttach((pin), (freq), (resBits))
    #define MOTOR_PWM_WRITE(pin, ch, duty)            ledcWrite((pin), (duty))
#else
    #define MOTOR_PWM_ATTACH(pin, ch, freq, resBits)  do { ledcSetup((ch), (freq), (resBits)); ledcAttachPin((pin), (ch)); } while (0)
    #define MOTOR_PWM_WRITE(pin, ch, duty)             ledcWrite((ch), (duty))
#endif

Motor::Motor(uint8_t in1Pin, uint8_t in2Pin, uint8_t pwmPin,
             uint8_t encoderPinA, uint8_t encoderPinB,
             uint8_t ledcChannel,
             float wheelDiameterCm, float gearRatio, uint32_t encoderPPR,
             bool reversed)
    : _in1Pin(in1Pin), _in2Pin(in2Pin), _pwmPin(pwmPin),
      _encoderPinA(encoderPinA), _encoderPinB(encoderPinB),
      _ledcChannel(ledcChannel),
      _wheelDiameterCm(wheelDiameterCm), _gearRatio(gearRatio),
      _encoderPPR(encoderPPR), _reversed(reversed) {
}

void Motor::begin() {
    pinMode(_in1Pin, OUTPUT);
    pinMode(_in2Pin, OUTPUT);

    MOTOR_PWM_ATTACH(_pwmPin, _ledcChannel, PWM_FREQ_HZ, PWM_RESOLUTION_BITS);

    pinMode(_encoderPinA, INPUT);
    pinMode(_encoderPinB, INPUT);

    stop(); // Dam bao dong co dung yen ngay khi khoi tao, truoc khi lam gi khac

    // Gan ngat cho kenh A cua Encoder. Dung attachInterruptArg (thay vi
    // attachInterrupt thong thuong) de truyen con tro "this" vao ISR, cho
    // phep moi doi tuong Motor co ISR rieng ma KHONG can bien toan cuc.
    attachInterruptArg(digitalPinToInterrupt(_encoderPinA), Motor::onEncoderInterrupt, this, RISING);
}

void Motor::setPWM(int16_t pwmValue) {
    pwmValue = constrain(pwmValue, (int16_t)-255, (int16_t)255);

    // "_reversed" duoc ap dung O DAY (chieu dien) VA trong ISR (chieu dem xung),
    // giup lop ben ngoai (PID, main.cpp) khong can quan tam dong co nao dang
    // lap nguoc tren khung xe - "PWM duong" luon dong nghia voi "tien".
    int16_t effectiveValue = _reversed ? (int16_t)(-pwmValue) : pwmValue;

    if (effectiveValue > 0) {
        // Quay thuan - gop phan lam xe TIEN
        digitalWrite(_in1Pin, HIGH);
        digitalWrite(_in2Pin, LOW);
    } else if (effectiveValue < 0) {
        // Quay nghich - gop phan lam xe LUI
        digitalWrite(_in1Pin, LOW);
        digitalWrite(_in2Pin, HIGH);
    } else {
        // PWM = 0: dung tu do (coast), khong thang gap
        digitalWrite(_in1Pin, LOW);
        digitalWrite(_in2Pin, LOW);
    }

    uint32_t dutyMagnitude = (uint32_t)abs((int)effectiveValue);
    MOTOR_PWM_WRITE(_pwmPin, _ledcChannel, dutyMagnitude);
}

void Motor::stop() {
    // Thang gap (short brake) theo bang trang thai cua TB6612FNG:
    // IN1=HIGH, IN2=HIGH => dong co bi thang bat ke gia tri PWM.
    digitalWrite(_in1Pin, HIGH);
    digitalWrite(_in2Pin, HIGH);
    MOTOR_PWM_WRITE(_pwmPin, _ledcChannel, 0);
}

float Motor::getDistanceCm() const {
    // Cong thuc: quang duong = (so xung / so xung moi vong quay BANH XE) * chu vi banh xe
    // "So xung moi vong quay banh xe" = PPR cua Encoder (o truc dong co, TRUOC hop so) * ti so truyen
    long pulses = _pulseCount; // Doc 1 lan (an toan: doc gia tri 32-bit align tu nhien tren kien truc nay)
    float pulsesPerWheelRev = (float)_encoderPPR * _gearRatio;
    float wheelRevolutions = (float)pulses / pulsesPerWheelRev;
    return wheelRevolutions * PI * _wheelDiameterCm;
}

void Motor::resetEncoder() {
    noInterrupts(); // Tam khoa ngat de tranh ISR ghi de dung luc dang reset
    _pulseCount = 0;
    interrupts();
}

long Motor::getPulseCount() const {
    return _pulseCount;
}

void IRAM_ATTR Motor::handleEncoderInterrupt() {
    // Doc muc tin hieu kenh B ngay tai thoi diem canh len cua kenh A de
    // xac dinh chieu quay (giai ma Encoder pha A/B don gian, do 1 canh/chu ky).
    bool bState = digitalRead(_encoderPinB);
    int8_t direction = bState ? 1 : -1;
    if (_reversed) direction = (int8_t)(-direction);
    _pulseCount += direction;
}

void IRAM_ATTR Motor::onEncoderInterrupt(void* arg) {
    Motor* self = static_cast<Motor*>(arg);
    self->handleEncoderInterrupt();
}
