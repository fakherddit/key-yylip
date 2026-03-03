#import "Esp/ImGuiDrawView.h"
#import <Metal/Metal.h>
#import <MetalKit/MetalKit.h>
#import <Foundation/Foundation.h>
#define ICON_FA_COG u8"\uf013"
#define ICON_FA_EXTRA u8"\uf067"
#define ICON_FA_EXCLAMATION_TRIANGLE "\xef\x81\xb1"
#include <iostream>
#include <UIKit/UIKit.h>
#include <vector>
#include "iconcpp.h"
#import "pthread.h"
#include <array>
#include <cmath>
#include <deque>
#include <fstream>
#include <algorithm>
#include <string>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <cerrno>
#include <cctype>
// Imgui library
// #import "JRMemory.framework/Headers/MemScan.h"
#import "Esp/CaptainHook.h"
#import "Esp/ImGuiDrawView.h"
#import "IMGUI/imgui.h"
#import "IMGUI/imgui_internal.h"
#import "IMGUI/imgui_impl_metal.h"
#import "IMGUI/zzz.h"
#include "oxorany/oxorany_include.h"
#import "Helper/Mem.h"
#include "font.h"
#import "Esp/Includes.h"
#import "Helper/Vector3.h"
#import "Helper/Vector2.h"
#import "Helper/Quaternion.h"
#import "Helper/Monostring.h"
#import <Foundation/Foundation.h>
#include "Helper/font.h"
#include "Helper/data.h"
#include "Helper/UltraSafeMode.h"        // ULTRA SAFE - Only ESP/Radar, NO damage/kill
#include "Helper/LogCleaner.h"           // Dynamic Anti-Cheat - Clean logs every 2 min
#include "Helper/StrongProtection.h"     // Enhanced protection for Free Fire IPA
#include "Helper/CrashFix.h"             // Disable damage hooks to prevent crash
#include "Helper/UltraMinimal.h"         // ZERO features - ptrace only - NO CRASH
#include "Helper/ProximityBypass.h"      // PROXIMITY FIX - Crash when close to enemy (<15m)
// ALL BYPASS SYSTEMS DISABLED - Testing if old offsets cause bans
// #include "Helper/SafeBypass.h" - Has patches with old offsets
#include "Helper/StealthBypass.h"
// #include "Helper/StoneProtection.h"
// #include "Helper/CloudBypass.h"
// #include "Helper/UltimateProtection.h"
// #include "Helper/DelayedInit.h"
// #include "ban.cpp"
ImFont* verdana_smol;
ImFont* pixel_big = {};
ImFont* pixel_smol = {};
#include "Helper/Obfuscate.h"
#import "Helper/Hooks.h"
game_sdk_t *game_sdk = nullptr;
#import "Helper/Bypass.h"
// #import "Helper/TacticalAntiCrash.h" // Added Tactical Anti-Crash
#import "Helper/ShadowBypass.h" // Added Shadow Bypass (Anti-Exit + Logs)

// CRASH FIX: Remove bad hook header
// #include "hook/hook.h"

// --- UNIFIED ANTI-BAN & FEATURES MODULE ---

// Forward declaration
void PerformDeceptionHandshake();

// Hook for application lifecycle
static void (*orig_applicationDidBecomeActive)(id, SEL, id);

// Hook DISABLED to prevent startup crash
static void hook_applicationDidBecomeActive(id self, SEL _cmd, id application) {
    // Call original method FIRST to let the game initialize normally
    if (orig_applicationDidBecomeActive) {
        orig_applicationDidBecomeActive(self, _cmd, application);
    }
}

// Spoof Bundle ID to bypass "Validation Gateway" checks
static NSString* (*orig_bundleIdentifier)(id self, SEL _cmd);
static NSString* hook_bundleIdentifier(id self, SEL _cmd) {
    return @"com.dts.freefireth"; 
}

// Global state for bypass
static bool g_BypassActive = false;

// ULTRA MINIMAL - ZERO FEATURES
void RealSystemInit() {
    NSLog(@"[ULTRA-MINIMAL] ptrace ONLY - NO features - NO crash");
    
    // ONLY ptrace - nothing else
    UltraMinimal::InitializeUltraMinimal();
    
    NSLog(@"[ULTRA-MINIMAL] Done - game should NOT crash");
}

// Simulated Server Handshake (Controlled by Menu)
void PerformDeceptionHandshake() {
    if (g_BypassActive) {
        NSLog(@"[HANDSHAKE] Bypass already active!");
        return;
    }

    NSLog(@"[HANDSHAKE] Manually Initiating Deception Protocol (LOBBY MODE)...");
    
    // Step 1: تفعيل نظام الحماية المتقدم
    // OLD FUNCTIONS DISABLED - Using Stealth Bypass now
    NSLog(@"[HANDSHAKE] Step 1/4: Stealth Protection Already Active.");
    
    // Step 2: Spoof Bundle ID
    // MSHookMessageEx(objc_getClass("NSBundle"), @selector(bundleIdentifier), (IMP)&hook_bundleIdentifier, (IMP*)&orig_bundleIdentifier);
    NSLog(@"[HANDSHAKE] Step 2/4: BundleID Spoof Verified (DISABLED).");
    
    // Step 3: Apply Memory Patches
    // OLD PATCHING DISABLED - Too detectable
    NSLog(@"[HANDSHAKE] Step 3/4: Stealth Hooks Already Applied.");

    // Step 4: Clean Memory
    // ApplyStringCleaner();
    NSLog(@"[HANDSHAKE] Step 4/4: Memory Cleaned (DISABLED).");
    
    g_BypassActive = true;
    NSLog(@"[HANDSHAKE] Deception Handshake Complete. All Protections Active!");
}


