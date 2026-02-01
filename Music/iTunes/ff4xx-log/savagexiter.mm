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
#import "JRMemory.framework/Headers/MemScan.h"
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
// #include "ban.cpp" - Removed as per request
ImFont* verdana_smol;
ImFont* pixel_big = {};
ImFont* pixel_smol = {};
#include "Helper/Obfuscate.h"
#import "Helper/NewHooks.h"
#import "Helper/Bypass.h"
// #import "Helper/AimKill.h" // AimKill Logic

// --- BYPASS LOGIC (Integrated) ---

bool g_BypassAttempted = false;
void ActivateBypass() {
    if(g_BypassAttempted) return;
    g_BypassAttempted = true;
    
    ApplyErzoBypass();
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

static bool MenDeal = true;
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

// Key Validation System
static bool isKeyValidated = false;
static char keyInput[128] = "";
static std::string validationMessage = "";
static NSString* serverURL = @"https://your-app-name.onrender.com/validate"; // Change to your Render URL

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

bool antiban(void *instance) {
    return false;
}


- (void)setSpeedMode:(int)mode {
    static dispatch_once_t onceToken;
    static vector<void*> results;
    
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x200000000};
    
    // Mode 0: Off, 1: x2, 2: x8, 3: x10
    if (mode > 0) {
        // Only scan if results are empty (this logic relies on reset when mode 0)
        if (results.empty()) {
            uint64_t search = 4397530849764387586;
            engine->JRScanMemory(range, &search, JR_Search_Type_ULong);
            results = engine->getAllResults();
        }
        
        uint64_t modify = 4397530849764387586;
        if (mode == 1) modify = 4366458311853765201; // x2
        if (mode == 2) modify = 4366458311853765201; // x8 (Placeholder, reuse x2 or find actual)
        if (mode == 3) modify = 4366458311853685297; // x10 (From SKAM 7WAY source)

        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_ULong);
        }
    } else {
        uint64_t modify = 4397530849764387586; // Original value
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_ULong);
        }
        results.clear();
    }
    delete engine;
}

- (void)toggleFastScope:(BOOL)enable {
    static dispatch_once_t onceToken;
    static vector<void*> results;
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x160000000};
    
    if (enable) {
        dispatch_once(&onceToken, ^{
            float search = 0.03f;
            engine->JRScanMemory(range, &search, JR_Search_Type_Float);
            results = engine->getAllResults();
        });
        float modify = 10.0f;
        for(int i=0; i<results.size(); i++) engine->JRWriteMemory((unsigned long long)results[i], &modify, JR_Search_Type_Float);
    } else {
        float modify = 0.03f;
        for(int i=0; i<results.size(); i++) engine->JRWriteMemory((unsigned long long)results[i], &modify, JR_Search_Type_Float);
        onceToken = 0;
        results.clear();
    }
    delete engine;
}

- (void)toggleTracking:(BOOL)enable {
     static dispatch_once_t onceToken;
    static vector<void*> results;
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x160000000};
    
    if (enable) {
        dispatch_once(&onceToken, ^{
            float search = 0.15f;
            engine->JRScanMemory(range, &search, JR_Search_Type_Float);
            results = engine->getAllResults();
        });
        float modify = 80.0f;
        for(int i=0; i<results.size(); i++) engine->JRWriteMemory((unsigned long long)results[i], &modify, JR_Search_Type_Float);
    } else {
        float modify = 0.15f;
        for(int i=0; i<results.size(); i++) engine->JRWriteMemory((unsigned long long)results[i], &modify, JR_Search_Type_Float);
        onceToken = 0;
        results.clear();
    }
    delete engine;
}

- (void)toggleNoRecoil:(BOOL)enable {
    static dispatch_once_t onceToken;
    static std::vector<void*> results; 

    JRMemoryEngine* engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = { 0x100000000, 0x200000000 }; 

    if (enable) {
        dispatch_once(&onceToken, ^{
            uint64_t search = 1016018816; 
            engine->result->resultBuffer.clear();
            engine->result->count = 0;
            engine->JRScanMemory(range, &search, JR_Search_Type_ULong);
            results = engine->getAllResults();
        });

        uint64_t modify = 0; 
        for (size_t i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_ULong);
        }
    } else {
        uint64_t modify = 1016018816; 
        for (size_t i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_ULong);
        }
        onceToken = 0; 
        results.clear();
    }

    delete engine;
}

