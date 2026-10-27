#include "PID_controller.h"
#include <math.h>

PIDController::PIDController(float kp, float ki, float kd,
                              float outputMin, float outputMax,
                              float integralClamp)
    : _kp(kp), _ki(ki), _kd(kd),
      _outputMin(outputMin), _outputMax(outputMax),
      _integralClamp(integralClamp) {
}

void PIDController::setGains(float kp, float ki, float kd) {
    _kp = kp;
    _ki = ki;
    _kd = kd;
}

void PIDController::setSetpoint(float setpointCm) {
    _setpoint = setpointCm;
}

void PIDController::reset() {
    _integral = 0.0f;
    _prevError = 0.0f;
    _firstComputeAfterReset = true;
}

float PIDController::compute(float measuredCm, float dtSeconds) {
    if (dtSeconds <= 0.0f) {
        // Tranh chia cho 0 (hoac so am bat thuong) neu ham duoc goi qua nhanh
        return 0.0f;
    }

    float error = _setpoint - measuredCm;

    // ---- Thanh phan TI LE (P) ----
    float pTerm = _kp * error;

    // ---- Thanh phan TICH PHAN (I) - co CHONG BAO HOA (anti-windup) ----
    _integral += error * dtSeconds;
    if (_integral > _integralClamp)       _integral = _integralClamp;
    else if (_integral < -_integralClamp) _integral = -_integralClamp;
    float iTerm = _ki * _integral;

    // ---- Thanh phan VI PHAN (D) ----
    // Bo qua o lan tinh dau tien sau reset() vi chua co _prevError hop le,
    // tranh sinh ra 1 xung dao ham gia tao (derivative kick).
    float derivative = _firstComputeAfterReset ? 0.0f : (error - _prevError) / dtSeconds;
    float dTerm = _kd * derivative;

    _prevError = error;
    _firstComputeAfterReset = false;

    float output = pTerm + iTerm + dTerm;

    // ---- Gioi han (saturate) output trong dai PWM cho phep ----
    if (output > _outputMax) {
        output = _outputMax;
        // Chong bao hoa kieu "conditional integration": neu output da bao hoa
        // THEO CHIEU sai so hien tai, rut lai phan tich phan vua cong them de
        // khong tiep tuc tich luy vo ich trong luc dang bao hoa.
        if (error > 0) _integral -= error * dtSeconds;
    } else if (output < _outputMin) {
        output = _outputMin;
        if (error < 0) _integral -= error * dtSeconds;
    }

    return output;
}

bool PIDController::atSetpoint(float measuredCm, float toleranceCm) const {
    return fabsf(_setpoint - measuredCm) <= toleranceCm;
}

float PIDController::getLastError() const {
    return _prevError;
}
