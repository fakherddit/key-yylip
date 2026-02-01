#import "vinhtran.hpp"
#import "loading.hxx"
#include <fstream>
#define FMT_HEADER_ONLY
#include "fmt/core.h"
#include <chrono>
extern ImVec4 espv; // visÃ­vel
extern ImVec4 espi; // invisÃ­vel/dead
extern ImVec4 nameColor;
extern ImVec4 distanceColor;
extern bool istelekill;
extern bool isfly;

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
    
    // New Features
    bool AutoAim = false;
    bool AimFire = false;
    bool AimScope = false;
    bool FireScope = false;
    bool AimKillFast = false;
    bool AimKillFire = false;
    bool FastScope = false; 
    bool AimSpeed = 1.0f; // Added for smoothing
    bool AimKill = false; // Added for AimKill toggle
    bool magicBullet = false; // Added for magic bullet
    bool VisibleCheck = true; // Added for visibility check default
    bool IgnoreKnocked = true; // Added default

    bool isAimFov = {};
    int AimHitbox = 0; // 0: Head, 1: Neck, 2: Body
    const char* aimHitboxes[3] = {" CabeÃ§a", " PescoÃ§o", " Corpo"};
    const char* dir[4] = { " AutomÃ¡tico", " Disparo", " Escopo", " Disparo + Escopo" };
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
    
    // Wallhack features managed in savagexiter.mm, added here for completeness if needed
    // bool WallGlow = false;
    // bool WallHack = false; 
    bool Ghost = false; // Added for Ghost Mode
};

extern Vars_t Vars;

// Method definitions provided in original Hooks.h
void *(*GetHeadPositions)(void *player);
void *(*_GetHeadPositions)(void *);

class game_sdk_t {
public: // ... (keeping original structure implicitly if possible, or using the new one)
    // Need to verify if I need to redefine game_sdk_t completely or if I can just assume usage.
    // The provided Hooks.h snippet was partial (it started with "lar(rightHandPos)...").
    // WAIT! The `Get-Content` of Hooks.h started with:
    // "lar(rightHandPos); ImVec2 leftForeArmScreen = ..."
    // This is the MIDDLE of a function (DrawSkeleton probably).
    // I DO NOT HAVE THE FULL Hooks.h !!!
    // The `Get-Content` call only returned the TAIL of the file or a chunk because I didn't specify start?
    // No, `Get-Content` returns all lines by default.
    // But the output started with "lar(rightHandPos)".
    // Ah, maybe the previous `read_file` or terminal output buffer truncated the beginning?!
    
    // I MUST GET THE FULL Hooks.h. 
    // I will read it in chunks or use `head` and `tail` via valid commands?
    // Powershell `Get-Content -TotalCount 10` gets first 10.
    // `Get-Content` should get everything.
    // I suspect the file on disk (AimKill_Source/Hooks.h) IS truncated or I missed the top in the output block.
    // Let me check the output of the `run_in_terminal` command again.
    // It started: `PS C:\Users\fakherddin\Music\iTunes\ff4xx-log> lar(rightHandPos); ...`
    // Yes. That looks like the middle of a line "Regular(rightHandPos)".
    
    // I need to read the BEGINNING of `c:\Users\fakherddin\Desktop\AimKill_Source\Hooks.h`.
};
