#include <cstdio>
#include <cstdint>


// Đổi tên hàm tránh trùng
void* getRealAddr(uintptr_t offset) {
    return (void*)(offset);
}

#define BAN_ACC_PTR_OFFSET 0x0052AC48

// Biến toàn cục
void* originalBanAcc = nullptr;
bool BanDay = false;

// Hàm giả thay thế BanAcc
void* FakeBanAcc(void* arg) {
    printf("[!] Ban Day() bị chặn!\n");
    static bool result = false;
    return &result;
}

// Bật chặn
void EnableBanBlock() {
    if (BanDay) return;

    void** banAccPtr = (void**)getRealAddr(BAN_ACC_PTR_OFFSET);

    originalBanAcc = *banAccPtr;          // lưu con trỏ gốc
    *banAccPtr = (void*)&FakeBanAcc;      // ghi đè bằng hàm giả


    isBanBlocked = true;
    printf("[+] Đã BẬT chặn Ban Day()\n");
}

// Tắt chặn
void DisableBanBlock() {
    if (!BanDay) return;

    void** banAccPtr = (void**)getRealAddr(BAN_ACC_PTR_OFFSET);

    *banAccPtr = originalBanAcc;          // khôi phục con trỏ ban đầu


    BanDay = false;
    printf("[+] Đã TẮT chặn Ban Day()\n");
}

// Ví dụ main test
int main() {
    EnableBanBlock();   // bật chặn
    // Gọi BanAcc giả thử (thực tế gọi từ game)
    FakeBanAcc(nullptr);
    DisableBanBlock();  // tắt chặn
    return 0;
}
