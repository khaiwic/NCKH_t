// ============================================================================
//  main.cpp - File DIEU PHOI (coordinator) cho xe 3 banh ESP32-C3
//
//  Dieu phoi 3 khoi xay dung (Motor, AnalogButton, PIDController) theo may
//  trang thai 4 che do: IDLE - RECORD - PLAYING - ERROR (xem muc 4 de bai).
//
//  *** GIA DINH QUAN TRONG can luu y (xem README.md de biet chi tiet) ***
//  O che do RECORD, de bai chi noi "luu chuoi lenh vao mang/vector" ma KHONG
//  noi la xe co di chuyen ngay hay khong (khac voi mo ta IDLE co ghi ro
//  "chay don lenh NGAY LAP TUC"). File nay hieu RECORD la che do "lap trinh"
//  thuan tuy: nhan phim huong CHI luu lenh vao hang doi, xe DUNG YEN, va chi
//  thuc su chay tat ca khi sang PLAYING. Neu ban muon xe VUA chay VUA ghi
//  nho ngay trong luc RECORD, chi can goi them startMovement(cmd) trong
//  handleRecordState() ben duoi (da chua san vi tri de them).
// ============================================================================

#include <Arduino.h>
#include <vector>
#include "Pinconfig.h"
#include "Motor.h"
#include "Analog_button.h"
#include "PID_controller.h"

// ============================================================================
//  CAU HINH THONG SO VAT LY CUA XE - BAT BUOC DO DAC THUC TE VA CAP NHAT LAI
// ============================================================================
namespace RobotConfig {
    constexpr float WHEEL_DIAMETER_CM = 4.2f;   // Duong kinh banh xe (cm)
    constexpr float GEAR_RATIO         = 100.0f; // Ti so truyen hop so N20 (vd 1:100)
    constexpr uint32_t ENCODER_PPR     = 7;      // So xung/vong TRUC DONG CO (xem datasheet N20)
    constexpr float WHEELBASE_CM       = 15.0f;  // Khoang cach tam 2 banh chu dong (cm) - do thuc te!

    constexpr float MOVE_DISTANCE_CM = 20.0f;    // Quang duong cho lenh Tien/Lui (theo de bai)
    constexpr float TURN_ANGLE_DEG   = 90.0f;    // Goc quay cho lenh Xoay Trai/Phai (theo de bai)
}

// ============================================================================
//  CAU HINH HE SO PID - BAT BUOC HIEU CHINH THUC TE (xem README.md muc "Hieu chinh PID")
// ============================================================================
namespace PIDConfig {
    constexpr float KP = 40.0f;
    constexpr float KI = 5.0f;
    constexpr float KD = 2.0f;
}

// ============================================================================
//  KIEU DU LIEU MAY TRANG THAI
// ============================================================================
enum class State : uint8_t { IDLE, RECORD, PLAYING, ERROR };

// Lenh di chuyen don (KHONG bao gom OK - OK chi la phim dieu khien che do,
// khong phai lenh di chuyen nen khong duoc ghi vao hang doi Record)
enum class Command : uint8_t { FORWARD, BACKWARD, LEFT, RIGHT };

static const char* commandToText(Command c) {
    switch (c) {
        case Command::FORWARD:  return "TIEN";
        case Command::BACKWARD: return "LUI";
        case Command::LEFT:     return "XOAY TRAI";
        case Command::RIGHT:    return "XOAY PHAI";
    }
    return "?";
}

// ============================================================================
//  DOI TUONG TOAN CUC
// ============================================================================
Motor leftMotor(MotorPins::LEFT_IN1, MotorPins::LEFT_IN2, MotorPins::LEFT_PWM,
                MotorPins::LEFT_ENCODER_A, MotorPins::LEFT_ENCODER_B,
                MotorPins::LEFT_LEDC_CHANNEL,
                RobotConfig::WHEEL_DIAMETER_CM, RobotConfig::GEAR_RATIO, RobotConfig::ENCODER_PPR,
                /*reversed=*/false);

