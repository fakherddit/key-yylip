export THEOS=/home/fakherddin/theos
export TARGET=iphone:clang:16.5:9.0
export ARCHS=arm64

TWEAK_NAME = SavageProtection

# REMOVED protection.mm to isolate crash
# ErzoBypass.mm caused crashes because offsets are version-dependent.
# FIXED BYPASS: Included protection.mm (Antiban) but disabled Helper verification
# REMOVED protection.mm AGAIN - Crash 0.0001s
SavageProtection_FILES = savagexiter.mm $(wildcard Esp/*.mm) $(wildcard Esp/*.m) $(wildcard IMGUI/*.cpp) $(wildcard IMGUI/*.mm)

# Use strict flags but allow C++17
SavageProtection_CFLAGS = -fobjc-arc -Wno-error -Wno-unused-variable -Wno-unused-function -O3 -fvisibility=hidden
SavageProtection_CCFLAGS = -std=c++17 -fno-rtti -fvisibility=hidden -DNDEBUG
SavageProtection_FRAMEWORKS = UIKit Foundation CoreGraphics QuartzCore Metal MetalKit
SavageProtection_LIBRARIES = substrate
# Merge JRMemory STATICALLY so we only have ONE dylib file
SavageProtection_LDFLAGS = -F.
# SavageProtection_LDFLAGS += -force_load JRMemory.framework/JRMemory

include $(THEOS)/makefiles/common.mk
include $(THEOS)/makefiles/tweak.mk
