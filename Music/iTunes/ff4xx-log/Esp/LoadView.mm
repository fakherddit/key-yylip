#import <UIKit/UIKit.h>
#include "Includes.h"
#include "../oxorany/oxorany_include.h"
#include "../Helper/Vector3.h"
#include "../Helper/Obfuscate.h"
#include "../IMGUI/imgui.h"
#include "../Helper/Mem.h"
#include "../Helper/Quaternion.h"
#include "../Helper/MonoString.h"

#ifndef Deg2Rad
#define Deg2Rad (3.14159265358979323846f / 180.0f)
#endif

extern ImFont* pixel_big;

#include "../Helper/SDK.h"
#import "menuIcon.h"
#define timer(sec) dispatch_after(dispatch_time(DISPATCH_TIME_NOW, sec * NSEC_PER_SEC), dispatch_get_main_queue(), ^
#import "LoadView.h"
@interface MenuLoad() <UIGestureRecognizerDelegate>
@property (nonatomic, strong) ImGuiDrawView *vna;

- (ImGuiDrawView*) GetImGuiView;
@end

static MenuLoad *extraInfo;

UIButton* InvisibleMenuButton;
UIButton* VisibleMenuButton;
MenuInteraction* menuTouchView;
UITextField* hideRecordTextfield;
UIView* hideRecordView;

bool StreamerMode = true;

@interface MenuInteraction()
@end

@implementation MenuInteraction

- (UIView *)hitTest:(CGPoint)point withEvent:(UIEvent *)event {
    if (FixLoginTimer > 0) return nil; // Pass ALL touches through when Fix Login is active
    return [super hitTest:point withEvent:event];
}

- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    [[extraInfo GetImGuiView] updateIOWithTouchEvent:event];
}
- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    [[extraInfo GetImGuiView] updateIOWithTouchEvent:event];
}
- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    [[extraInfo GetImGuiView] updateIOWithTouchEvent:event];
}
- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(UIEvent *)event {
    [[extraInfo GetImGuiView] updateIOWithTouchEvent:event];
}
// Allow touches to pass through if checking hit test, but here we want to capture.
// However, adding hitTest override can help if we want to be selective.
@end

@implementation MenuLoad

- (ImGuiDrawView*) GetImGuiView
{
    return _vna;
}


static void didFinishLaunching(CFNotificationCenterRef center, void *observer, CFStringRef name, const void *object, CFDictionaryRef info)
{   
    // SAFEMODE: REMOVED TELEGRAM URL OPEN (Crash Risk)
    
    // Increased timer to 10 seconds to ensure Unity is fully loaded
    timer(10) {
        NSLog(@"[SAFE-LOAD] ⏳ Attempting to load menu...");
        
        // Initialize GameSDK NOW (Safe Zone)
        if (game_sdk) {
           game_sdk->init();
        }
        
        extraInfo = [MenuLoad new];
        [extraInfo checkAndExecutePaidBlock];
    });
    
}


 - (void)checkAndExecutePaidBlock {

      

        [extraInfo initTapGes];
      

}
//         timer(5) {
//             [extraInfo checkAndExecutePaidBlock];
//         });
//     }
// }

__attribute__((constructor)) static void initialize()
{
    CFNotificationCenterAddObserver(CFNotificationCenterGetLocalCenter(), NULL, &didFinishLaunching, (CFStringRef)UIApplicationDidFinishLaunchingNotification, NULL, CFNotificationSuspensionBehaviorDrop);
}

- (void)initTapGes {
    
    UIView *mainView = [UIApplication sharedApplication].windows[0].rootViewController.view;
    hideRecordTextfield = [[UITextField alloc] init];
    hideRecordView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, UIScreen.mainScreen.bounds.size.width, UIScreen.mainScreen.bounds.size.height)];
    [hideRecordView setBackgroundColor:[UIColor clearColor]];
    [hideRecordView setUserInteractionEnabled:YES];
    hideRecordTextfield.secureTextEntry = true;
    [hideRecordView addSubview:hideRecordTextfield];
    CALayer *layer = hideRecordTextfield.layer;

    if ([layer.sublayers.firstObject.delegate isKindOfClass:[UIView class]]) {
        hideRecordView = (UIView *)layer.sublayers.firstObject.delegate;
    } else {
        hideRecordView = nil;
    }

    [[UIApplication sharedApplication].keyWindow addSubview:hideRecordView];

    if (!_vna) {
        ImGuiDrawView *vc = [[ImGuiDrawView alloc] init];
        _vna = vc;
    }

    // Restore MenuTouchView instantiation
    menuTouchView = [[MenuInteraction alloc] initWithFrame:mainView.frame];
    // Add to keyWindow to ensure it's on top but below ImGui
    [[UIApplication sharedApplication].keyWindow addSubview:menuTouchView];

    [ImGuiDrawView showChange:false]; // Start HIDDEN - gesture will show it
    [[UIApplication sharedApplication].keyWindow addSubview:_vna.view];

    UITapGestureRecognizer *tapGesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
    tapGesture.numberOfTapsRequired = 2; // Double tap (TAP TWICE with 3 fingers)
    tapGesture.numberOfTouchesRequired = 3; // Three fingers
    tapGesture.cancelsTouchesInView = NO; // CRITICAL: Don't eat the touches
    tapGesture.delegate = self; // Set delegate for simultaneous recognition
    
    [[UIApplication sharedApplication].keyWindow addGestureRecognizer:tapGesture];
}

- (void)handleTap:(UITapGestureRecognizer *)sender {
    if (sender.state == UIGestureRecognizerStateEnded) {
        NSLog(@"[ST-GESTURE] ✅ 3-Finger Double-Tap detected! Toggling menu...");
        [ImGuiDrawView showChange:![ImGuiDrawView isMenuShowing]];
    }
}

// UIGestureRecognizerDelegate implementation
- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer {
    return YES;
}

@end