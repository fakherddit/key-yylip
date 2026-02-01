#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include "imgui.h"

// Biến lưu offset gốc
struct OffsetInfo {
    uintptr_t offset;  // offset gốc trong module (không trừ base)
    uintptr_t base;    // base module
};

static std::map<std::string, OffsetInfo> dumpedOffsets;

// Hàm lấy base module
uintptr_t GetModuleBase(const char* moduleName) {
    HMODULE hModule = GetModuleHandleA(moduleName);
    if (!hModule) return 0;
    return (uintptr_t)hModule;
}

// Hàm lấy địa chỉ hàm export (nếu cần, dùng để check)
uintptr_t GetFunctionAddress(HMODULE module, const char* funcName) {
    return (uintptr_t)GetProcAddress(module, funcName);
}

// Hàm dump offset gốc + base
void DumpOffsets() {
    const char* moduleName = "kernel32.dll";

    uintptr_t base = GetModuleBase(moduleName);
    if (!base) {
        std::cout << "Module not found: " << moduleName << "\n";
        return;
    }

    HMODULE hModule = (HMODULE)base;

    // Lấy địa chỉ hàm thực (base + offset gốc)
    uintptr_t createFileAAddr = (uintptr_t)GetProcAddress(hModule, "CreateFileA");
    uintptr_t readFileAddr = (uintptr_t)GetProcAddress(hModule, "ReadFile");

    if (!createFileAAddr || !readFileAddr) {
        std::cout << "Function not found\n";
        return;
    }

    // Tính offset gốc = addr hàm - base module
    uintptr_t createFileAOffset = createFileAAddr - base;
    uintptr_t readFileOffset = readFileAddr - base;

    dumpedOffsets["CreateFileA"] = { createFileAOffset, base };
    dumpedOffsets["ReadFile"] = { readFileOffset, base };

    // Ghi ra file
    std::ofstream out("function_dump.txt");
    for (auto& [name, info] : dumpedOffsets) {
        out << "// Offset gốc: 0x" << std::hex << info.offset << "\n";
        out << "// Base: 0x" << std::hex << info.base << "\n";
        out << "public static void " << name << "() { }\n\n";
    }
    out.close();

    std::cout << "Dump done\n";
}