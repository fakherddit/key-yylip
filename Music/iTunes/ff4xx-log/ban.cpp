#include <cstdio>
#include <cstdint>


// Đổi tên hàm tránh trùng
void* getRealAddr(uintptr_t offset) {
    return (void*)(offset);
}

#define BAN_ACC_PTR_OFFSET 0x52AC18

// Biến toàn cục
void* originalBanAcc = nullptr;
bool isBanBlocked = false;

// Hàm giả thay thế BanAcc
void* FakeBanAcc(void* arg) {
    printf("[!] BanAcc() bị chặn!\n");
    static bool result = false;
    return &result;
}

// Bật chặn
void EnableBanBlock() {
    if (isBanBlocked) return;

    void** banAccPtr = (void**)getRealAddr(BAN_ACC_PTR_OFFSET);

    originalBanAcc = *banAccPtr;          // lưu con trỏ gốc
    *banAccPtr = (void*)&FakeBanAcc;      // ghi đè bằng hàm giả


    isBanBlocked = true;
    printf("[+] Đã BẬT chặn BanAcc()\n");
}

// Tắt chặn
void DisableBanBlock() {
    if (!isBanBlocked) return;

    void** banAccPtr = (void**)getRealAddr(BAN_ACC_PTR_OFFSET);

    *banAccPtr = originalBanAcc;          // khôi phục con trỏ ban đầu


    isBanBlocked = false;
    printf("[+] Đã TẮT chặn BanAcc()\n");
}

// Ví dụ main test
int main() {
    EnableBanBlock();   // bật chặn
    // Gọi BanAcc giả thử (thực tế gọi từ game)
    FakeBanAcc(nullptr);
    DisableBanBlock();  // tắt chặn
    return 0;
}
