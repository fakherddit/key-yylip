#ifndef AIMKILL_H
#define AIMKILL_H

#include "Gobal.h"
#include "Vector3.h"
#include "../IMGUI/imgui.h"
#include "vinhtran.hpp"

// Minimal support since logic is now in Hooks.h
class AimKill {
public:
    static AimKill& Get() {
        static AimKill instance;
        return instance;
    }
    void Start(void* LocalPlayer, void* EnemyPlayer);
    void Stop() {}
    void TakeDamage_Req(uintptr_t, uintptr_t, void*, int, int, void*, Vector3, Vector3, void*) {}
};

#endif
