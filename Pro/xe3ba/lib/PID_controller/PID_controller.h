#pragma once
// ============================================================================
//  PID_controller.h - Bo dieu khien PID VI TRI (theo quang duong, don vi cm).
//
//  Day la 1 lop PID DUNG CHUNG, tao 2 doi tuong doc lap (1 cho banh trai, 1
//  cho banh phai) trong main.cpp - moi doi tuong tu quan ly setpoint/tich
//  phan/sai so rieng => thoa yeu cau "PID doc lap cho 2 dong co" ma van tan
//  dung code (khong lap lai logic).
//
//  Input   : quang duong hien tai do duoc tu Encoder (cm) - do main.cpp doc
//            tu Motor::getDistanceCm() va truyen vao qua compute()
//  Setpoint: quang duong (hoac do dai cung tuong duong cho lenh xoay) muc
//            tieu can dat (cm)
//  Output  : gia tri PWM (-255..255) de truyen thang cho Motor::setPWM()
// ============================================================================

#include <Arduino.h>

class PIDController {
public:
    // kp, ki, kd       : cac he so PID - CAN HIEU CHINH THUC TE tren xe that
    // outputMin/Max    : gioi han bao hoa nga ra (khop voi dai PWM -255..255)
    // integralClamp    : gioi han bien do phan tich phan noi bo (chong boi hoa/anti-windup)
    PIDController(float kp, float ki, float kd,
                  float outputMin = -255.0f, float outputMax = 255.0f,
                  float integralClamp = 100.0f);

    void setGains(float kp, float ki, float kd);

    // Dat quang duong/do dai muc tieu can dat (cm)
    void setSetpoint(float setpointCm);

    // Xoa tich phan va sai so cu - BAT BUOC goi truoc khi bat dau 1 lenh di
    // chuyen MOI, neu khong so tich phan cua lenh truoc se lam sai lenh sau
    void reset();

    // Tinh gia tri PWM output dua tren vi tri do duoc (measuredCm) va thoi
    // gian troi qua tu lan goi truoc (dtSeconds, don vi GIAY)
    float compute(float measuredCm, float dtSeconds);

    // true neu vi tri hien tai da nam trong pham vi sai so cho phep so voi setpoint
    bool atSetpoint(float measuredCm, float toleranceCm) const;

    // Sai so cua lan compute() gan nhat - tien ich cho debug/hien thi qua Serial
    float getLastError() const;

private:
    float _kp, _ki, _kd;
    float _outputMin, _outputMax;
    float _integralClamp;

    float _setpoint  = 0.0f;
    float _integral  = 0.0f;
    float _prevError = 0.0f;
    bool  _firstComputeAfterReset = true;
};