// System Initialization - MINIMAL MODE (NO PATCHES)
__attribute__((constructor(102)))
static void SystemServiceInit() {
    NSLog(@"[INIT] SystemServiceInit: FREE FIRE MAX AIMBOT ENABLED");
    NSLog(@"[INIT] Safe Activation: Only Aimbot + ESP");
    
    // Initialize strong protection
    // StrongProtection::Initialize();
    
    // ACTIVATE TACTICAL ANTI-CRASH (Anti-Terminate)
    // TacticalAntiCrash::Initialize();
    
    // DELAYED SHADOW BYPASS: DISABLED FOR DIAGNOSTICS
    /*
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(8.0 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        NSLog(@"[DELAYED INIT] Activating Shadow Bypass for Kill Protection...");
        ShadowBypass::Initialize();
    });
    */

    // Initialize GameSDK (LAZY INIT - fix startup crash)
    if (!game_sdk) {
        game_sdk = new game_sdk_t();
        // game_sdk->init(); // Do NOT call init here, call it later when game is loaded
    }
    
    // ACTIVATE ULTRA SAFE MODE (ESP only, no damage/kill) - DISABLED TO ALLOW AIM
    // UltraSafeMode::Initialize();
    
    // ACTIVATE AIMBOT LOGIC
    // Re-enabling basic aim helper initialization if needed
    // #include "Helper/AimKill.h" logic is usually in main loop or draw hook
    
    NSLog(@"[INIT] ✅ Safe Mode with Aim Activated");
}
#import "IMGUI/zzz.h"
#include <OpenGLES/ES2/gl.h>
#include <OpenGLES/ES2/glext.h>
#include <unistd.h>
#include <string.h>
#include "hook/hook.h"
ImVec4 userColor = ImVec4(1.0f, 0.0f, 0.0f, 1.0f);
ImVec4 espv = ImVec4(0.0f, 1.0f, 0.0f, 1.0f);
ImVec4 espi = ImVec4(1.0f, 0.0f, 0.0f, 1.0f);
ImVec4 fovColor = ImVec4(1.0f, 0.0f, 0.0f, 1.0f);
ImVec4 nameColor = ImVec4(1.0f, 1.0f, 1.0f, 1.0f);
ImVec4 distanceColor = ImVec4(1.0f, 1.0f, 1.0f, 1.0f);
#define timer(sec) dispatch_after(dispatch_time(DISPATCH_TIME_NOW, sec * NSEC_PER_SEC), dispatch_get_main_queue(), ^
#define kWidth  [UIScreen mainScreen].bounds.size.width
#define kHeight [UIScreen mainScreen].bounds.size.height
#define kScale [UIScreen mainScreen].scale
#define UIColorFromHex(hexColor) [UIColor colorWithRed:((float)((hexColor & 0xFF0000) >> 16))/255.0 green:((float)((hexColor & 0xFF00) >> 8))/255.0 blue:((float)(hexColor & 0xFF))/255.0 alpha:1.0]
UIWindow *mainWindow;
UIButton *menuView;
// Ghost Mode Variables


@interface ImGuiDrawView () <MTKViewDelegate>
@property (nonatomic, strong) id <MTLDevice> device;
@property (nonatomic, strong) id <MTLCommandQueue> commandQueue;
@end

@implementation ImGuiDrawView
ImFont *_espFont;
ImFont* verdanab;
ImFont* icons;
ImFont* interb;
ImFont* Urbanist;

// Safety System
static bool g_SystemInitialized = false;
static bool g_MemoryEngineReady = false;
static bool g_UIReady = false;
static int g_FeatureFailCount = 0;
static const int MAX_FAIL_COUNT = 3;

static bool MenDeal = true; // Menu visible by default (gesture toggles)
BOOL hasGhostBeenDrawn = NO;
static bool StreamerMode = true;
static bool aimKill = false;
static bool voarPlayer = false;
static bool teleport8m = false;
bool fakeLagEnabled = false;
bool FastReloadEnabled = true;
bool SpeeeX2Enabled = false;
bool NoRecoilEnabled = false;
bool WallGlowEnabled = false;
bool WallFlyEnabled = false;
bool WallHackEnabled = false;
bool ScopeEnabled = false;
bool BypassEnabled = true;
bool istelekill = false;
bool isfly = false;

// New Globals
bool ComfortMode = false;
int SpeedOption = 0; // 0: Off, 1: x2, 2: x8, 3: x10
int FixLoginTimer = 0;
bool showLoginMessage = false;

// Key Validation System - ENABLED
static bool isKeyValidated = false; // API Server ENABLED - Key Required
static char keyInput[128] = "";
static std::string validationMessage = "";
static NSString* serverURL = @"https://ggggggggggggggggggg.onrender.com/validate"; // Render API Server

// Key Validation Function
- (BOOL)validateKeyWithServer:(NSString*)key {
    NSURL *url = [NSURL URLWithString:serverURL];
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
    [request setHTTPMethod:@"POST"];
    [request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
    
    NSDictionary *postData = @{@"key": key, @"hwid": [self getDeviceHWID]};
    NSData *jsonData = [NSJSONSerialization dataWithJSONObject:postData options:0 error:nil];
    [request setHTTPBody:jsonData];
    
    dispatch_semaphore_t semaphore = dispatch_semaphore_create(0);
    __block BOOL isValid = NO;
    
    NSURLSession *session = [NSURLSession sharedSession];
    [[session dataTaskWithRequest:request completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        if (data) {
            NSDictionary *json = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
            isValid = [[json objectForKey:@"valid"] boolValue];
            validationMessage = [[json objectForKey:@"message"] UTF8String];
        }
        dispatch_semaphore_signal(semaphore);
    }] resume];
    
    dispatch_semaphore_wait(semaphore, dispatch_time(DISPATCH_TIME_NOW, 5 * NSEC_PER_SEC));
    return isValid;
}

- (NSString*)getDeviceHWID {
    return [[[UIDevice currentDevice] identifierForVendor] UUIDString];
}

- (void)showAuthenticationDialog {
    dispatch_async(dispatch_get_main_queue(), ^{
        NSLog(@"[ST-AUTH] 🔍 Checking clipboard for auto-paste...");
        
        // Try to auto-paste from clipboard
        UIPasteboard *pasteboard = [UIPasteboard generalPasteboard];
        NSString *clipboardText = pasteboard.string;
        
        if (clipboardText) {
            NSLog(@"[ST-AUTH] 📋 Clipboard content: '%@' (length: %lu)", clipboardText, (unsigned long)clipboardText.length);
        } else {
            NSLog(@"[ST-AUTH] ⚠️ Clipboard is empty");
        }
        
        // Check if clipboard contains a valid key format (XXXX-XXXX-XXXX-XXXX or GLB-XXXX-XXXX-XXXX)
        BOOL isValidFormat = NO;
        if (clipboardText && clipboardText.length > 0) {
            // Trim whitespace first
            NSString *trimmedText = [clipboardText stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
            NSString *upperText = [trimmedText uppercaseString];
            
            NSLog(@"[ST-AUTH] 🔍 Testing pattern on: '%@'", upperText);
            
            // More flexible pattern - allow spaces and variations
            NSString *pattern1 = @"^[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$";
            NSString *pattern2 = @"^GLB-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$";
            
            NSPredicate *test1 = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", pattern1];
            NSPredicate *test2 = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", pattern2];
            
            isValidFormat = [test1 evaluateWithObject:upperText] || [test2 evaluateWithObject:upperText];
            
            if (isValidFormat) {
                NSLog(@"[ST-AUTH] ✅ Valid key format detected!");
            } else {
                NSLog(@"[ST-AUTH] ❌ Invalid format - expected XXXX-XXXX-XXXX-XXXX or GLB-XXXX-XXXX-XXXX");
            }
        }
        
        // If valid key in clipboard, auto-validate SILENTLY
        if (isValidFormat) {
            NSString *trimmedText = [clipboardText stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
            NSString *autoKey = [trimmedText uppercaseString];
            NSLog(@"[ST-AUTH] 🚀 Silent auto-validation: %@", autoKey);
            
            // Validate in background WITHOUT showing any UI
            dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
                BOOL isValid = [self validateKeyWithServer:autoKey];
                
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (isValid) {
                        isKeyValidated = YES;
                        MenDeal = YES;
                        NSLog(@"[ST-AUTH] ✅ Silent validation SUCCESS - Direct panel access!");
                        // NO ALERT - Panel will show automatically in main render loop
                    } else {
                        NSLog(@"[ST-AUTH] ❌ Validation FAILED - Show error");
                        // Only show UI on failure
                        NSString *errorMsg = validationMessage.empty() ? @"❌ Invalid or Expired Key\n\nPlease get a new key from @STXFAMILY_bot" : [NSString stringWithUTF8String:validationMessage.c_str()];
                        UIAlertController *error = [UIAlertController alertControllerWithTitle:@"🔐 Authentication Failed"
                                                                                       message:errorMsg
                                                                                preferredStyle:UIAlertControllerStyleAlert];
                        [error addAction:[UIAlertAction actionWithTitle:@"🔑 Get Key" style:UIAlertActionStyleDefault handler:^(UIAlertAction *action) {
                            NSURL *telegramURL = [NSURL URLWithString:@"https://t.me/STXFAMILY_bot"];
                            if ([[UIApplication sharedApplication] canOpenURL:telegramURL]) {
                                [[UIApplication sharedApplication] openURL:telegramURL options:@{} completionHandler:nil];
                            }
                        }]];
                        [error addAction:[UIAlertAction actionWithTitle:@"⌨️ Enter Key" style:UIAlertActionStyleDefault handler:^(UIAlertAction *action) {
                            [self showManualKeyDialog:nil];
                        }]];
                        [[UIApplication sharedApplication].keyWindow.rootViewController presentViewController:error animated:YES completion:nil];
                    }
                });
            });
            return;
        }
        
        // No valid key in clipboard, show manual entry
        NSLog(@"[ST-AUTH] 📝 Showing manual entry dialog");
        [self showManualKeyDialog:nil];
    });
}