// reversed=true: dong co phai thuong duoc lap GUONG so voi dong co trai tren
// khung xe (xem ghi chu trong Motor.h) - doi lai thanh false neu xe ban chay
// nguoc huong mong muon.
Motor rightMotor(MotorPins::RIGHT_IN1, MotorPins::RIGHT_IN2, MotorPins::RIGHT_PWM,
                  MotorPins::RIGHT_ENCODER_A, MotorPins::RIGHT_ENCODER_B,
                  MotorPins::RIGHT_LEDC_CHANNEL,
                  RobotConfig::WHEEL_DIAMETER_CM, RobotConfig::GEAR_RATIO, RobotConfig::ENCODER_PPR,
                  /*reversed=*/true);

AnalogButton analogButton(ButtonPins::ANALOG_BUTTON_PIN);

PIDController leftPid(PIDConfig::KP, PIDConfig::KI, PIDConfig::KD);
PIDController rightPid(PIDConfig::KP, PIDConfig::KI, PIDConfig::KD);

State currentState = State::IDLE;

constexpr size_t MAX_RECORDED_COMMANDS = 100; // Gioi han an toan, tranh vector phinh to vo han
std::vector<Command> commandQueue;
size_t playbackIndex = 0;

constexpr uint32_t ERROR_EXIT_HOLD_MS = 2000; // Giu OK 2 giay de thoat ERROR (theo de bai)

// ============================================================================
//  BO THUC THI 1 LENH DI CHUYEN (dung PID, khong chan luong loop - non-blocking)
//  Dung chung cho ca IDLE (chay don lenh) va PLAYING (chay tuan tu hang doi)
// ============================================================================
struct MovementExecutor {
    bool _active = false;
    uint32_t _lastPidUpdateMs = 0;
    uint32_t _moveStartMs = 0;

    static constexpr float POSITION_TOLERANCE_CM   = 0.3f; // Sai so cho phep khi dung
    static constexpr uint32_t PID_UPDATE_INTERVAL_MS = 20;  // Chu ky dieu khien PID ~50Hz
    static constexpr uint32_t MOVE_TIMEOUT_MS        = 8000; // Bao ve: qua thoi gian nay ma
                                                              // chua toi dich thi buoc dung
                                                              // (tranh treo neu PID khong hoi tu)

    bool isActive() const { return _active; }

    // Quy doi 1 Command thanh setpoint (cm) cho tung banh xe
    static void computeWheelTargets(Command cmd, float &leftTargetCm, float &rightTargetCm) {
        // Do dai cung ma MOI banh phai di khi xoay tai cho 1 goc TURN_ANGLE_DEG,
        // voi tam xoay la trung diem truc noi 2 banh (cong thuc dong hoc vi sai):
        //   cung = (khoang_cach_2_banh / 2) * goc(radian)
        const float pivotArcCm = (RobotConfig::WHEELBASE_CM / 2.0f)
                                  * (RobotConfig::TURN_ANGLE_DEG * PI / 180.0f);

        switch (cmd) {
            case Command::FORWARD:
                leftTargetCm  = RobotConfig::MOVE_DISTANCE_CM;
                rightTargetCm = RobotConfig::MOVE_DISTANCE_CM;
                break;
            case Command::BACKWARD:
                leftTargetCm  = -RobotConfig::MOVE_DISTANCE_CM;
                rightTargetCm = -RobotConfig::MOVE_DISTANCE_CM;
                break;
            case Command::LEFT:
                // Xoay trai tai cho: banh trai lui, banh phai tien (quy uoc -
                // neu xe ban xoay NGUOC huong mong muon, doi dau 2 dong nay lai)
                leftTargetCm  = -pivotArcCm;
                rightTargetCm =  pivotArcCm;
                break;
            case Command::RIGHT:
                leftTargetCm  =  pivotArcCm;
                rightTargetCm = -pivotArcCm;
                break;
        }
    }