- (void)toggleWallGlow:(BOOL)enable {
    static dispatch_once_t onceToken;
    static vector<void*> results;
    
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x160000000};
    
    if (enable) {
        dispatch_once(&onceToken, ^{
            float search = 1.22f;
            engine->JRScanMemory(range, &search, JR_Search_Type_Float);
            results = engine->getAllResults();
        });

        
        float modify = 965.0f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
    } else {
        float modify = 1.22f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
        onceToken = 0;
        results.clear();
    }
    delete engine;
}



- (void)toggleWallFly:(BOOL)enable {
    static dispatch_once_t onceToken;
    static vector<void*> results;
    
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x160000000};
    
    if (enable) {
        dispatch_once(&onceToken, ^{
            float search = 1.5f;
            engine->JRScanMemory(range, &search, JR_Search_Type_Float);
            results = engine->getAllResults();
        });
        
        float modify = 900.0f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
    } else {
        float modify = 1.5f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
        onceToken = 0;
        results.clear();
    }
    delete engine;
}

- (void)toggleWallHack:(BOOL)enable {
    static dispatch_once_t onceToken;
    static vector<void*> results;
    
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x160000000};
    
    if (enable) {
        dispatch_once(&onceToken, ^{
            float search = 1.5f;
            engine->JRScanMemory(range, &search, JR_Search_Type_Float);
            results = engine->getAllResults();
        });
        
        float modify = 965.0f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
    } else {
        float modify = 1.5f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
        onceToken = 0;
        results.clear();
    }
    delete engine;
}