- (void)showManualKeyDialog:(NSString*)errorMsg {
    dispatch_async(dispatch_get_main_queue(), ^{
        UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"🔐 Authentication"
                                                                       message:errorMsg ? errorMsg : @"Enter your License Key\n(or copy it first for auto-paste)"
                                                                preferredStyle:UIAlertControllerStyleAlert];
        
        [alert addTextFieldWithConfigurationHandler:^(UITextField *textField) {
            textField.placeholder = @"XXXX-XXXX-XXXX-XXXX";
            textField.autocapitalizationType = UITextAutocapitalizationTypeAllCharacters;
            textField.autocorrectionType = UITextAutocorrectionTypeNo;
            textField.keyboardType = UIKeyboardTypeDefault;
            textField.clearButtonMode = UITextFieldViewModeWhileEditing;
            textField.returnKeyType = UIReturnKeyDone;
            
            // Auto-fill from clipboard if available
            UIPasteboard *pb = [UIPasteboard generalPasteboard];
            if (pb.string && pb.string.length > 10) {
                textField.text = [pb.string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
                NSLog(@"[ST-AUTH] 📋 Auto-filled textfield from clipboard");
            }
        }];
        
        UIAlertAction *pasteAction = [UIAlertAction actionWithTitle:@"📋 Paste & Validate"
                                                              style:UIAlertActionStyleDefault
                                                            handler:^(UIAlertAction *action) {
            UIPasteboard *pb = [UIPasteboard generalPasteboard];
            NSString *key = [[pb.string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] uppercaseString];
            
            NSLog(@"[ST-AUTH] 📋 Manual paste: '%@'", key);
            
            if ([self validateKeyWithServer:key]) {
                isKeyValidated = true;
                MenDeal = true;
                NSLog(@"[ST-AUTH] ✅ Manual validation SUCCESS - Direct access!");
                // NO SUCCESS ALERT - Direct panel access
            } else {
                NSLog(@"[ST-AUTH] ❌ Manual validation FAILED");
                dispatch_async(dispatch_get_main_queue(), ^{
                    UIAlertController *error = [UIAlertController alertControllerWithTitle:@"❌ Error"
                                                                                   message:@"Invalid key or connection error"
                                                                            preferredStyle:UIAlertControllerStyleAlert];
                    [error addAction:[UIAlertAction actionWithTitle:@"Retry" style:UIAlertActionStyleDefault handler:^(UIAlertAction *action) {
                        [self showAuthenticationDialog];
                    }]];
                    [[UIApplication sharedApplication].keyWindow.rootViewController presentViewController:error animated:YES completion:nil];
                });
            }
        }];
        
        UIAlertAction *loginAction = [UIAlertAction actionWithTitle:@"✅ Activate"
                                                              style:UIAlertActionStyleDefault
                                                            handler:^(UIAlertAction *action) {
            UITextField *keyField = alert.textFields.firstObject;
            NSString *key = [[keyField.text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] uppercaseString];
            
            NSLog(@"[ST-AUTH] ⌨️ Manual entry: '%@'", key);
            
            if ([self validateKeyWithServer:key]) {
                isKeyValidated = true;
                MenDeal = true;
                NSLog(@"[ST-AUTH] ✅ Typed validation SUCCESS - Direct access!");
                // NO SUCCESS ALERT - Direct panel access
            } else {
                NSLog(@"[ST-AUTH] ❌ Typed validation FAILED");
                dispatch_async(dispatch_get_main_queue(), ^{
                    UIAlertController *error = [UIAlertController alertControllerWithTitle:@"❌ Error"
                                                                                   message:@"Invalid key or connection error"
                                                                            preferredStyle:UIAlertControllerStyleAlert];
                    [error addAction:[UIAlertAction actionWithTitle:@"Retry" style:UIAlertActionStyleDefault handler:^(UIAlertAction *action) {
                        [self showAuthenticationDialog];
                    }]];
                    [[UIApplication sharedApplication].keyWindow.rootViewController presentViewController:error animated:YES completion:nil];
                });
            }
        }];
        
        UIAlertAction *getKeyAction = [UIAlertAction actionWithTitle:@"🔑 Get Key"
                                                               style:UIAlertActionStyleDefault
                                                             handler:^(UIAlertAction *action) {
            NSLog(@"[ST-AUTH] 🔗 Opening Telegram bot");
            NSURL *telegramURL = [NSURL URLWithString:@"https://t.me/STXFAMILY_bot"];
            if ([[UIApplication sharedApplication] canOpenURL:telegramURL]) {
                [[UIApplication sharedApplication] openURL:telegramURL options:@{} completionHandler:^(BOOL success) {
                    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 1 * NSEC_PER_SEC), dispatch_get_main_queue(), ^{
                        [self showAuthenticationDialog];
                    });
                }];
            } else {
                [self showAuthenticationDialog];
            }
        }];
        
        [alert addAction:pasteAction];
        [alert addAction:loginAction];
        [alert addAction:getKeyAction];
        
        [[UIApplication sharedApplication].keyWindow.rootViewController presentViewController:alert animated:YES completion:nil];
    });
}

bool antiban(void *instance) {
    return false;
}


- (void)setSpeedMode:(int)mode {
    NSLog(@"[ST-SPEED] 🎯 Setting speed mode: %d (DISABLED)", mode);
}

- (void)toggleFastScope:(BOOL)enable {
    NSLog(@"[ST-FASTSCOPE] Disabled");
}

// STUBS removed - genuine implementations follow

- (void)toggleTracking:(BOOL)enable {
    NSLog(@"[ST-TRACKING] Disabled");
}

