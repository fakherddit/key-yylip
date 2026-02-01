//
//  APIKey.h
//
//  Created by PhatPham on 2025/05/31.
//
#import <Foundation/Foundation.h>
@interface PPAPIKey : NSObject

- (void)loading:(void (^)(void))execute;
- (void)setPackageToken:(NSString *)token;
- (void)setAppVersion:(NSString *)newAppVersion;
- (void)setENLanguage:(BOOL)value;
- (void)exitKey;//Call this function to Clear key
- (void)copyKey;//Call this function to Copy key to clipboard
- (void)showCSAL:(NSString *)title message:(NSString *)message apiKeyLabel:(NSString *)apiKeyLabel doneTime:(NSInteger)doneTime;
- (void)cdt:(void (^)(NSString *a))completion;

- (NSString*) getKey;
- (NSString*) getKeyExpire;
- (NSString*) getKeyAmount;
- (NSString*) getUDID;
- (NSString*) getDeviceName;
- (NSString*) getiOSVersion;
- (NSString*) getAppVersion;
- (NSString*) getAppName;
- (NSString*) getAppBundle;
- (NSString*) getJailbreakStatus;


@end