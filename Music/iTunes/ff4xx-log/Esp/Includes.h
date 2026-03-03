#include <MetalKit/MetalKit.h>
#include <Metal/Metal.h>
#include <iostream>
#include <UIKit/UIKit.h>
#include <vector>
#import "pthread.h"
#include <array>


#import "ImGuiDrawView.h"
#import "LoadView.h"
#import "FTNotificationIndicator.h"

#define kWidth  [UIScreen mainScreen].bounds.size.width
#define kHeight [UIScreen mainScreen].bounds.size.height
#define kScale [UIScreen mainScreen].scale

extern int FixLoginTimer; // Global timer for login fix
extern MenuInteraction* menuTouchView;
extern UIButton* InvisibleMenuButton;

extern UIButton* VisibleMenuButton;
extern UITextField* hideRecordTextfield;
extern UIView* hideRecordView;