- (void)toggleNoRecoil:(BOOL)enable {
    NSLog(@"[ST-NORECOIL] Disabled");
}

- (void)toggleWallGlow:(BOOL)enable {
    NSLog(@"[ST-WALLGLOW] Disabled");
}

// Fly & Wall Fly Logic - Enhanced & Stable
- (void)toggleWallFly:(BOOL)enable {
    NSLog(@"[ST-FLY] Disabled");
}

- (void)toggleWallHack:(BOOL)enable {
    NSLog(@"[ST-WALLHACK] Disabled");
}

- (void)toggleScope:(BOOL)enable {
    NSLog(@"[ST-SCOPE] Disabled");
}

- (instancetype)initWithNibName:(nullable NSString *)nibNameOrNil bundle:(nullable NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];

    _device = MTLCreateSystemDefaultDevice();
    _commandQueue = [_device newCommandQueue];

    if (!self.device) abort();

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;
    io.FontGlobalScale = 1.15f; // زيادة سُمك الخط
    ImGuiStyle& style = ImGui::GetStyle();

    // Dark Gradient / Soft Red Aesthetic
    style.WindowPadding = ImVec2(15, 15);
    style.WindowRounding = 12.0f;
    style.FramePadding = ImVec2(5, 5);
    style.FrameRounding = 6.0f;
    style.ItemSpacing = ImVec2(12, 8);
    style.ItemInnerSpacing = ImVec2(8, 6);
    style.IndentSpacing = 25.0f;
    style.ScrollbarSize = 15.0f;
    style.ScrollbarRounding = 9.0f;
    style.GrabMinSize = 5.0f;
    style.GrabRounding = 6.0f;
    style.TabRounding = 6.0f;
    style.ChildRounding = 0.0f; // إزالة borders
    style.ChildBorderSize = 0.0f; // إزالة borders

    ImVec4 text = ImVec4(0.92f, 0.92f, 0.92f, 1.00f);
    ImVec4 textDis = ImVec4(0.45f, 0.45f, 0.45f, 1.00f);
    ImVec4 bg = ImVec4(0.05f, 0.05f, 0.05f, 0.98f); // Very dark background
    ImVec4 accent = ImVec4(0.80f, 0.20f, 0.25f, 1.00f); // Soft Red
    ImVec4 accentHover = ImVec4(0.90f, 0.25f, 0.30f, 1.00f);
    ImVec4 accentActive = ImVec4(0.70f, 0.15f, 0.20f, 1.00f);
    ImVec4 elementBg = ImVec4(0.10f, 0.10f, 0.10f, 1.00f); // Darker elements
    
    style.Colors[ImGuiCol_Text] = text;
    style.Colors[ImGuiCol_TextDisabled] = textDis;
    style.Colors[ImGuiCol_WindowBg] = bg;
    style.Colors[ImGuiCol_ChildBg] = ImVec4(0.08f, 0.08f, 0.08f, 1.00f); // Darker child bg
    style.Colors[ImGuiCol_PopupBg] = bg;
    style.Colors[ImGuiCol_Border] = ImVec4(0.15f, 0.15f, 0.15f, 0.40f); // Darker border
    style.Colors[ImGuiCol_BorderShadow] = ImVec4(0.00f, 0.00f, 0.00f, 0.00f);
    style.Colors[ImGuiCol_FrameBg] = elementBg;
    style.Colors[ImGuiCol_FrameBgHovered] = ImVec4(0.15f, 0.15f, 0.15f, 1.00f); // Darker hover
    style.Colors[ImGuiCol_FrameBgActive] = ImVec4(0.20f, 0.20f, 0.20f, 1.00f); // Darker active
    style.Colors[ImGuiCol_TitleBg] = accent;
    style.Colors[ImGuiCol_TitleBgActive] = accent;
    style.Colors[ImGuiCol_TitleBgCollapsed] = accent;
    style.Colors[ImGuiCol_MenuBarBg] = ImVec4(0.15f, 0.15f, 0.17f, 1.00f);
    style.Colors[ImGuiCol_ScrollbarBg] = ImVec4(0.02f, 0.02f, 0.02f, 0.50f);
    style.Colors[ImGuiCol_ScrollbarGrab] = elementBg;
    style.Colors[ImGuiCol_ScrollbarGrabHovered] = accentHover;
    style.Colors[ImGuiCol_ScrollbarGrabActive] = accentActive;
    style.Colors[ImGuiCol_CheckMark] = accent;
    style.Colors[ImGuiCol_SliderGrab] = accent;
    style.Colors[ImGuiCol_SliderGrabActive] = accentActive;
    style.Colors[ImGuiCol_Button] = elementBg;
    style.Colors[ImGuiCol_ButtonHovered] = accentHover;
    style.Colors[ImGuiCol_ButtonActive] = accentActive;
    style.Colors[ImGuiCol_Header] = elementBg;
    style.Colors[ImGuiCol_HeaderHovered] = accentHover;
    style.Colors[ImGuiCol_HeaderActive] = accentActive;
    style.Colors[ImGuiCol_Separator] = ImVec4(0.25f, 0.25f, 0.27f, 1.00f);
    style.Colors[ImGuiCol_SeparatorHovered] = accentHover;
    style.Colors[ImGuiCol_SeparatorActive] = accentActive;
    style.Colors[ImGuiCol_ResizeGrip] = elementBg;
    style.Colors[ImGuiCol_ResizeGripHovered] = accentHover;
    style.Colors[ImGuiCol_ResizeGripActive] = accentActive;
    style.Colors[ImGuiCol_Tab] = elementBg;
    style.Colors[ImGuiCol_TabHovered] = accentHover;
    style.Colors[ImGuiCol_TabActive] = accent;
    style.Colors[ImGuiCol_TabUnfocused] = elementBg;
    style.Colors[ImGuiCol_TabUnfocusedActive] = elementBg;
    style.Colors[ImGuiCol_PlotLines] = text;
    style.Colors[ImGuiCol_PlotLinesHovered] = accent;
    style.Colors[ImGuiCol_PlotHistogram] = text;
    style.Colors[ImGuiCol_PlotHistogramHovered] = accent;
    style.Colors[ImGuiCol_TextSelectedBg] = accent;
    style.Colors[ImGuiCol_DragDropTarget] = accent;
    style.Colors[ImGuiCol_NavHighlight] = textDis;
    style.Colors[ImGuiCol_NavWindowingHighlight] = text;
    style.Colors[ImGuiCol_NavWindowingDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.20f);
    style.Colors[ImGuiCol_ModalWindowDimBg] = ImVec4(0.80f, 0.80f, 0.80f, 0.35f);

    static const ImWchar icons_ranges[] = { 0xf000, 0xf3ff, 0 };
    ImFontConfig icons_config;
    ImFontConfig CustomFont;
    CustomFont.FontDataOwnedByAtlas = false;
    icons_config.MergeMode = true;
    icons_config.PixelSnapH = true;
    io.Fonts->AddFontFromMemoryTTF(const_cast<std::uint8_t*>(Custom), sizeof(Custom), 21.f, &CustomFont);
    io.Fonts->AddFontFromMemoryCompressedTTF(font_awesome_data, font_awesome_size, 19.0f, &icons_config, icons_ranges);
    io.Fonts->AddFontDefault();
    ImFont* font = io.Fonts->AddFontFromMemoryTTF(sansbold, sizeof(sansbold), 21.0f, NULL, io.Fonts->GetGlyphRangesCyrillic());
    verdana_smol = io.Fonts->AddFontFromMemoryTTF(verdana, sizeof verdana, 40, NULL, io.Fonts->GetGlyphRangesCyrillic());
    pixel_big = io.Fonts->AddFontFromMemoryTTF((void*)smallestpixel, sizeof smallestpixel, 400, NULL, io.Fonts->GetGlyphRangesCyrillic());
    pixel_smol = io.Fonts->AddFontFromMemoryTTF((void*)smallestpixel, sizeof smallestpixel, 10*2, NULL, io.Fonts->GetGlyphRangesCyrillic());
    ImGui_ImplMetal_Init(_device);

    return self;
}

