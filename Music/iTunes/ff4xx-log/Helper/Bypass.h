#pragma once
#include <vector>
#include <string>
#include <mach/mach.h>
#include "Mem.h"

struct PatchData {
    uint64_t offset;
    const char* hexCode;
};

// ERZO X BOLT Offsets
PatchData bypassPatches[] = {
    {0x4947BF0, "200080D2C0035FD6"},
    {0x2E2ABAC, "C0035FD6"},
    {0x52C03D4, "00D0201EC0035FD6"},
    {0x51627A8, "40008052C0035FD6"},
    {0x388082C, "00F0271EC0035FD6"},
    {0x506AFD4, "C0035FD6"},
    {0x3109E74, "C0035FD6"},
    {0x3109E7C, "C0035FD6"},
    {0x3107658, "C0035FD6"},
    {0x3107660, "C0035FD6"},
    {0x31074B8, "C0035FD6"},
    {0x31074C0, "0035FD69"}, 
    {0x310A9D4, "C0035FD6"},
    {0x4BDE6E8, "C0035FD6"},
    {0x4AFCF04, "C0035FD6"},
    {0x4AFCB6C, "C0035FD6"},
    {0xA19A74, "C0035FD6"},
    {0xA097D4, "C0035FD6"},
    {0x4E6C010, "C0035FD6"},
    {0x30FA8BC, "C0035FD6"},
    {0x4B757E4, "C0035FD6"},
    {0x480747C, "C0035FD6"},
    {0x48074D4, "C0035FD6"},
    {0x4807078, "C0035FD6"},
    {0x4807558, "C0035FD6"},
    {0x48057B8, "C0035FD6"},
    {0x48067E8, "C0035FD6"},
    {0x4807608, "C0035FD6"},
    {0x2FE0A60, "C0035FD6"},
    {0x48059D4, "C0035FD6"},
    {0x4807D28, "C0035FD6"},
    {0x4805AB0, "C0035FD6"},
    {0x4805B8C, "C0035FD6"},
    {0x4805FE8, "C0035FD6"},
    {0x4805EE4, "C0035FD6"},
    {0x4806110, "C0035FD6"},
    {0x4802FC8, "C0035FD6"},
    {0x4803624, "000080D2"},
    {0x4803800, "C0035FD6"},
    {0x4803FC0, "C0035FD6"},
    {0x4802D94, "000080D2"},
    {0x41C0658, "C0035FD6"},
    {0x41C05F0, "C0035FD6"},
    {0x41C0588, "C0035FD6"},
    {0x4ACCA7C, "C0035FD6"},
    {0xA680D4, "C0035FD6"},
    {0xA68C40, "C0035FD6"},
    {0xA0DBEC, "C0035FD6"},
    {0xA14690, "C0035FD6"},
    {0xA2BC94, "C0035FD6"},
    {0xBFBC84, "C0035FD6"},
    {0x2F327A4, "C0035FD6"},
    {0x2F338CC, "C0035FD6"},
    {0x3198DFC, "C0035FD6"},
    {0x3198F08, "C0035FD6"},
    {0x3198FE0, "C0035FD6"},
    {0x3199A84, "C0035FD6"},
    {0x3199C48, "C0035FD6"},
    {0x3199E0C, "C0035FD6"},
    {0x319A1E4, "C0035FD6"},
    {0x319A440, "C0035FD6"},
    {0x319D7A0, "C0035FD6"},
    {0x319D92C, "C0035FD6"},
    {0xA30218, "C0035FD6"},
    {0xA2FB20, "C0035FD6"},
    {0xA2FEC4, "C0035FD6"},
    {0xA304E4, "C0035FD6"},
    {0xA2F530, "C0035FD6"},
    {0x129CCD0, "00008052C0035FD6"},
    {0x5F01C28, "20008052C0035FD6"},
    {0x5F01604, "C0035FD6"},
    {0x5F01CA4, "20008052C0035FD6"},
    {0x5F01DE0, "20008052C0035FD6"},
    {0x5F01EF8, "20008052C0035FD6"},
    {0x5F02488, "20008052C0035FD6"},
    {0x5F026E0, "C0035FD6"},
    {0x5F026E8, "C0035FD6"},
    {0x4802D8C, "C0035FD6"},
    {0x48030D8, "C0035FD6"},
    {0x4803A70, "C0035FD6"},
    {0x4803EF8, "C0035FD6"},
    {0x4804864, "C0035FD6"},
    {0x319C904, "00008052C0035FD6"},
    {0x2E5A680, "00008052C0035FD6"},
    {0x2E5A6E0, "C0035FD6"},
    {0x3193D0C, "C0035FD6"},
    {0x319B398, "C0035FD6"},
    {0x319B628, "C0035FD6"},
    {0x319B6C4, "C0035FD6"},
    {0x319BEA8, "00008052C0035FD6"},
    {0x319BFD4, "00008052C0035FD6"},
    {0x319C278, "C0035FD6"},
    {0x319C428, "C0035FD6"},
    {0x319C6C8, "C0035FD6"},
    {0x32F61FC, "C0035FD6"},
    {0x26D5C28, "C0035FD6"},
    {0x26DB1A0, "C0035FD6"},
    {0x4806710, "C0035FD6"},
    {0x30FF60C, "C0035FD6"},
    {0x4805158, "C0035FD6"},
    {0xB9F2AC, "C0035FD6"},
    {0x31073E4, "C0035FD6"},
    {0x4804214, "C0035FD6"},
    {0x4804A2C, "C0035FD6"},
    {0x30F46C0, "C0035FD6"},
    {0x30F5F08, "C0035FD6"},
    {0x2D50310, "C0035FD6"}
};

uint8_t HexDigit(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return 0;
}

void WritePatch(uint64_t offset, const char* hexBytes) {
    size_t len = strlen(hexBytes);
    size_t byteLen = len / 2;
    uint8_t* bytes = new uint8_t[byteLen];
    
    for(size_t i=0; i<byteLen; i++) {
        bytes[i] = (HexDigit(hexBytes[i*2]) << 4) | HexDigit(hexBytes[i*2+1]);
    }
    
    // Check offsets are valid using Mem.h logic
    uintptr_t address = getRealOffset(offset);
    if (!address) {
        delete[] bytes;
        return;
    }

    kern_return_t err;
    mach_port_t port = mach_task_self();
    
    // Unlock memory
    err = vm_protect(port, (mach_vm_address_t)address, byteLen, false, VM_PROT_READ | VM_PROT_WRITE | VM_PROT_COPY);
    if (err == KERN_SUCCESS) {
        // Write bytes
        vm_write(port, (mach_vm_address_t)address, (vm_offset_t)bytes, byteLen);
        
        // Restore permissions
        vm_protect(port, (mach_vm_address_t)address, byteLen, false, VM_PROT_READ | VM_PROT_EXECUTE);
    }
    
    delete[] bytes;
}

void ApplyErzoBypass() {
    for (const auto& patch : bypassPatches) {
        WritePatch(patch.offset, patch.hexCode);
    }
}