    void start(Command cmd) {
        leftMotor.resetEncoder();
        rightMotor.resetEncoder();

        float leftTargetCm = 0.0f, rightTargetCm = 0.0f;
        computeWheelTargets(cmd, leftTargetCm, rightTargetCm);

        leftPid.reset();
        rightPid.reset();
        leftPid.setSetpoint(leftTargetCm);
        rightPid.setSetpoint(rightTargetCm);

        uint32_t now = millis();
        _lastPidUpdateMs = now;
        _moveStartMs = now;
        _active = true;

        Serial.print("[MOVE] Bat dau lenh: ");
        Serial.print(commandToText(cmd));
        Serial.print(" | Muc tieu trai=");
        Serial.print(leftTargetCm, 2);
        Serial.print("cm, phai=");
        Serial.print(rightTargetCm, 2);
        Serial.println("cm");
    }

    // Goi moi vong lap; tu bo qua neu khong co lenh nao dang chay
    void update() {
        if (!_active) return;

        uint32_t now = millis();

        // Bao ve: qua thoi gian toi da cho 1 lenh (PID khong hoi tu / banh ket...)
        if ((now - _moveStartMs) >= MOVE_TIMEOUT_MS) {
            leftMotor.stop();
            rightMotor.stop();
            _active = false;
            Serial.println("[MOVE] CANH BAO: qua thoi gian cho phep, buoc dung lenh nay.");
            return;
        }

        uint32_t elapsed = now - _lastPidUpdateMs;
        if (elapsed < PID_UPDATE_INTERVAL_MS) return; // Chi cap nhat PID theo chu ky co dinh

        float dtSeconds = elapsed / 1000.0f;
        _lastPidUpdateMs = now;

        float leftDist  = leftMotor.getDistanceCm();
        float rightDist = rightMotor.getDistanceCm();

        float leftOut  = leftPid.compute(leftDist, dtSeconds);
        float rightOut = rightPid.compute(rightDist, dtSeconds);

        bool leftDone  = leftPid.atSetpoint(leftDist, POSITION_TOLERANCE_CM);
        bool rightDone = rightPid.atSetpoint(rightDist, POSITION_TOLERANCE_CM);

        if (leftDone && rightDone) {
            leftMotor.stop();
            rightMotor.stop();
            _active = false;
            Serial.println("[MOVE] Hoan thanh lenh di chuyen.");
            return;
        }

        leftMotor.setPWM((int16_t)leftOut);
        rightMotor.setPWM((int16_t)rightOut);
    }

    // Huy lenh dang chay ngay lap tuc (dung cho ERROR) - KHONG goi Motor::stop()
    // o day vi enterErrorState() da tu lo phan do, tranh goi trung lap
    void cancel() {
        _active = false;
    }
};

MovementExecutor movement;

// ============================================================================
//  HAM TIEN ICH
// ============================================================================
static bool buttonToCommand(Button b, Command &outCmd) {
    switch (b) {
        case Button::FORWARD:  outCmd = Command::FORWARD;  return true;
        case Button::BACKWARD: outCmd = Command::BACKWARD; return true;
        case Button::LEFT:     outCmd = Command::LEFT;     return true;
        case Button::RIGHT:    outCmd = Command::RIGHT;    return true;
        default: return false; // NONE hoac OK khong phai lenh di chuyen
    }
}

static void enterErrorState() {
    leftMotor.stop();
    rightMotor.stop();
    movement.cancel();
    commandQueue.clear();
    playbackIndex = 0;
    currentState = State::ERROR;
    Serial.println("[STATE] ** CHUYEN SANG ERROR ** (loi tu bo doc nut nhan)");
}