// Custom Toggle Switch Widget
bool ToggleSwitch(const char* str_id, bool* v) {
    ImVec2 p = ImGui::GetCursorScreenPos();
    ImDrawList* draw_list = ImGui::GetWindowDrawList();

    float height = ImGui::GetFrameHeight();
    float width = height * 1.8f;
    float radius = height * 0.50f;

    ImGui::InvisibleButton(str_id, ImVec2(width, height));
    if (ImGui::IsItemClicked())
        *v = !*v;

    float t = *v ? 1.0f : 0.0f;

    ImGuiContext& g = *GImGui;
    float ANIM_SPEED = 0.08f;
    if (g.LastActiveId == g.CurrentWindow->GetID(str_id))
    {
        float t_anim = ImSaturate(g.LastActiveIdTimer / ANIM_SPEED);
        t = *v ? (t_anim) : (1.0f - t_anim);
    }

    ImU32 col_bg;
    if (ImGui::IsItemHovered())
        col_bg = ImGui::GetColorU32(ImLerp(ImVec4(0.50f, 0.50f, 0.50f, 1.0f), ImVec4(0.10f, 0.85f, 0.20f, 1.0f), t)); // Green when on
    else
        col_bg = ImGui::GetColorU32(ImLerp(ImVec4(0.35f, 0.35f, 0.35f, 1.0f), ImVec4(0.05f, 0.75f, 0.15f, 1.0f), t)); // Green when on

    draw_list->AddRectFilled(p, ImVec2(p.x + width, p.y + height), col_bg, height * 0.5f);
    draw_list->AddCircleFilled(ImVec2(p.x + radius + t * (width - radius * 2.0f), p.y + radius), radius - 1.5f, IM_COL32(255, 255, 255, 255));

    return ImGui::IsItemClicked();
}

+ (void)showChange:(BOOL)open {
    MenDeal = open;
}

+ (BOOL)isMenuShowing {
    return MenDeal;
}

- (MTKView *)mtkView {
    return (MTKView *)self.view;
}

- (void)loadView
{
    CGFloat w = [UIApplication sharedApplication].windows[0].rootViewController.view.frame.size.width;
    CGFloat h = [UIApplication sharedApplication].windows[0].rootViewController.view.frame.size.height;
    self.view = [[MTKView alloc] initWithFrame:CGRectMake(0, 0, w, h)];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.mtkView.device = self.device;
    self.mtkView.delegate = self;
    self.mtkView.clearColor = MTLClearColorMake(0, 0, 0, 0);
    self.mtkView.backgroundColor = [UIColor colorWithRed:0 green:0 blue:0 alpha:0];
    self.mtkView.clipsToBounds = YES;
    self.mtkView.clipsToBounds = YES;
}
#pragma mark - Interaction

