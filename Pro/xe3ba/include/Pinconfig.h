#pragma once
// ============================================================================
//  Pinconfig.h - Cau hinh toan bo chan ket noi phan cung cho ESP32-C3-Mini
// ============================================================================
//
//  LUU Y QUAN TRONG - DAY LA SO DO CHAN MAU:
//  File nay chi la mot vi du hop ly cho board ESP32-C3 pho thong (vi du:
//  ESP32-C3-DevKitM-1, ESP32-C3 SuperMini...). Ban BAT BUOC phai doi chieu
//  voi so do chan (pinout diagram) thuc te cua board minh dang dung roi
//  chinh lai cac hang so ben duoi cho khop, vi cac hang khac nhau co the
//  khong dua ra cung mot so chan GPIO kha dung.
//
//  Ve 3 chan "strapping" GPIO2, GPIO8, GPIO9 (anh huong che do boot cua chip):
//  o day chung CHI duoc dung lam ngo OUTPUT dieu khien driver TB6612FNG
//  (IN1/IN2/PWM - la chan do chinh ESP32 chu dong keo muc dien ap), TRANH
//  dung cho ngo vao Encoder (input thu dong, co the bi keo muc boi phan
//  cung ben ngoai dung luc cap nguon, gay anh huong den che do boot). Day la
//  lua chon an toan hop ly, nhung van nen kiem tra lai voi board thuc te.
// ============================================================================

#include <Arduino.h>

namespace MotorPins {
    // ---- Dong co TRAI (Left / Motor A) ----
    constexpr uint8_t LEFT_IN1        = 6;   // Chan dieu khien chieu quay 1
    constexpr uint8_t LEFT_IN2        = 7;   // Chan dieu khien chieu quay 2
    constexpr uint8_t LEFT_PWM        = 10;  // Chan xung PWM (toc do)
    constexpr uint8_t LEFT_ENCODER_A  = 0;   // Kenh A cua Encoder (ngat ngoai)
    constexpr uint8_t LEFT_ENCODER_B  = 1;   // Kenh B cua Encoder (doc chieu quay)

    // ---- Dong co PHAI (Right / Motor B) ----
    constexpr uint8_t RIGHT_IN1       = 2;   // GPIO2 la chan strapping - xem ghi chu tren dau file
    constexpr uint8_t RIGHT_IN2       = 8;   // GPIO8 la chan strapping - xem ghi chu tren dau file
    constexpr uint8_t RIGHT_PWM       = 9;   // GPIO9 la chan strapping - xem ghi chu tren dau file
    constexpr uint8_t RIGHT_ENCODER_A = 3;
    constexpr uint8_t RIGHT_ENCODER_B = 5;

    // ---- Kenh LEDC (PWM) danh rieng cho tung dong co ----
    // ESP32-C3 co 6 kenh LEDC doc lap, du dung cho 2 dong co.
    constexpr uint8_t LEFT_LEDC_CHANNEL  = 0;
    constexpr uint8_t RIGHT_LEDC_CHANNEL = 1;

    // Ghi chu phan cung: chan STBY cua module TB6612FNG (neu breakout board co
    // dua chan nay ra) nen noi truc tiep len 3.3V (VCC logic) bang day jumper,
    // vi de bai chi yeu cau dieu khien IN1/IN2/PWM, khong can bat/tat STBY
    // bang phan mem trong project nay.
}

namespace ButtonPins {
    // Chan Analog (ADC1_CH4 - co kha nang doc ADC) doc dien ap tu mach phan
    // ap dien tro cua 5 nut nhan (Tien, Lui, Trai, Phai, OK).
    constexpr uint8_t ANALOG_BUTTON_PIN = 4;
}
