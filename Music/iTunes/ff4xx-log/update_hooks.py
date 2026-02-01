import os

content = r"""#import "vinhtran.hpp"
#import "loading.hxx"
#include <fstream>
#define FMT_HEADER_ONLY
#include "fmt/core.h"
#include <chrono>

extern ImVec4 espv; 
extern ImVec4 espi; 
extern ImVec4 nameColor;
extern ImVec4 distanceColor;
extern bool istelekill;
extern bool isfly;

// New: Helper for offsets
static void Transform_INTERNAL_SetPosition(void *player, Vvector3 inn) {
    void (*_Transform_INTERNAL_SetPosition)(void *transform, Vvector3 in) = (void (*)(void *, Vvector3))getRealOffset(ENCRYPTOFFSET("0x105FE7DB8"));
    _Transform_INTERNAL_SetPosition(player, inn);
}

struct Vars_t
{
    bool UpPlayerOne = false;
    bool Enable = {};
    bool AimbotEnable = {};
    bool Aimbot = {};
    float AimFov = {};
    int AimCheck = {};
    int AimType = {};
    int AimWhen = {};
    bool isAimFov = {};
    int AimHitbox = 0; 
    const char* aimHitboxes[3] = {" Head", " Neck", " Body"};
    const char* dir[4] = { " Automatic", " On Fire", " On Scope", " Fire + Scope" };
    bool lines = {};
    bool Box = {};
    bool Outline = {};
    bool Name = {};
    bool Health = {};
    bool Distance = {};
    bool fovaimglow = {};
    bool circlepos = {};
    bool skeleton = {};
    bool OOF = {};
    bool counts = {};
    ImVec4 boxColor = ImVec4(1.0f, 0.0f, 0.0f, 0.8f);
    float AimSpeed = 9999.0f;
    bool VisibleCheck = false;
    bool IgnoreKnocked = false;
    bool AimOnFire = false;
    bool AimOnScope = false;
    bool magicBullet = false;
    bool AimKill = false;
    bool AimKillFast = false;
    bool WallhackGlow = false;
    bool Bypass = true;
    bool Ghost = false;
    bool AutoAim = false; // Legacy/Compat
} Vars; 

class game_sdk_t
{
public:
    void init();
    int (*GetHp)(void *player);
    void *(*Curent_Match)();
    void *(*GetLocalPlayer)(void *Game);
    void *(*GetHeadPositions)(void *player);
    Vector3 (*get_position)(void *player);
    void *(*Component_GetTransform)(void *player);
    void *(*get_camera)();
    Vector3 (*WorldToScreenPoint)(void *, Vector3);
    bool (*get_isVisible)(void *player);
    bool (*get_isLocalTeam)(void *player);
    bool (*get_IsDieing)(void *player);
    int (*get_MaxHP)(void *player);
    Vector3 (*GetForward)(void *player);
    void (*set_aim)(void *player, Quaternion look);
    bool (*get_IsSighting)(void *player);
    bool (*get_IsFiring)(void *player);
    monoString *(*name)(void *player);
    void *(*_GetHeadPositions)(void *);
    void *(*_newHipMods)(void *);
    void *(*_GetLeftAnkleTF)(void *);
    void *(*_GetRightAnkleTF)(void *);
    void *(*_GetLeftToeTF)(void *);
    void *(*_GetRightToeTF)(void *);
    void *(*_getLeftHandTF)(void *);
    void *(*_getRightHandTF)(void *);
    void *(*_getLeftForeArmTF)(void *);
    void *(*_getRightForeArmTF)(void *);
};

game_sdk_t *game_sdk = new game_sdk_t();

void game_sdk_t::init()
{
    this->GetHp = (int (*)(void*))getRealOffset(oxo("0x1051AAF78"));
    this->Curent_Match = (void* (*)())getRealOffset(oxo("0x101283110"));
    this->GetLocalPlayer = (void* (*)(void*))getRealOffset(oxo("0x103FF6CD4"));
    this->GetHeadPositions = (void* (*)(void*))getRealOffset(oxo("0x1051C5228"));
    this->get_position = (Vector3(*)(void*))getRealOffset(oxo("0x105FE7CE4"));
    this->Component_GetTransform = (void* (*)(void*))getRealOffset(oxo("0x105F9CC54"));
    this->get_camera = (void* (*)())getRealOffset(oxo("0x105F9A79C"));
    this->WorldToScreenPoint = (Vector3(*)(void*, Vector3))getRealOffset(oxo("0x105F9A154"));
    this->get_isVisible = (bool (*)(void*))getRealOffset(oxo("0x10514A22C"));
    this->get_isLocalTeam = (bool (*)(void*))getRealOffset(oxo("0x10515FFFC"));
    this->get_IsDieing = (bool (*)(void*))getRealOffset(oxo("0x105133838"));
    this->get_MaxHP = (int (*)(void*))getRealOffset(oxo("0x1051AB020"));
    this->GetForward = (Vector3(*)(void*))getRealOffset(oxo("0x105FE8694"));
    this->set_aim = (void (*)(void*, Quaternion))getRealOffset(oxo("0x1051468F0"));
    this->get_IsSighting = (bool (*)(void*))getRealOffset(oxo("0x10513AA94"));
    this->get_IsFiring = (bool (*)(void*))getRealOffset(oxo("0x105135E20"));
    this->name = (monoString * (*)(void* player)) getRealOffset(oxo("0x105141C3C"));
    
    this->_GetHeadPositions = (void* (*)(void*))getRealOffset(oxo("0x1051C5228"));
    this->_newHipMods = (void* (*)(void*))getRealOffset(oxo("0x1051C5378"));
    this->_GetLeftAnkleTF = (void* (*)(void*))getRealOffset(oxo("0x1051C56AC"));
    this->_GetRightAnkleTF = (void* (*)(void*))getRealOffset(oxo("0x1051C5750"));
    this->_GetLeftToeTF = (void* (*)(void*))getRealOffset(oxo("0x1051C57F4"));
    this->_GetRightToeTF = (void* (*)(void*))getRealOffset(oxo("0x1051C5898"));
    this->_getLeftHandTF = (void* (*)(void*))getRealOffset(oxo("0x105145BD0"));
    this->_getRightHandTF = (void* (*)(void*))getRealOffset(oxo("0x105145C7C"));
    this->_getLeftForeArmTF = (void* (*)(void*))getRealOffset(oxo("0x105145D20"));
    this->_getRightForeArmTF = (void* (*)(void*))getRealOffset(oxo("0x105145DC4"));
}

namespace Camera$$WorldToScreen {
    ImVec2 Regular(Vector3 pos) {
        auto cam = game_sdk->get_camera();
        if (!cam) return {0, 0};
        Vector3 worldPoint = game_sdk->WorldToScreenPoint(cam, pos);
        Vector3 location;
        int ScreenWidth = ImGui::GetIO().DisplaySize.x;
        int ScreenHeight = ImGui::GetIO().DisplaySize.y;
        location.x = ScreenWidth * worldPoint.x;
        location.y = ScreenHeight - worldPoint.y * ScreenHeight;
        location.z = worldPoint.z;
        return {location.x, location.y};
    }

    ImVec2 Checker(Vector3 pos, bool &checker) {
        auto cam = game_sdk->get_camera();
        if (!cam) return {0, 0};
        Vector3 worldPoint = game_sdk->WorldToScreenPoint(cam, pos);
        Vector3 location;
        int ScreenWidth = ImGui::GetIO().DisplaySize.x;
        int ScreenHeight = ImGui::GetIO().DisplaySize.y;
        location.x = ScreenWidth * worldPoint.x;
        location.y = ScreenHeight - worldPoint.y * ScreenHeight;
        location.z = worldPoint.z;
        checker = location.z > 1;
        return {location.x, location.y};
    }
}

Vector3 GetBonePosition(void *player, void *(*transformGetter)(void *)) {
    if (!player || !transformGetter) return Vector3();
    void *transform = transformGetter(player);
    return transform ? game_sdk->get_position(game_sdk->Component_GetTransform(transform)) : Vector3();
}

Vector3 GetHitboxPosition(void* player, int hitbox) {
    if (!player) return Vector3::zero();
    switch (hitbox) {
        case 0: return GetBonePosition(player, game_sdk->_GetHeadPositions);
        case 1: {
            Vector3 headPos = GetBonePosition(player, game_sdk->_GetHeadPositions);
            return headPos == Vector3::zero() ? headPos : Vector3(headPos.x, headPos.y - 0.05f, headPos.z);
        }
        case 2: {
            Vector3 headPos = GetBonePosition(player, game_sdk->_GetHeadPositions);
            return headPos == Vector3::zero() ? headPos : Vector3(headPos.x, headPos.y - 0.2f, headPos.z);
        }
        default: return GetBonePosition(player, game_sdk->_GetHeadPositions);
    }
}

Vector3 getPosition(void *player) {
    return game_sdk->get_position(game_sdk->Component_GetTransform(player));
}

static Vector3 GetHeadPosition(void *player) {
    return game_sdk->get_position(game_sdk->GetHeadPositions(player));
}

static Vector3 CameraMain(void *player) {
    return game_sdk->get_position(*(void **)((uint64_t)player + oxo("0x318")));
}

Quaternion GetRotationToTheLocation(Vector3 Target, float Height, Vector3 MyEnemy) {
    Vector3 direction = (Target + Vector3(0, Height, 0)) - MyEnemy;
    return Quaternion::LookRotation(direction, Vector3(0, 1, 0));
}

Quaternion GetCurrentRotation(void* player) {
    void* transform = game_sdk->Component_GetTransform(player);
    if (!transform) return Quaternion();
    return Quaternion::LookRotation(game_sdk->GetForward(transform), Vector3(0, 1, 0));
}

#include "Helper/Ext.h"

class tanghinh {
public:
    static Vector3 Transform_GetPosition(void *player) {
        Vector3 out = Vector3::zero();
        void (*_Transform_GetPosition)(void *transform, Vector3 *out) = (void (*)(void *, Vector3 *))getRealOffset(oxo("0x105FE7D14"));
        _Transform_GetPosition(player, &out);
        return out;
    }

    static void *Player_GetHeadCollider(void *player) {
        void *(*_Player_GetHeadCollider)(void *players) = (void *(*)(void *))getRealOffset(oxo("0x105144E64"));
        return _Player_GetHeadCollider(player);
    }

    static bool Physics_Raycast(Vector3 camLocation, Vector3 headLocation, unsigned int LayerID, void *collider) {
        bool (*_Physics_Raycast)(Vector3 camLocation, Vector3 headLocation, unsigned int LayerID, void *collider) = (bool (*)(Vector3, Vector3, unsigned int, void *))getRealOffset(oxo("0x1046F7568"));
        return _Physics_Raycast(camLocation, headLocation, LayerID, collider);
    }

    static bool isVisible(void *enemy) {
        if (enemy != NULL) {
            void *hitObj = NULL;
            auto Camera = Transform_GetPosition(game_sdk->Component_GetTransform(game_sdk->get_camera()));
            auto Target = Transform_GetPosition(game_sdk->Component_GetTransform(Player_GetHeadCollider(enemy)));
            return !Physics_Raycast(Camera, Target, 12, &hitObj);
        }
        return false;
    }
};

void DrawLine(ImDrawList* drawList, ImVec2 start, ImVec2 end, float thickness, bool isDead = false, bool isVisible = false) {
    if (!drawList) return;
    ImColor color = isDead ? ImColor(espi) : isVisible ? ImColor(espv) : ImColor(espi);
    drawList->AddLine(start, end, color, thickness);
}

void DrawHealthBar(ImDrawList* drawList, ImVec2 start, ImVec2 end, float healthMultiplier, float thickness, bool isDead = false) {
    if (!drawList) return;
    float totalHeight = end.y - start.y;
    float healthHeight = totalHeight * healthMultiplier;
    drawList->AddRectFilled(ImVec2(start.x - thickness/2, start.y), ImVec2(start.x + thickness/2, end.y), ImColor(50, 50, 50, 200));
    if (healthMultiplier > 0) {
        ImColor color = isDead ? ImColor(255, 0, 0) : ImColor(0, 255, 0);
        drawList->AddRectFilled(ImVec2(start.x - thickness/2, end.y - healthHeight), ImVec2(start.x + thickness/2, end.y), color);
    }
    if (Vars.Outline) {
        drawList->AddRect(ImVec2(start.x - thickness/2 - 1, start.y - 1), ImVec2(start.x + thickness/2 + 1, end.y + 1), ImColor(0, 255, 0));
    }
}

void DrawSkeleton(void *player, ImDrawList *drawList) {
    if (!player || !drawList) return;
    bool isPlayerVisible = tanghinh::isVisible(player);
    bool isPlayerDead = game_sdk->get_IsDieing(player);
    
    Vector3 headPos = GetBonePosition(player, game_sdk->_GetHeadPositions);
    Vector3 hipPos = GetBonePosition(player, game_sdk->_newHipMods);
    Vector3 leftAnklePos = GetBonePosition(player, game_sdk->_GetLeftAnkleTF);
    Vector3 rightAnklePos = GetBonePosition(player, game_sdk->_GetRightAnkleTF);
    Vector3 leftToePos = GetBonePosition(player, game_sdk->_GetLeftToeTF);
    Vector3 rightToePos = GetBonePosition(player, game_sdk->_GetRightToeTF);
    Vector3 leftHandPos = GetBonePosition(player, game_sdk->_getLeftHandTF);
    Vector3 rightHandPos = GetBonePosition(player, game_sdk->_getRightHandTF);
    Vector3 leftForeArmPos = GetBonePosition(player, game_sdk->_getLeftForeArmTF);
    Vector3 rightForeArmPos = GetBonePosition(player, game_sdk->_getRightForeArmTF);
    bool visible;
    ImVec2 headScreen = Camera$$WorldToScreen::Checker(headPos, visible);
    if (!visible) return;
    ImVec2 hipScreen = Camera$$WorldToScreen::Regular(hipPos);
    ImVec2 leftAnkleScreen = Camera$$WorldToScreen::Regular(leftAnklePos);
    ImVec2 rightAnkleScreen = Camera$$WorldToScreen::Regular(rightAnklePos);
    ImVec2 leftToeScreen = Camera$$WorldToScreen::Regular(leftToePos);
    ImVec2 rightToeScreen = Camera$$WorldToScreen::Regular(rightToePos);
    ImVec2 leftHandScreen = Camera$$WorldToScreen::Regular(leftHandPos);
    ImVec2 rightHandScreen = Camera$$WorldToScreen::Regular(rightHandPos);
    ImVec2 leftForeArmScreen = Camera$$WorldToScreen::Regular(leftForeArmPos);
    ImVec2 rightForeArmScreen = Camera$$WorldToScreen::Regular(rightForeArmPos);
    float thickness = 1.0f;
    ImColor color = isPlayerDead ? ImColor(espi) : isPlayerVisible ? ImColor(espv) : ImColor(espi);

    drawList->AddCircle(headScreen, 2.0f, color, 12, thickness);
    drawList->AddLine(headScreen, hipScreen, color, thickness);
    drawList->AddLine(headScreen, leftForeArmScreen, color, thickness);
    drawList->AddLine(headScreen, rightForeArmScreen, color, thickness);
    drawList->AddLine(leftForeArmScreen, leftHandScreen, color, thickness);
    drawList->AddLine(rightForeArmScreen, rightHandScreen, color, thickness);
    drawList->AddLine(hipScreen, leftAnkleScreen, color, thickness);
    drawList->AddLine(hipScreen, rightAnkleScreen, color, thickness);
    drawList->AddLine(leftAnkleScreen, leftToeScreen, color, thickness);
    drawList->AddLine(rightAnkleScreen, rightToeScreen, color, thickness);
}

bool isFov(Vector3 vec1, Vector3 vec2, int radius) {
    float dx = vec1.x - vec2.x;
    float dy = vec1.y - vec2.y;
    return (dx * dx + dy * dy) <= (radius * radius);
}

void *GetClosestEnemy() {
    try {
        float shortestDistance = 250.0f;
        void *closestEnemy = NULL;
        void *get_MatchGame = game_sdk->Curent_Match();
        if (!get_MatchGame) return NULL;
        void *LocalPlayer = game_sdk->GetLocalPlayer(get_MatchGame);
        if (!LocalPlayer || !game_sdk->Component_GetTransform(LocalPlayer)) return NULL;
        if (!Vars.Aimbot && !Vars.Enable) return NULL;
        Dictionary<uint8_t *, void **> *players = *(Dictionary<uint8_t *, void **> **)((long)get_MatchGame + oxo("0x120"));
        if (!players || !players->getValues()) return NULL;

        Vector3 LocalPlayerPos = getPosition(LocalPlayer);
        ImVec2 center = ImVec2(ImGui::GetIO().DisplaySize.x / 2, ImGui::GetIO().DisplaySize.y / 2);

        for (int u = 0; u < players->getNumValues(); u++) {
            void *Player = players->getValues()[u];
            if (!Player || Player == LocalPlayer || !game_sdk->get_MaxHP(Player) || game_sdk->get_isLocalTeam(Player)) continue;
            if ((Vars.IgnoreKnocked && game_sdk->get_IsDieing(Player)) || game_sdk->GetHp(Player) <= 0) continue;
            if (Vars.VisibleCheck && !tanghinh::isVisible(Player)) continue;

            Vector3 PlayerPos = GetHitboxPosition(Player, Vars.AimHitbox);
            float distance = Vector3::Distance(LocalPlayerPos, PlayerPos);
            if (distance >= 300) continue;

            ImVec2 enemyScreenPos = Camera$$WorldToScreen::Regular(PlayerPos);
            if (isFov(Vector3(enemyScreenPos.x, enemyScreenPos.y, 0), Vector3(center.x, center.y, 0), Vars.AimFov) && distance < shortestDistance) {
                shortestDistance = distance;
                closestEnemy = Player;
            }
        }
        return closestEnemy;
    } catch (...) { return NULL; }
}

// --- AIM KILL LOGIC (Ported) ---
namespace Save {
    void* DamageInfo;
    clock_t AimDelay;
    int AimFPS = (1000000 / 50); // 50 Hits/Sec
}
bool SowDamage = false; 
bool autochangeweapon = false;
bool POFFNNMOOBM = false;
int GDKLMFLNNGM = 0;

struct COW_GamePlay_IHAAMHPPLMG_o {
    uint32_t NBPDJAAAFBH;
    uint32_t JEDDPHIHGKL;
    uint8_t IOICFFEKAIL;
    uint8_t PHAFNFOFFDB;
    uint64_t BNFAIDHEHOM;
};

COW_GamePlay_IHAAMHPPLMG_o GetplayerID(void *_this) {   
    return ((COW_GamePlay_IHAAMHPPLMG_o (*)(void *))getRealOffset(oxo("0x10511E8A4")))(_this);
}

static void *GetWeaponOnHand1(void *local) {
    void *(*_GetWeaponOnHand1)(void *local) = (void *(*)(void *))getRealOffset(oxo("0x1051414FC"));
    return _GetWeaponOnHand1(local);
}

static int GetWeapon(void* enemy) {
    int (*GetWeapon)(void *player) = (int(*)(void *))getRealOffset(oxo("0x104B2F198"));
    return GetWeapon(enemy);
}

static int GetDamage(void *pthis) {
    return ((int (*)(void *))getRealOffset(oxo("0x10387F3AC")))(pthis);
}

void *get_HeadCollider(void *pthis) {
    return ((void* (*)(void *))getRealOffset(oxo("0x105144E64")))(pthis);
}

void *get_gameObject(void *Pthis) {
    return ((void* (*)(void *))getRealOffset(oxo("0x105F9CCC0")))(Pthis);
}

void *GKHECDLGAJA(void *pthis, void* a1) {
    return ((void* (*)(void *,void *))getRealOffset(oxo("0x1051A8600")))(pthis,a1);
}

monoList<float *> *LCLHHHKFCFP(void *Weapon,void *CAGCICACKCF,void *HFBDJJDICLN,bool LDGHPOPPPNL,void* DamageInfo) {
    return ((monoList<float *> * (*)(void*,void*,void*,bool,void*))getRealOffset(oxo("0x1038A86B0")))(Weapon,CAGCICACKCF,HFBDJJDICLN,LDGHPOPPPNL,DamageInfo);
}

void StartWholeBodyFiring(void* player,void* WeaponOnHand) {
    void(*StartWholeBodyFiring)(void*,void*) = (void(*)(void*,void*))getRealOffset(oxo("0x105304B44"));
    return StartWholeBodyFiring(player,WeaponOnHand);   
}

static void StartFiring(void *Player, void *WeaponOnHand) {
    void (*_StartFiring)(void *, void *) = (void (*)(void *, void *))getRealOffset(oxo("0x1053045C0"));
    return _StartFiring(Player, WeaponOnHand);
}

static void StopFire1(void* Player,void* WeaponOnHand) {
    void(*_StopFire1)(void*,void*) = (void(*)(void*,void*))getRealOffset(oxo("0x1052DAF9C"));
    _StopFire1(Player, WeaponOnHand);
}

static int32_t TakeDamage(void *_this, int32_t KOCMLPLOILD, COW_GamePlay_IHAAMHPPLMG_o HLJDHPGGODB, void* JIIJIFKKCCB, int32_t BOEIBGAABDL, Vector3 NJMFBKNHMBP, Vector3 DOBOBMFMKBJ, monoList<float *> *NBKBEBFNDBE, void* damagerWeaponDynamicInfo, uint32_t damagerVehicleID) {
    return ((int32_t (*)(void*, int32_t, COW_GamePlay_IHAAMHPPLMG_o, void*, int32_t, Vector3, Vector3, monoList<float *> *, void*, uint32_t))getRealOffset(oxo("0x1052D91EC")))(_this, KOCMLPLOILD, HLJDHPGGODB, JIIJIFKKCCB, BOEIBGAABDL, NJMFBKNHMBP, DOBOBMFMKBJ, NBKBEBFNDBE, damagerWeaponDynamicInfo, damagerVehicleID);
}

static void SwapWeapon(void *player, int POFFNNMOOBM, bool GDKLMFLNNGM) {
    void (*_SwapWeapon)(void *player, int POFFNNMOOBM, bool GDKLMFLNNGM) = (void (*)(void *, int, bool))getRealOffset(oxo("0x1053051BC"));
    _SwapWeapon(player, POFFNNMOOBM, GDKLMFLNNGM);      
}

void PlayerTakeDamage(void* ClosestEnemy) {
    if (ClosestEnemy != nullptr && game_sdk->get_isVisible(ClosestEnemy) && clock() > Save::AimDelay) {
        Save::AimDelay = clock() + Save::AimFPS;
        void* match = game_sdk->Curent_Match();
        if (!match) return;
        void* LocalPlayer = game_sdk->GetLocalPlayer(match);
        if (LocalPlayer != NULL) {
            void* WeaponHand = GetWeaponOnHand1(LocalPlayer);
            if (WeaponHand == nullptr) return;
            void* HitInfo = *(void**)((uintptr_t)LocalPlayer + 0x9F0);
            if (HitInfo == nullptr) return;
            auto PlayerID2 = GetplayerID(LocalPlayer);
            auto baseDamage = GetDamage(WeaponHand);
            int WeaponID = GetWeapon(WeaponHand);
            Vector3 localLocation = GetHitboxPosition(LocalPlayer, 0);
            Vector3 enemyLocation = GetHitboxPosition(ClosestEnemy, 0);
            void* damagerWeaponDynamicInfo = reinterpret_cast<void*>(getRealOffset(oxo("0x104F16C30")));
            void *damagerDynamicInfo = (!SowDamage) ? damagerWeaponDynamicInfo : nullptr;
            if (WeaponID == -1 || baseDamage == 0) return;
            void* PlayerAttributes = *(void**)((uint64_t)LocalPlayer + 0x680);
            if (!PlayerAttributes) return;
            void* DamageModule = *(void**)((uint64_t)PlayerAttributes + 0x2A0);
            if (!DamageModule) return;
            void* DamageInfo = *(void**)((uint64_t)DamageModule + 0x10);
            if (!DamageInfo) return;
            *(int*)((char*)DamageInfo + 0x14) = 1;
            *(void**)((char*)DamageInfo + 0x40) = WeaponHand;
            *(int*)((char*)DamageInfo + 0x10) = baseDamage;
            *(COW_GamePlay_IHAAMHPPLMG_o*)((char*)DamageInfo + 0x28) = PlayerID2;
            void* headCollider = get_HeadCollider(ClosestEnemy);
            if (headCollider == nullptr) return;
            void* hitGameObject = get_gameObject(headCollider);
            if (hitGameObject == nullptr) return;
            *(void**)((char*)HitInfo + 0x18) = hitGameObject;
            *(void**)((char*)HitInfo + 0x20) = headCollider;
            *(Vector3*)((char*)HitInfo + 0x30) = enemyLocation;
            *(int*)((char*)HitInfo + 0x64) = 1;
            auto targetPosition = GKHECDLGAJA(LocalPlayer, HitInfo);
            if (targetPosition == nullptr) return;
            monoList<float*>* CheckParametros = LCLHHHKFCFP(WeaponHand, targetPosition, headCollider, false, DamageInfo);
            if (CheckParametros == nullptr) return;
            StartWholeBodyFiring(LocalPlayer, WeaponHand);
            TakeDamage(ClosestEnemy, baseDamage, PlayerID2, DamageInfo, WeaponID, localLocation, enemyLocation, CheckParametros, damagerDynamicInfo, 0);
            StartFiring(LocalPlayer, WeaponHand);
            StopFire1(LocalPlayer, WeaponHand);
            GDKLMFLNNGM++;
            if (GDKLMFLNNGM > 0 && (autochangeweapon || Vars.AimKillFast)) {
                POFFNNMOOBM = !POFFNNMOOBM;
                SwapWeapon(LocalPlayer, POFFNNMOOBM, false);
                GDKLMFLNNGM = 0;
            }
        }
    }
}

void ProcessAimKill(void* local, void* enemy) {
    if (!local || !enemy) return;
    void* localTF = game_sdk->Component_GetTransform(local);
    void* enemyTF = game_sdk->Component_GetTransform(enemy);
    if (!localTF || !enemyTF) return;
    Vector3 localPos = game_sdk->get_position(localTF);
    Vector3 forward = game_sdk->GetForward(localTF);
    Vector3 targetPos = localPos + (forward * 8.0f);
    targetPos.y = localPos.y;
    Transform_INTERNAL_SetPosition(enemyTF, Vvector3(targetPos.x, targetPos.y, targetPos.z));
}

void UpOneEnemy() {
    if (!Vars.Enable || !Vars.UpPlayerOne) return;
    void *match = game_sdk->Curent_Match();
    if (!match) return;
    void *local = game_sdk->GetLocalPlayer(match);
    if (!local || !game_sdk->Component_GetTransform(local)) return;
    Dictionary<uint8_t *, void **> *players = *(Dictionary<uint8_t *, void **> **)((long)match + 0x120);
    if (!players || !players->getValues()) return;

    for (int i = 0; i < players->getNumValues(); i++) {
        void *enemy = players->getValues()[i];
        if (!enemy || enemy == local) continue;
        if (!game_sdk->Component_GetTransform(enemy)) continue;
        if (!game_sdk->get_MaxHP(enemy)) continue;
        if (game_sdk->get_IsDieing(enemy)) continue;
        if (game_sdk->GetHp(enemy) <= 0) continue;
        if (game_sdk->get_isLocalTeam(enemy)) continue;

        void *enemyTF = game_sdk->Component_GetTransform(enemy);
        void *localTF = game_sdk->Component_GetTransform(local);
        if (!enemyTF || !localTF) continue;

        Vector3 enemyPos = game_sdk->get_position(enemyTF);
        Vector3 localPos = game_sdk->get_position(localTF);
        float distance = Vector3::Distance(localPos, enemyPos);
        if (distance <= 10.0f) continue;
        float groundY = enemyPos.y;
        float targetY = groundY + 5.7f;
        float step = 0.35f;
        if (enemyPos.y < targetY - 0.1f) enemyPos.y += step;
        else if (enemyPos.y > targetY + 0.1f) enemyPos.y -= step;
        Transform_INTERNAL_SetPosition(enemyTF, Vvector3(enemyPos.x, enemyPos.y, enemyPos.z));
    }
}

void ProcessAimbot() {
    if (!Vars.Aimbot) return;
    void *CurrentMatch = game_sdk->Curent_Match();
    if (!CurrentMatch) return;
    void *LocalPlayer = game_sdk->GetLocalPlayer(CurrentMatch);
    if (!LocalPlayer || !game_sdk->Component_GetTransform(LocalPlayer)) return;
    
    // Auto-Aim Logic
    void *closestEnemy = GetClosestEnemy();
    if (!closestEnemy || !game_sdk->Component_GetTransform(closestEnemy)) return;

    Vector3 EnemyLocation = GetHitboxPosition(closestEnemy, Vars.AimHitbox);
    if (EnemyLocation == Vector3::zero()) return;
    Vector3 PlayerLocation = CameraMain(LocalPlayer);
    if (PlayerLocation == Vector3::zero()) return;

    bool IsScopeOn = game_sdk->get_IsSighting(LocalPlayer);
    bool IsFiring = game_sdk->get_IsFiring(LocalPlayer);
    bool shouldAim = (Vars.AimWhen == 0) || (Vars.AimWhen == 1 && IsFiring) || (Vars.AimWhen == 2 && IsScopeOn) || (Vars.AimWhen == 3 && (IsFiring || IsScopeOn));
    if (Vars.AutoAim) shouldAim = true;
    if (Vars.AimKillFast) shouldAim = true;

    if (shouldAim && (!Vars.VisibleCheck || tanghinh::isVisible(closestEnemy))) {
        float smooth = 0.05f;
        if (Vars.AimKillFast || Vars.AimKillFire) smooth = 1.0f;
        Quaternion TargetLook = GetRotationToTheLocation(EnemyLocation, smooth, PlayerLocation);
        
        bool isFacingTarget = true;
        if (Vars.AimKill || Vars.AimKillFast) {
            ImVec2 center = ImVec2(ImGui::GetIO().DisplaySize.x / 2.0f, ImGui::GetIO().DisplaySize.y / 2.0f);
            ImVec2 enemyScreenPos = Camera$$WorldToScreen::Regular(EnemyLocation);
            float distToCenter = sqrt(pow(enemyScreenPos.x - center.x, 2) + pow(enemyScreenPos.y - center.y, 2));
            if (distToCenter > 130.0f) isFacingTarget = false;
        }

        if (isFacingTarget) {
             game_sdk->set_aim(LocalPlayer, TargetLook);
             if ((Vars.AimKill || Vars.AimKillFast) && Vars.Aimbot) {
                 PlayerTakeDamage(closestEnemy);
             }
        }
        if (Vars.magicBullet && Vars.Aimbot && !isFacingTarget) {
             PlayerTakeDamage(closestEnemy);
        }
    }
}

void get_players() {
    ImDrawList *draw_list = ImGui::GetBackgroundDrawList();
    int numberOfPlayersAround = 0;
    if (!draw_list) return;
    if (!Vars.Enable) return;
    try {
        if (Vars.Aimbot) ProcessAimbot();
        if (Vars.UpPlayerOne) UpOneEnemy();

        void *current_Match = game_sdk->Curent_Match();
        if (!current_Match) return;
        void *local_player = game_sdk->GetLocalPlayer(current_Match);
        if (!local_player) return;
        Dictionary<uint8_t *, void **> *players = *(Dictionary<uint8_t *, void **> **)((long)current_Match + 0x120);
        if (!players || !players->getValues()) return;

        for (int u = 0; u < players->getNumValues(); u++) {
            void *closestEnemy = players->getValues()[u];
            if (!closestEnemy || !game_sdk->Component_GetTransform(closestEnemy) || closestEnemy == local_player || !game_sdk->get_MaxHP(closestEnemy) || game_sdk->get_isLocalTeam(closestEnemy)) continue;
            numberOfPlayersAround++;
            Vector3 pos = getPosition(closestEnemy);
            Vector3 pos2 = getPosition(local_player);
            float distance = Vector3::Distance(pos, pos2);
            if (distance > 200.0f) continue;
            bool isEnemyDead = game_sdk->get_IsDieing(closestEnemy);
            bool isEnemyVisible = tanghinh::isVisible(closestEnemy);

            bool w2sc;
            ImVec2 top_pos = Camera$$WorldToScreen::Regular(pos + Vector3(0, 1.6, 0));
            ImVec2 bot_pos = Camera$$WorldToScreen::Regular(pos);
            ImVec2 pos_3 = Camera$$WorldToScreen::Checker(pos, w2sc);
            
            float height = bot_pos.y - top_pos.y;
            float width = height * 0.5f;

            ImRect rect(ImVec2(top_pos.x - width/2, top_pos.y), ImVec2(top_pos.x + width/2, bot_pos.y));

            if (w2sc) {
                if (Vars.lines) DrawLine(draw_list, ImVec2(ImGui::GetIO().DisplaySize.x / 2, 15), ImVec2(rect.GetCenter().x, rect.Min.y), 1.0f, isEnemyDead, isEnemyVisible);
                if (Vars.Box) {
                    DrawLine(draw_list, rect.Min, ImVec2(rect.Max.x, rect.Min.y), 1.0f, isEnemyDead, isEnemyVisible);
                    DrawLine(draw_list, ImVec2(rect.Max.x, rect.Min.y), rect.Max, 1.0f, isEnemyDead, isEnemyVisible);
                    DrawLine(draw_list, ImVec2(rect.Min.x, rect.Max.y), rect.Min, 1.0f, isEnemyDead, isEnemyVisible);
                    DrawLine(draw_list, ImVec2(rect.Min.x, rect.Max.y), rect.Min, 1.0f, isEnemyDead, isEnemyVisible);
                }
                if (Vars.Health) {
                     float health = (float)game_sdk->GetHp(closestEnemy) / (float)game_sdk->get_MaxHP(closestEnemy);
                     DrawHealthBar(draw_list, ImVec2(rect.Min.x - 4, rect.Min.y), ImVec2(rect.Min.x - 2, rect.Max.y), health, 2.0f, isEnemyDead);
                }
                if (Vars.Name) {
                    auto pname = game_sdk->name(closestEnemy);
                    if (pname) {
                        std::string name = pname->toCPPString();
                        draw_list->AddText(ImVec2(rect.GetCenter().x - 10, rect.Min.y - 15), nameColor, name.c_str());
                    }
                }
                if (Vars.Distance) {
                    std::string dist = fmt::format("{}M", (int)distance);
                    draw_list->AddText(ImVec2(rect.Max.x + 2, rect.Min.y), distanceColor, dist.c_str());
                }
                if (Vars.skeleton) DrawSkeleton(closestEnemy, draw_list);
            }
        }
    } catch (...) {}
}

void RunTelekill() {
    if (!istelekill) return;
    void *local = game_sdk->GetLocalPlayer(game_sdk->Curent_Match());
    if (!local) return;
    ProcessAimKill(local, GetClosestEnemy());
}

void aimbot() {
    ProcessAimbot();
}
"""

file_path = os.path.join(os.getcwd(), 'Helper', 'Hooks.h')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