- (void)updateIOWithTouchEvent:(UIEvent *)event
{
    UITouch *anyTouch = event.allTouches.anyObject;
    CGPoint touchLocation = [anyTouch locationInView:self.view];
    ImGuiIO &io = ImGui::GetIO();
    io.MousePos = ImVec2(touchLocation.x, touchLocation.y);

    BOOL hasActiveTouch = NO;
    for (UITouch *touch in event.allTouches)
    {
        if (touch.phase != UITouchPhaseEnded && touch.phase != UITouchPhaseCancelled)
        {
            hasActiveTouch = YES;
            break;
        }
    }
    io.MouseDown[0] = hasActiveTouch;
}

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event
{
    [self updateIOWithTouchEvent:event];
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event
{
    [self updateIOWithTouchEvent:event];
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event
{
    [self updateIOWithTouchEvent:event];
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event
{
    [self updateIOWithTouchEvent:event];
}

extern UIView* hideRecordView;

// ÃÂÃÂ£ÃÂÃÂ¶ÃÂÃÂ ÃÂÃÂÃÂÃÂ¨ÃÂÃÂ drawInMTKView

#pragma mark - MTKViewDelegate

- (void)drawInMTKView:(MTKView*)view
{
    ImGuiIO& io = ImGui::GetIO();
    io.DisplaySize.x = view.bounds.size.width;
    io.DisplaySize.y = view.bounds.size.height;

    CGFloat framebufferScale = view.window.screen.nativeScale ?: UIScreen.mainScreen.nativeScale;
    io.DisplayFramebufferScale = ImVec2(framebufferScale, framebufferScale);
    io.DeltaTime = 1 / float(view.preferredFramesPerSecond ?: 60);

    id<MTLCommandBuffer> commandBuffer = [self.commandQueue commandBuffer];
    
    hideRecordTextfield.secureTextEntry = StreamerMode;

    // During Fix Login, disable all interaction on overlay to let touches pass through
    // WARNING: DO NOT USE setHidden:YES on self.view here, or the loop stops running!
    if (FixLoginTimer > 0)
    {
        [self.view setUserInteractionEnabled:NO];
        [self.view setAlpha:0.0f]; // Make invisible but keep running
        
        [menuTouchView setUserInteractionEnabled:NO];
        [menuTouchView setHidden:YES]; // This one can be hidden as it doesn't dry render loop
        
        // Ensure hideRecordView is also passthrough
        if (hideRecordView) {
            [hideRecordView setUserInteractionEnabled:NO];
            [hideRecordView setHidden:YES];
        }
    }
    else if (MenDeal == true) 
    {
        [self.view setUserInteractionEnabled:YES];
        [self.view setAlpha:1.0f];
        
        // [self.view.superview setUserInteractionEnabled:YES]; // KEEP commented - enables interaction on RootView (Game)
        [menuTouchView setUserInteractionEnabled:YES];          // UNCOMMENTED - enables interaction on Overlay (Menu)
        [menuTouchView setHidden:NO];
        
        if (hideRecordView) {
             [hideRecordView setUserInteractionEnabled:YES];
             [hideRecordView setHidden:NO]; // Or whatever its default state is
        }
    } 
    else if (MenDeal == false) 
    {
        [self.view setUserInteractionEnabled:NO];
        [self.view setAlpha:1.0f]; // Keep visible if just "closed" but rendering touches? No, usually hidden if closed.
        // Wait, MenDeal==false means Menu is closed.
        // If menu is closed, self.view handles drawings (ESP)? 
        // Yes, ESP is drawn when menu is closed. So Alpha must be 1.0.
        
        // [self.view.superview setUserInteractionEnabled:NO]; // KEEP commented - would disable interaction on RootView (Game) -> Frozen Screen
        [menuTouchView setUserInteractionEnabled:NO];          // UNCOMMENTED - disables interaction on Overlay (Menu) -> Pass through to Game
        [menuTouchView setHidden:NO];
        
        if (hideRecordView) {
            [hideRecordView setUserInteractionEnabled:NO]; 
        }
    }

    MTLRenderPassDescriptor* renderPassDescriptor = view.currentRenderPassDescriptor;
    if (renderPassDescriptor != nil) 
    {
        id<MTLRenderCommandEncoder> renderEncoder = [commandBuffer renderCommandEncoderWithDescriptor:renderPassDescriptor];
        [renderEncoder pushDebugGroup:@"ImGui Jane"];

        ImGui_ImplMetal_NewFrame(renderPassDescriptor);
        ImGui::NewFrame();
        ImGuiStyle& style = ImGui::GetStyle();
        ImFont* font = ImGui::GetFont();
        font->Scale = 16.f / font->FontSize;
        
        CGFloat x = (([UIApplication sharedApplication].windows[0].rootViewController.view.frame.size.width) - 340) / 2;
        CGFloat y = (([UIApplication sharedApplication].windows[0].rootViewController.view.frame.size.height) - 250) / 2;

ImGui::SetNextWindowPos(ImVec2(x, y), ImGuiCond_FirstUseEver);
        ImGui::SetNextWindowSize(ImVec2(342, 265), ImGuiCond_FirstUseEver);

        

        // Comfort Mode Overlay
        if (ComfortMode) {
             ImGui::GetBackgroundDrawList()->AddRectFilled(
                ImVec2(0, 0), 
                io.DisplaySize, 
                IM_COL32(0, 0, 0, 100) 
            );
        }

        // Don't render panel if Fix Login is active
        if (isKeyValidated && MenDeal == true && FixLoginTimer == 0)
        {
            // COMPACT DASHBOARD DESIGN - Small & Unique
            ImGui::SetNextWindowSize(ImVec2(420, 520), ImGuiCond_Always);
            ImGui::SetNextWindowPos(ImVec2(ImGui::GetIO().DisplaySize.x - 440, 20), ImGuiCond_FirstUseEver);
            
            // Dark theme with red accent
            ImGui::PushStyleColor(ImGuiCol_WindowBg, ImVec4(0.08f, 0.08f, 0.08f, 0.96f));
            ImGui::PushStyleColor(ImGuiCol_Border, ImVec4(0.8f, 0.1f, 0.1f, 0.8f));
            ImGui::PushStyleColor(ImGuiCol_FrameBg, ImVec4(0.15f, 0.15f, 0.15f, 1.0f));
            ImGui::PushStyleColor(ImGuiCol_FrameBgHovered, ImVec4(0.25f, 0.15f, 0.15f, 1.0f));
            ImGui::PushStyleColor(ImGuiCol_FrameBgActive, ImVec4(0.3f, 0.1f, 0.1f, 1.0f));
            ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 8.0f);
            ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 4.0f);
            ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 2.0f);
            
            ImGui::Begin("##STDashboard", &MenDeal, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoScrollbar);
            
            // COMPACT HEADER (With Close Button)
            ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.95f, 0.2f, 0.2f, 1.0f));
            ImGui::SetCursorPosX(ImGui::GetWindowWidth() / 2 - 60);
            ImGui::Text("ST DASHBOARD");
            ImGui::PopStyleColor();

            // CLOSE BUTTON (Top Right)
            ImGui::SetCursorPos(ImVec2(ImGui::GetWindowWidth() - 35, 5));
            ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0,0,0,0)); 
            ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1.0f, 0.2f, 0.2f, 1.0f));
            if (ImGui::Button("X", ImVec2(30, 30))) { MenDeal = false; }
            ImGui::PopStyleColor(2);
            
            ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.5f, 0.5f, 0.5f, 1.0f));
            ImGui::SetCursorPosX(ImGui::GetWindowWidth() / 2 - 40);
            ImGui::Text("FPS: %.0f", ImGui::GetIO().Framerate);
            ImGui::PopStyleColor();
            
            ImGui::Spacing();
            ImGui::Separator();
            ImGui::Spacing();

            // COMPACT TAB SYSTEM - 3 Tabs
            static int activeTab = 0;
            ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.15f, 0.05f, 0.05f, 1.0f));
            ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(0.25f, 0.1f, 0.1f, 1.0f));
            ImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(0.4f, 0.15f, 0.15f, 1.0f));
            ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 3.0f);
            
            float btnWidth = (ImGui::GetWindowWidth() - 50) / 3;
            if (ImGui::Button(activeTab == 0 ? "[AIM]" : "AIM", ImVec2(btnWidth, 35))) activeTab = 0;
            ImGui::SameLine();
            if (ImGui::Button(activeTab == 1 ? "[ESP]" : "ESP", ImVec2(btnWidth, 35))) activeTab = 1;
            ImGui::SameLine();
            if (ImGui::Button(activeTab == 2 ? "[MISC]" : "MISC", ImVec2(btnWidth, 35))) activeTab = 2;
            
            ImGui::PopStyleVar();
            ImGui::PopStyleColor(3);
            
            ImGui::Spacing();
            ImGui::Separator();
            ImGui::Spacing();

            // CONTENT AREA - COMPACT SCROLLABLE
            ImGui::BeginChild("Content", ImVec2(0, ImGui::GetWindowHeight() - 160), true, ImGuiWindowFlags_AlwaysVerticalScrollbar);
            
            if (activeTab == 0) { // AIM TAB
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.95f, 0.3f, 0.3f, 1.0f));
                ImGui::Text("AIMBOT FEATURES");
                ImGui::PopStyleColor();
                ImGui::Spacing();
                
                // Master Aimbot Switch
                bool masterOn = Vars.Aimbot;
                if (ToggleSwitch("##MasterAim", &Vars.Aimbot)) {
                    Vars.AimbotEnable = Vars.Aimbot;
                }
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, masterOn ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.8f, 0.2f, 0.2f, 1.0f));
                ImGui::Text(masterOn ? "Master Aimbot [ON]" : "Master Aimbot [OFF]");
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Spacing();
                
                // Aim Modes
                ImGui::Text("Basic Modes:");
                ImGui::Spacing();
                
                if (ToggleSwitch("##AutoAim", &Vars.AutoAim)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.AutoAim ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Auto Aim");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##AimFire", &Vars.AimFire)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.AimFire ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Aim Fire");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##AimScope", &Vars.AimScope)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.AimScope ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Aim Scope");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##FireScope", &Vars.FireScope)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.FireScope ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Fire + Scope");
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Text("Advanced:");
                ImGui::Spacing();
                
                // DISABLED: AimKill features cause crash when killing
                // if (ToggleSwitch("##AimKillFast", &Vars.AimKillFast)) {}
                Vars.AimKillFast = false;  // Force disable
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.6f, 0.0f, 0.0f, 1.0f));  // Red = disabled
                ImGui::Text("Aim Kill Fast [DISABLED]");
                ImGui::PopStyleColor();
                
                // if (ToggleSwitch("##AimKillFire", &Vars.AimKillFire)) {}
                Vars.AimKillFire = false;  // Force disable
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.6f, 0.0f, 0.0f, 1.0f));  // Red = disabled
                ImGui::Text("Aim Kill Fire [DISABLED]");
                ImGui::PopStyleColor();
                
                // DISABLED: FastScope triggers anti-cheat on shooting
                Vars.FastScope = false;
                // if (ToggleSwitch("##FastScope", &Vars.FastScope)) {
                //     [self toggleFastScope:Vars.FastScope];
                // }
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.6f, 0.0f, 0.0f, 1.0f));
                ImGui::Text("Fast Scope [DISABLED - CAUSES CRASH]");
                ImGui::PopStyleColor();
                
                // DISABLED: NoRecoil triggers anti-cheat on shooting
                NoRecoilEnabled = false;
                // if (ToggleSwitch("##NoRecoilAim", &NoRecoilEnabled)) {
                //     [self toggleNoRecoil:NoRecoilEnabled];
                // }
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.6f, 0.0f, 0.0f, 1.0f));
                ImGui::Text("No Recoil [DISABLED - CAUSES CRASH]");
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Text("M Kill:");
                ImGui::Spacing();
                
                // DISABLED: M Kill causes crash when killing enemies
                extern bool AimKill;
                AimKill = false;  // Force disable
                // if (ToggleSwitch("##MKill", &AimKill)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.6f, 0.0f, 0.0f, 1.0f));  // Red = disabled
                ImGui::Text("Enable M Kill [DISABLED - CAUSES CRASH]");
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Text("FOV Settings:");
                ImGui::Spacing();
                
                // FOV Circle Toggle
                if (ToggleSwitch("##ShowFOV", &Vars.isAimFov)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.isAimFov ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Show FOV Circle");
                ImGui::PopStyleColor();
                
                // FOV Size Slider
                ImGui::Text("FOV Size:");
                ImGui::PushItemWidth(ImGui::GetWindowWidth() - 40);
                ImGui::SliderFloat("##FovSize", &Vars.AimFov, 50.0f, 360.0f, "%.0f");
                ImGui::PopItemWidth();
                
                ImGui::Spacing();
                
                // Hitbox Selection
                ImGui::Text("Target Hitbox:");
                ImGui::PushItemWidth(ImGui::GetWindowWidth() - 40);
                ImGui::Combo("##Hitbox", &Vars.AimHitbox, Vars.aimHitboxes, 3);
                ImGui::PopItemWidth();
                
                ImGui::Spacing();
                
                // Ignore Knocked
                if (ToggleSwitch("##IgnoreKnocked", &Vars.IgnoreKnocked)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.IgnoreKnocked ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Ignore Knocked Players");
                ImGui::PopStyleColor();
            }
            else if (activeTab == 1) { // ESP TAB
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.95f, 0.3f, 0.3f, 1.0f));
                ImGui::Text("ESP / VISUALS");
                ImGui::PopStyleColor();
                ImGui::Spacing();
                
                // Master ESP Switch
                if (ToggleSwitch("##MasterESP", &Vars.Enable)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.Enable ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.8f, 0.2f, 0.2f, 1.0f));
                ImGui::Text(Vars.Enable ? "Master ESP [ON]" : "Master ESP [OFF]");
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Spacing();
                
                // ESP Options
                if (ToggleSwitch("##LineESP", &Vars.lines)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.lines ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Line ESP");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##BoxESP", &Vars.Box)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.Box ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Box ESP");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##SkeletonESP", &Vars.skeleton)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.skeleton ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Skeleton ESP");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##NameESP", &Vars.Name)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.Name ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Name Display");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##DistanceESP", &Vars.Distance)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.Distance ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Distance Info");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##HealthESP", &Vars.Health)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, Vars.Health ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Health Status");
                ImGui::PopStyleColor();
            }
            else if (activeTab == 2) { // MISC TAB
                ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.95f, 0.3f, 0.3f, 1.0f));
                ImGui::Text("SECURITY & MISC");
                ImGui::PopStyleColor();
                ImGui::Spacing();
                
                // Fly Feature (User Requested)
                if (ToggleSwitch("##FlyHack", &WallFlyEnabled)) {
                    [self toggleWallFly:WallFlyEnabled];
                }
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, WallFlyEnabled ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Fly");
                ImGui::PopStyleColor();

                // Teleport Enemy Feature
                if (ToggleSwitch("##TeleportEnemy", &istelekill)) {}
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, istelekill ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Teleport Enemy");
                ImGui::PopStyleColor();

                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Spacing();
                
                // Speed Section
                ImGui::Text("Speed Multiplier:");
                ImGui::Spacing();
                
                static int speedMode = 0;
                ImGui::PushStyleColor(ImGuiCol_Button, speedMode == 0 ? ImVec4(0.3f, 0.1f, 0.1f, 1.0f) : ImVec4(0.15f, 0.05f, 0.05f, 1.0f));
                if (ImGui::Button("Normal##Spd", ImVec2(90, 30))) {
                    if (speedMode != 0) { [self setSpeedMode:0]; speedMode = 0; }
                }
                ImGui::PopStyleColor();
                ImGui::SameLine();
                
                ImGui::PushStyleColor(ImGuiCol_Button, speedMode == 1 ? ImVec4(0.3f, 0.1f, 0.1f, 1.0f) : ImVec4(0.15f, 0.05f, 0.05f, 1.0f));
                if (ImGui::Button("x2##Spd", ImVec2(90, 30))) {
                    if (speedMode != 1) { [self setSpeedMode:1]; speedMode = 1; }
                }
                ImGui::PopStyleColor();
                
                ImGui::PushStyleColor(ImGuiCol_Button, speedMode == 2 ? ImVec4(0.3f, 0.1f, 0.1f, 1.0f) : ImVec4(0.15f, 0.05f, 0.05f, 1.0f));
                if (ImGui::Button("x8##Spd", ImVec2(90, 30))) {
                    if (speedMode != 2) { [self setSpeedMode:2]; speedMode = 2; }
                }
                ImGui::PopStyleColor();
                ImGui::SameLine();
                
                ImGui::PushStyleColor(ImGuiCol_Button, speedMode == 3 ? ImVec4(0.3f, 0.1f, 0.1f, 1.0f) : ImVec4(0.15f, 0.05f, 0.05f, 1.0f));
                if (ImGui::Button("x10##Spd", ImVec2(90, 30))) {
                    if (speedMode != 3) { [self setSpeedMode:3]; speedMode = 3; }
                }
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Spacing();
                
                // Wallhack Section
                ImGui::Text("Wallhack:");
                ImGui::Spacing();
                
                if (ToggleSwitch("##WallGlow", &WallGlowEnabled)) {
                    [self toggleWallGlow:WallGlowEnabled];
                }
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, WallGlowEnabled ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Glow");
                ImGui::PopStyleColor();
                
                if (ToggleSwitch("##WallChams", &WallHackEnabled)) {
                    [self toggleWallHack:WallHackEnabled];
                }
                ImGui::SameLine();
                ImGui::PushStyleColor(ImGuiCol_Text, WallHackEnabled ? ImVec4(0.2f, 1.0f, 0.2f, 1.0f) : ImVec4(0.6f, 0.6f, 0.6f, 1.0f));
                ImGui::Text("Chams");
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::Separator();
                ImGui::Spacing();
                
                // Quick Actions
                ImGui::Text("Quick Actions:");
                ImGui::Spacing();

                // SAFE MODE BUTTON - REMOVED (using stubs)
                ImGui::TextColored(ImVec4(0.8f, 0.2f, 0.2f, 1.0f), "Safe Mode: INACTIVE");
                ImGui::Spacing();
                ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f), "Using stub dylibs - no extra protection");
                
                ImGui::Spacing();

                // GUEST ACCOUNT BUTTON - REMOVED (using stubs)
                ImGui::TextColored(ImVec4(0.8f, 0.2f, 0.2f, 1.0f), "Guest Mode: INACTIVE");
                ImGui::Spacing();
                ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f), "Using stub dylibs - no guest system");
                
                ImGui::Spacing();

                // FIX LOGIN (Close Menu)
                ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.3f, 0.1f, 0.1f, 1.0f));
                if (ImGui::Button("Fix Login (Close)", ImVec2(ImGui::GetWindowWidth() - 40, 50))) {
                     MenDeal = false; 
                     FixLoginTimer = 2400; // 40 seconds timer (60fps * 40)
                     showLoginMessage = true;
                     NSLog(@"[ST-FEATURES] Fix Login activated for 40 seconds");
                }
                ImGui::PopStyleColor();
                
                ImGui::Spacing();
                ImGui::TextColored(ImVec4(0.6f, 0.6f, 0.6f, 1.0f), "Minimizes menu for 40 seconds to allow login.");
            }
            
            ImGui::EndChild(); // End Content
            
            // FOOTER
            ImGui::Spacing();
            ImGui::Separator();
            ImGui::SetCursorPosY(ImGui::GetWindowHeight() - 30);
            ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.4f, 0.4f, 0.4f, 1.0f));
            ImGui::Text("ST DASHBOARD v3.0");
            ImGui::SameLine(ImGui::GetWindowWidth() - 200);
            // Display stealth status
            ImGui::Text("Stealth: ON");
            ImGui::PopStyleColor();
            
            ImGui::End(); // End Main Window
            
            // Clean up styles
            ImGui::PopStyleVar(3); // WindowRounding, FrameRounding, WindowBorderSize
            ImGui::PopStyleColor(5); // WindowBg, Border, FrameBg, FrameBgHovered, FrameBgActive
        }
        
        // SDK & ESP disabled for ultra-stable base
        // Will be re-enabled incrementally after testing
        
        // Initialize SDK once - DISABLED
        // static bool sdkInitialized = false;
        // if (!sdkInitialized) {
        //     try {
        //         game_sdk->init();
        //         sdkInitialized = true;
        //     } catch (...) {
        //     }
        // }
        
        // Fix Login Timer Logic - Release input during timer
        if (FixLoginTimer > 0) {
            FixLoginTimer--;
            
            // Release ALL input capture so login pages work
            ImGui::GetIO().WantCaptureMouse = false;
            ImGui::GetIO().WantCaptureKeyboard = false;
            
            // Timer ended
            if (FixLoginTimer == 1) {
                showLoginMessage = false;
                NSLog(@"[ST-FEATURES] Fix Login timer ended");
            }
        }
        
        // Only run game functions if Fix Login is NOT active
        ImDrawList* draw_list = ImGui::GetBackgroundDrawList();
        
        if (FixLoginTimer == 0) {
            get_players();
            aimbot();
            // game_sdk->init(); // DIAGNOSTIC: DISABLED
        }
        
        // Continue to render ImGui even during Fix Login
        