// ============================================================================
//  CAC HAM XU LY TUNG TRANG THAI
// ============================================================================
static void handleIdleState() {
    if (!movement.isActive()) {
        Button pressed = analogButton.getNewlyPressedButton();

        if (pressed == Button::OK) {
            currentState = State::RECORD;
            commandQueue.clear();
            Serial.println("[STATE] IDLE -> RECORD");
            return;
        }

        Command cmd;
        if (buttonToCommand(pressed, cmd)) {
            movement.start(cmd); // IDLE: chay don lenh NGAY LAP TUC (theo de bai)
        }
    }
    movement.update();
}

static void handleRecordState() {
    // Xem ghi chu "GIA DINH QUAN TRONG" o dau file: RECORD chi LUU lenh,
    // KHONG lam xe di chuyen. Neu muon vua chay vua ghi, goi them
    // movement.start(cmd) ngay sau khi push_back() ben duoi.
    Button pressed = analogButton.getNewlyPressedButton();

    if (pressed == Button::OK) {
        currentState = State::PLAYING;
        playbackIndex = 0;
        Serial.print("[STATE] RECORD -> PLAYING (da luu ");
        Serial.print(commandQueue.size());
        Serial.println(" lenh)");
        return;
    }

    Command cmd;
    if (buttonToCommand(pressed, cmd)) {
        if (commandQueue.size() < MAX_RECORDED_COMMANDS) {
            commandQueue.push_back(cmd);
            Serial.print("[RECORD] Da luu lenh: ");
            Serial.print(commandToText(cmd));
            Serial.print(" (tong so: ");
            Serial.print(commandQueue.size());
            Serial.println(")");
        } else {
            Serial.println("[RECORD] Canh bao: da dat so luong lenh toi da, bo qua phim nay.");
        }
    }
}

static void handlePlayingState() {
    if (!movement.isActive()) {
        if (playbackIndex < commandQueue.size()) {
            movement.start(commandQueue[playbackIndex]);
            playbackIndex++;
        } else {
            // Da chay het toan bo hang doi lenh
            commandQueue.clear();
            playbackIndex = 0;
            currentState = State::IDLE;
            Serial.println("[STATE] PLAYING -> IDLE (hoan thanh phat lai toan bo hang doi)");
            return;
        }
    }
    movement.update();
}

static void handleErrorState() {
    // Dong co da duoc dung va bo nho da bi xoa tu enterErrorState().
    // Chi con kiem tra dieu kien thoat: giu OK lien tuc du ERROR_EXIT_HOLD_MS.
    if (analogButton.getButton() == Button::OK &&
        analogButton.getHoldDurationMs() >= ERROR_EXIT_HOLD_MS) {
        currentState = State::IDLE;
        analogButton.clearError();
        Serial.println("[STATE] ERROR -> IDLE (nguoi dung da giu OK du 2 giay)");
    }
}

// ============================================================================
//  SETUP & LOOP
// ============================================================================
void setup() {
    Serial.begin(115200);
    delay(300); // Cho on dinh cong USB-Serial tren mot so board ESP32-C3

    leftMotor.begin();
    rightMotor.begin();
    analogButton.begin();

    commandQueue.reserve(MAX_RECORDED_COMMANDS);

    Serial.println();
    Serial.println("==================================================");
    Serial.println(" XE 3 BANH ESP32-C3 - KHOI DONG HOAN TAT");
    Serial.println(" Trang thai hien tai: IDLE");
    Serial.println("==================================================");
}

void loop() {
    analogButton.update();

    // ---- Kiem tra loi TOAN CUC - ap dung o MOI trang thai, tru khi da o ERROR ----
    if (currentState != State::ERROR && analogButton.isError()) {
        enterErrorState();
        return; // Xu ly tiep tu ERROR o vong lap ke tiep
    }

    switch (currentState) {
        case State::IDLE:    handleIdleState();    break;
        case State::RECORD:  handleRecordState();  break;
        case State::PLAYING: handlePlayingState(); break;
        case State::ERROR:   handleErrorState();   break;
    }
}
