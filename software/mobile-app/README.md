## Digital Card Mobile App
The digital card mobile app can store a personnel's digital card information, scan the NFC reader, and grant access to a door. To activate a personnel's card, they must log into their account, use Face ID or a passcode to activate the card, and put their phone over the NFC reader.

## Content
Folders:
* NFCReader &rarr; contains Swift files for final mobile application design
* NFCReaderTests &rarr; contains Swift files for testing separates parts of the mobile application
* NFCReaderUITests &rarr; conatins Swift files to test different parts of the UI design

File:
* NFCReader.xcodeproj &rarr; used to open Xcode and load the folders containing the Swift files

## Setup and Installation
**Requirements:** Mac, iPhone, and [Xcode IDE](https://developer.apple.com/xcode)

#### Apple Developer Account Required
Before using Xcode, an [active Apple Developer account](https://developer.apple.com/programs/) is required. Then, you will need to create a povisioning certificate for your Xcode to support libraries that can only be built with an active Developer Account.

*See how you can make a provisioning profile here: https://developer.apple.com/help/account/manage-profiles/create-a-development-provisioning-profile/*

#### How to install the application on your iPhone
1. Download the `mobile-app` folder and open the folder on Xcode.
2. Let Xcode index the source code files and build the application.
3. Enable Developer Mode on your iPhone through the Settings App &rarr; Privacy & Security, Developer Mode &rarr; Toggle on Devloper Mode. Restart your iPhone to complete the change.
4. Plug in your iPhone to your Mac.
5. Select the target build to build to your iPhone.
6. Run the build. Xcode will install the application on your iPhone.
7. Open the app on your iPhone. The app is successfully installed.