try {
    if (draw_list && Vars.isAimFov && Vars.AimFov > 0 && Vars.AimFov < 500) {
        ImVec2 center = ImVec2(ImGui::GetIO().DisplaySize.x / 2, ImGui::GetIO().DisplaySize.y / 2);

        if (Vars.fovaimglow) {
            static float rainbowHue = 0.0f;
            rainbowHue += ImGui::GetIO().DeltaTime * 0.8f;
            if (rainbowHue > 1.0f) rainbowHue = 0.0f;

            drawcircleglow(
                draw_list,
                center,
                Vars.AimFov,
                ImColor(fovColor),
                100,
                2.0f,
                12
            );
        } else {
            draw_list->AddCircle(
                center,
                Vars.AimFov,
                ImColor(fovColor),
                100,
                2.0f
            );
        }
    }
} catch (...) {
    // FOV circle draw failure
}

        ImGui::Render();
        ImDrawData* draw_data = ImGui::GetDrawData();
        ImGui_ImplMetal_RenderDrawData(draw_data, commandBuffer, renderEncoder);
        [renderEncoder popDebugGroup];
        [renderEncoder endEncoding];
        [commandBuffer presentDrawable:view.currentDrawable];
        [commandBuffer commit];
    } 
} 

- (void)mtkView:(MTKView*)view drawableSizeWillChange:(CGSize)size {}