- (void)toggleScope:(BOOL)enable {
    static dispatch_once_t onceToken;
    static vector<void*> results;
    
    JRMemoryEngine *engine = new JRMemoryEngine(mach_task_self());
    AddrRange range = {0x100000000, 0x160000000};
    
    if (enable) {
        dispatch_once(&onceToken, ^{
            float search = 0.03f;
            engine->JRScanMemory(range, &search, JR_Search_Type_Float);
            results = engine->getAllResults();
        });
        
        float modify = 10.0f;
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
    } else {
        float modify = 0.03f; // Original value
        for(int i = 0; i < results.size(); i++) {
            engine->JRWriteMemory((unsigned long long)(results[i]), &modify, JR_Search_Type_Float);
        }
        onceToken = 0;
        results.clear();
    }
    delete engine;
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

    if (MenDeal == true) 
    {
        [self.view setUserInteractionEnabled:YES];
        // [self.view.superview setUserInteractionEnabled:YES]; // KEEP commented - enables interaction on RootView (Game)
        [menuTouchView setUserInteractionEnabled:YES];          // UNCOMMENTED - enables interaction on Overlay (Menu)
    } 
    else if (MenDeal == false) 
    {
        [self.view setUserInteractionEnabled:NO];
        // [self.view.superview setUserInteractionEnabled:NO]; // KEEP commented - would disable interaction on RootView (Game) -> Frozen Screen
        [menuTouchView setUserInteractionEnabled:NO];          // UNCOMMENTED - disables interaction on Overlay (Menu) -> Pass through to Game
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

        // Logic for Fix Login Timer
        if (FixLoginTimer > 0) {
            static CFTimeInterval lastTime = 0;
            CFTimeInterval currentTime = CACurrentMediaTime();
            if (currentTime - lastTime >= 1.0) {
               FixLoginTimer--;
               if (FixLoginTimer <= 0) {
                   FixLoginTimer = 0;
                   MenDeal = true;
                   [ImGuiDrawView showChange:true];
               }
               lastTime = currentTime;
            }
        }

        if (MenDeal == true)
        {
            ImGui::SetNextWindowSize(ImVec2(550, 400), ImGuiCond_FirstUseEver); 
            // Theme Colors match the image (Black background, Red Accent)
            ImGui::PushStyleColor(ImGuiCol_WindowBg, ImVec4(0.05f, 0.05f, 0.05f, 0.95f));
            ImGui::PushStyleColor(ImGuiCol_Border, ImVec4(1.0f, 0.0f, 0.0f, 0.5f));
            
            ImGui::Begin("ST CHEATS", &MenDeal, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoResize);
            
            // --- HEADER ---
            // ImGui::PushFont(verdanab); // Assuming bold font available or default
            ImGui::TextColored(ImVec4(1, 0, 0, 1), "ST FAMILY");
            // ImGui::PopFont();
            ImGui::SameLine();
            
            // Determine session ID (mock) and FPS
            char sessionInfo[100];
            sprintf(sessionInfo, "                                                      ST CHEATS | Session: C931O4CY6NPZ | FPS: %.1f", ImGui::GetIO().Framerate);
            ImGui::Text("%s", sessionInfo);
            
            ImGui::Separator();
            ImGui::Spacing();

            // --- LAYOUT ---
            ImGui::Columns(2, "MainLayout", true);
            ImGui::SetColumnWidth(0, 180); // Left Sidebar Width

            static int activeTab = 0;
            // style for buttons
            ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0, 0, 0, 0)); // Transparent
            ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(0.2f, 0.0f, 0.0f, 0.5f));
            ImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(0.4f, 0.0f, 0.0f, 0.8f));
            ImGui::PushStyleColor(ImGuiCol_Border, ImVec4(1, 0, 0, 1));
            ImGui::PushStyleVar(ImGuiStyleVar_FrameBorderSize, 1.0f);
            ImGui::PushStyleVar(ImGuiStyleVar_FrameRounding, 5.0f);

            if (ImGui::Button("   Aimbot   ", ImVec2(160, 45))) activeTab = 0;
            ImGui::Spacing();
            if (ImGui::Button("   Visuals  ", ImVec2(160, 45))) activeTab = 1;
            ImGui::Spacing();
            if (ImGui::Button("   Misc     ", ImVec2(160, 45))) activeTab = 2;
            ImGui::Spacing();
            if (ImGui::Button("   Settings ", ImVec2(160, 45))) activeTab = 3;

            ImGui::PopStyleVar(2);
            ImGui::PopStyleColor(4);

            // Footer in Sidebar
            ImGui::SetCursorPosY(ImGui::GetWindowHeight() - 30);
            ImGui::TextDisabled("ST GEN 3");

            ImGui::NextColumn();

            // --- RIGHT PANEL CONTENT ---
            ImGui::BeginChild("ContentRegion", ImVec2(0, 0), false, ImGuiWindowFlags_None);
            
            if (activeTab == 0) { // AIMBOT
                ImGui::TextColored(ImVec4(1, 0.3f, 0.0f, 1), "AIMBOT / KILL");
                ImGui::Spacing();

                // MASTER SWITCH - Only enables system, no direct effect
                ToggleSwitch("##MasterAimBot", &Vars.Aimbot);
                ImGui::SameLine();
                ImGui::TextColored(ImVec4(1, 0.8f, 0, 1), "Aim Bot");
                ImGui::Spacing();
                
                // Disable all sub-options if master is off
                if (!Vars.Aimbot) {
                    ImGui::PushStyleVar(ImGuiStyleVar_Alpha, 0.3f);
                    ImGui::BeginDisabled();
                }
                
                ImGui::Text("Standard Modes:");
                ImGui::Spacing();
                
                ToggleSwitch("##AutoAim", &Vars.AutoAim);
                ImGui::SameLine();
                ImGui::Text("Auto Aim");
                
                ToggleSwitch("##AimFire", &Vars.AimFire);
                ImGui::SameLine();
                ImGui::Text("Aim Fire");
                
                ToggleSwitch("##AimScope", &Vars.AimScope);
                ImGui::SameLine();
                ImGui::Text("Aim Scope");
                
                ToggleSwitch("##FireScope", &Vars.FireScope);
                ImGui::SameLine();
                ImGui::Text("Fire + Scope");
                
                ImGui::Spacing();
                ImGui::Text("Rage / Kill Modes:");
                ImGui::Spacing();
                
                ToggleSwitch("##AimKillFast", &Vars.AimKillFast);
                ImGui::SameLine();
                ImGui::Text("Aim Kill Fast");
                
                ToggleSwitch("##AimKillFire", &Vars.AimKillFire);
                ImGui::SameLine();
                ImGui::Text("Aim Kill Fire");
                
                ToggleSwitch("##FastScope", &Vars.FastScope);
                ImGui::SameLine();
                ImGui::Text("Fast Scope");
                if (ImGui::IsItemClicked()) [self toggleFastScope:Vars.FastScope];
                
                ImGui::Spacing();
                ImGui::Text("Stability:");
                ImGui::Spacing();
                
                ToggleSwitch("##NoRecoil", &NoRecoilEnabled);
                ImGui::SameLine();
                ImGui::Text("No Recoil");
                if (ImGui::IsItemClicked()) [self toggleNoRecoil:NoRecoilEnabled];

                if (!Vars.Aimbot) {
                    ImGui::EndDisabled();
                    ImGui::PopStyleVar();
                }
                
                ImGui::Spacing();
                ImGui::Text("Bullet Speed:");
                const char* speeds[] = { "x10", "x50", "x100" };
                static int currentSpeed = 1; 
                ImGui::PushItemWidth(300);
                ImGui::Combo("##BulletSpeed", &currentSpeed, speeds, IM_ARRAYSIZE(speeds));
                ImGui::PopItemWidth();

                ImGui::Spacing();
                ImGui::Text("Target Hitbox:");
                ImGui::PushItemWidth(300);
                ImGui::Combo("##Hitbox", &Vars.AimHitbox, Vars.aimHitboxes, 3);
                ImGui::PopItemWidth();

                ImGui::Spacing();
                ImGui::Checkbox("Show FOV circle", &Vars.isAimFov);
                
                ImGui::PushItemWidth(250);
                ImGui::SliderFloat("##FovSize", &Vars.AimFov, 0.0f, 360.0f, "%.3f");
                ImGui::PopItemWidth();
                ImGui::SameLine();
                ImGui::Text("FOV Size");

                ImGui::Spacing();
                ImGui::Checkbox("Ignore Knocked", &Vars.IgnoreKnocked);
            }
            else if (activeTab == 1) { // VISUALS
                ImGui::TextColored(ImVec4(1, 0.3f, 0.0f, 1), "VISUALS");
                ImGui::Spacing();
                
                ImGui::Checkbox("Enemy ESP Master", &Vars.Enable);
                ImGui::Spacing();
                ImGui::Spacing();
                ImGui::Checkbox("Line ESP", &Vars.lines);
                ImGui::Checkbox("Box ESP", &Vars.Box);
                ImGui::Checkbox("Skeleton ESP", &Vars.skeleton);
                ImGui::Checkbox("Name Display", &Vars.Name);
                ImGui::Checkbox("Distance Info", &Vars.Distance);
                ImGui::Checkbox("Health Status", &Vars.Health);
            }
            else if (activeTab == 2) { // MISC
                 ImGui::TextColored(ImVec4(1, 0.3f, 0.0f, 1), "[ MISC ]");
                 ImGui::Separator();
                 ImGui::Spacing();

                 ImGui::Text("Speed Multiplier:");
                 static int speedMode = 0; 
                 if (ImGui::RadioButton("Normal", speedMode == 0)) {
                     if (speedMode != 0) { [self setSpeedMode:0]; }
                     speedMode = 0;
                 }
                 ImGui::SameLine();
                 if (ImGui::RadioButton("x2", speedMode == 1)) {
                     if (speedMode != 1) { [self setSpeedMode:1]; }
                     speedMode = 1;
                 }
                 ImGui::SameLine();
                 if (ImGui::RadioButton("x8", speedMode == 2)) {
                      if (speedMode != 2) { [self setSpeedMode:2]; } 
                      speedMode = 2;
                 }
                 ImGui::SameLine();
                 if (ImGui::RadioButton("x10", speedMode == 3)) {
                      if (speedMode != 3) { [self setSpeedMode:3]; } 
                      speedMode = 3;
                 }
                 
                 ImGui::Spacing();
                 ImGui::Separator();
                 ImGui::TextColored(ImVec4(1, 0, 0, 1), "[ ANTI-BAN ]");
                 if (!g_BypassAttempted) {
                      ImGui::TextDisabled(" (Initializing...)");
                 } else {
                      ImGui::TextColored(ImVec4(0, 1, 0, 1), " (Bypass Active)");
                 }

                 ImGui::Spacing();
                 ImGui::Separator();
                 
                 ImGui::Checkbox("No Recoil", &NoRecoilEnabled);
                 if (ImGui::IsItemClicked()) [self toggleNoRecoil:!NoRecoilEnabled];
                 
                 if (ImGui::Checkbox("Wallhack (Glow)", &WallGlowEnabled)) {
                     [self toggleWallGlow:WallGlowEnabled];
                 }
                 
                 if (ImGui::Checkbox("Wallhack (Chams)", &WallHackEnabled)) {
                     [self toggleWallHack:WallHackEnabled];
                 }
            }
            else if (activeTab == 3) { // SETTINGS
                ImGui::TextColored(ImVec4(1, 0, 0, 1), "EMERGENCY PROTOCOL");
                ImGui::Separator();
                ImGui::Spacing();
                
                // Panic Button Styled Red
                ImGui::PushStyleColor(ImGuiCol_Button, ImVec4(0.8f, 0.0f, 0.0f, 1.0f));
                ImGui::PushStyleColor(ImGuiCol_ButtonHovered, ImVec4(1.0f, 0.0f, 0.0f, 1.0f));
                ImGui::PushStyleColor(ImGuiCol_ButtonActive, ImVec4(0.6f, 0.0f, 0.0f, 1.0f));
                if (ImGui::Button("PANIC: DISABLE ALL & HIDE", ImVec2(-1, 50))) {
                    MenDeal = false;
                    Vars.Enable = false;
                    Vars.Aimbot = false;
                    Vars.AimKillFast = false;
                    Vars.AimKillFire = false;
                    [ImGuiDrawView showChange:false];
                }
                ImGui::PopStyleColor(3);

                ImGui::Spacing();
                ImGui::Spacing();
                ImGui::TextColored(ImVec4(0, 1, 0, 1), "[ SECURITY ]");
                ImGui::SameLine();
                ImGui::TextDisabled("(Always keep ON)");
                
                ImGui::Spacing();
                ImGui::Spacing();
                ImGui::Text("Menu Colors");
                static bool saveSettings = false;
                static bool loadSettings = false;
                static bool fixLogin = false;
                
                ImGui::ColorEdit3("##ThemeColor", (float*)&userColor, ImGuiColorEditFlags_NoInputs | ImGuiColorEditFlags_NoLabel);
                ImGui::SameLine();
                ImGui::Text("Theme Color");
                
                ImGui::ColorEdit3("##FOVColor", (float*)&fovColor, ImGuiColorEditFlags_NoInputs | ImGuiColorEditFlags_NoLabel);
                ImGui::SameLine();
                ImGui::Text("FOV Color");

                ImGui::Spacing();
                ImGui::Spacing();
                
                ToggleSwitch("##SaveSettings", &saveSettings);
                ImGui::SameLine();
                ImGui::Text("Save Settings");
                
                ToggleSwitch("##LoadSettings", &loadSettings);
                ImGui::SameLine();
                ImGui::Text("Load Settings");
                
                ImGui::Spacing();
                if (ToggleSwitch("##FixLogin", &fixLogin)) {
                    if (fixLogin) {
                        MenDeal = false;
                        FixLoginTimer = 40;
                        [ImGuiDrawView showChange:false];
                    }
                }
                ImGui::SameLine();
                ImGui::Text("FIX LOGIN (40s)");
            }

            ImGui::EndChild();
            ImGui::EndColumns();
            ImGui::End();

            ImGui::PopStyleColor(2); // Pop WindowBg and Border
        }
        
        ImDrawList* draw_list = ImGui::GetBackgroundDrawList();
        get_players();
        // aimbot(); 
        
        game_sdk->init();
        
if (Vars.isAimFov && Vars.AimFov > 0) {
    ImVec2 center = ImVec2(ImGui::GetIO().DisplaySize.x / 2, ImGui::GetIO().DisplaySize.y / 2);

    if (Vars.fovaimglow) {
        static float rainbowHue = 0.0f;
        rainbowHue += ImGui::GetIO().DeltaTime * 0.8f;
        if (rainbowHue > 1.0f) rainbowHue = 0.0f;

        drawcircleglow(
            draw_list,
            center,
            Vars.AimFov,
            ImColor(fovColor), // usa cor configurada
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
ActivateBypass(); // Auto-activate bypass
    
    sleep(5);
    hooking();
    pthread_exit(nullptr);
    return nullptr;
}

void __attribute__((constructor)) initialize() {
    pthread_t hacks;
    pthread_create(&hacks, NULL, hack_thread, NULL); 
}
@end