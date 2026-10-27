#pragma once
// ============================================================================
//  Motor.h - Dieu khien 1 dong co DC Gear Motor N20 qua driver TB6612FNG,
//            dong thoi doc xung Encoder (2 kenh A/B) de tinh quang duong di
//            duoc cua banh xe.
//
//  Moi doi tuong Motor quan ly MOT dong co. Xe 3 banh can 2 doi tuong (trai,
//  phai). Lop nay KHONG biet gi ve PID hay Pinconfig - no chi nhan cac chan
//  va thong so vat ly qua constructor, giup de tai su dung / kiem thu doc lap.
// ============================================================================

#include <Arduino.h>

class Motor {
public:
    // in1Pin, in2Pin      : 2 chan dieu khien chieu quay cua TB6612FNG
    // pwmPin               : chan xung PWM dieu khien toc do
    // encoderPinA/B         : 2 chan doc xung vuong pha A/B cua Encoder
    // ledcChannel           : kenh LEDC rieng cho dong co nay (0..5 tren ESP32-C3),
    //                          moi dong co PHAI dung 1 kenh khac nhau
    // wheelDiameterCm       : duong kinh banh xe (cm)
    // gearRatio             : ti so truyen hop so (vi du hop so 1:100 => truyen 100.0f)
    // encoderPPR            : so xung/vong quay CUA TRUC DONG CO (truoc hop so)
    // reversed              : dat true neu dong co nay duoc lap GUONG so voi dong co
    //                          con lai tren khung xe (VD dong co phai thuong lap
    //                          nguoc chieu so voi dong co trai) - Motor se tu dong
    //                          dao chieu ca khi CHAY (setPWM) lan khi DO (encoder)
    //                          de "PWM duong" luon co nghia la "gop phan lam xe tien"
    Motor(uint8_t in1Pin, uint8_t in2Pin, uint8_t pwmPin,
          uint8_t encoderPinA, uint8_t encoderPinB,
          uint8_t ledcChannel,
          float wheelDiameterCm, float gearRatio, uint32_t encoderPPR,
          bool reversed = false);

    // Goi 1 lan trong setup(): cau hinh chan INPUT/OUTPUT, LEDC PWM va ngat Encoder
    void begin();

    // Cap gia tri PWM cho dong co, gia tri hop le: -255..255
    // Duong = tien (theo quy uoc "gop phan lam xe tien"), am = lui, 0 = dung tu do
    void setPWM(int16_t pwmValue);

    // Dung gap (thang dong co - short brake): dua IN1=IN2=HIGH bat ke PWM,
    // dung cho truong hop can dung ngay lap tuc (ket thuc 1 lenh, hoac ERROR)
    void stop();

    // Tra ve quang duong da di duoc cua banh xe nay tinh tu lan resetEncoder()
    // gan nhat (cm), CO DAU: duong = huong "tien", am = huong "lui"
    float getDistanceCm() const;

    // Dat lai bo dem xung Encoder va quang duong ve 0 (goi khi bat dau 1 lenh di chuyen moi)
    void resetEncoder();

    // Doc so xung Encoder tho hien tai (co dau), dung cho debug
    long getPulseCount() const;

    // --- Noi bo: xu ly ngat Encoder. Public vi can duoc goi tu ham "trampoline"
    //     tinh (static) ben ngoai lop - xem Motor.cpp de biet ly do ky thuat.
    void IRAM_ATTR handleEncoderInterrupt();

private:
    uint8_t _in1Pin, _in2Pin, _pwmPin;
    uint8_t _encoderPinA, _encoderPinB;
    uint8_t _ledcChannel;
    float _wheelDiameterCm;
    float _gearRatio;
    uint32_t _encoderPPR;
    bool _reversed;

    volatile long _pulseCount = 0;

    static constexpr uint32_t PWM_FREQ_HZ        = 5000; // Tan so PWM (Hz) - 5kHz nam ngoai vung nghe duoc, tranh dong co keu ri
    static constexpr uint8_t  PWM_RESOLUTION_BITS = 8;    // Do phan giai PWM: 8 bit => 0..255, khop voi yeu cau output PID

    // Ham "trampoline" tinh, dung lam callback cho attachInterruptArg(): nhan
    // con tro 'this' qua tham so arg roi goi lai ham thanh vien tuong ung.
    // Can thiet vi attachInterruptArg yeu cau con tro ham kieu C (khong phai
    // con tro ham thanh vien), day la cach chuan de lam ISR huong doi tuong
    // tren ESP32 Arduino core.
    static void IRAM_ATTR onEncoderInterrupt(void* arg);
};