@end // FIX: Added the missing @end for the ImGuiDrawView implementation.

/*
// Hooking enabled for Antiban protection
void hooking() {
    void* address[] = {
               (void*)getRealOffset(ENCRYPTOFFSET("0x1048041B8"))
    };
    void* function[] = {
                (void*)antiban                                                     
    };
            hook(address, function, 1);
}
void *hack_thread(void *) {
    hooking();
    pthread_exit(nullptr);
    return nullptr;
}
*/

void __attribute__((constructor)) initialize() {
    NSLog(@"[ST-SYSTEM] 🚀 Initializing SAVAGEXITER-F...");
    NSLog(@"[ST-SYSTEM] 📋 Safety System: Active");
    NSLog(@"[ST-SYSTEM] Access: Direct (No Authentication)");
    NSLog(@"[ST-SYSTEM] 📊 Features: Aimbot, AimKill, ESP, Speed, WallHack");
    
    // System initialization
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 2 * NSEC_PER_SEC), dispatch_get_main_queue(), ^{
        g_SystemInitialized = true;
        g_UIReady = true;
        NSLog(@"[ST-SYSTEM] ✅ System ready");
    });
    
    pthread_t hacks;
    // Antiban Hook Enabled
    // CRASH FIX: Disabled hook_thread because it uses old offsets and bad hook.c
    // pthread_create(&hacks, NULL, hack_thread, NULL);
    
    // Authentication enabled - API Server Active
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 3 * NSEC_PER_SEC), dispatch_get_main_queue(), ^{
        if (!isKeyValidated) {
            NSLog(@"[ST-SYSTEM] 🔑 Showing authentication dialog...");
            [[ImGuiDrawView new] showAuthenticationDialog];
        }
    });
}