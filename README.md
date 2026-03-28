# CallerID

An Android application that identifies unknown callers in real time by querying the [nieznany-numer.pl](https://www.nieznany-numer.pl/) database. When a call comes in, a draggable overlay displays the caller's community rating, search history, and user comments, with a one-tap option to reject negatively-rated calls.

![Android](https://img.shields.io/badge/Android-21%2B-3DDC84?logo=android&logoColor=white)
![Java](https://img.shields.io/badge/Java-8-007396?logo=openjdk&logoColor=white)
![Gradle](https://img.shields.io/badge/Gradle-8.x-02303A?logo=gradle&logoColor=white)
![API](https://img.shields.io/badge/Target%20SDK-36-blue)

## Features

- **Real-time caller identification** via BroadcastReceiver that intercepts `PHONE_STATE` intents when the phone rings
- **Floating overlay** displayed on top of other apps, showing caller number, rating badge, and details while the phone is ringing
- **Community ratings** with color-coded badges: positive (green), neutral (yellow), negative (red), and unknown (gray)
- **One-tap call rejection** button that appears automatically for negatively-rated numbers, using TelecomManager on Android P+ with legacy reflection fallback
- **Draggable overlay** that can be repositioned by touch during an active call
- **Persistent notification** keeping the service alive in the background
- **Multi-language support** with localized strings for English, Polish, French, and Russian
- **API integration** fetching rating counts, search history, comment count, last-searched date, and user comments from the backend

## Screenshots

![Screenshot 1](https://user-images.githubusercontent.com/17749811/152438154-43c6c848-16ce-42d4-b670-bb1a7e698cc7.jpg)

![Screenshot 2](https://user-images.githubusercontent.com/17749811/152438173-5759df2b-bd1f-4c15-aead-47ab282ab81e.jpg)

## Architecture

The app follows a receiver-service-provider pattern:

1. **PhoneStateReceiver** -- A `BroadcastReceiver` registered for `android.intent.action.PHONE_STATE`. On `RINGING`, it extracts the incoming number and starts `OverlayService`. On `IDLE` or `OFFHOOK`, it stops the service.
2. **OverlayService** -- Creates a `TYPE_APPLICATION_OVERLAY` window with the caller info layout. Handles drag gestures, close/reject buttons, and manages the overlay lifecycle.
3. **PhoneNumberProvider** -- Performs an asynchronous HTTP GET to the API endpoint, parses the JSON response, and delivers rating, counts, and comments via a callback interface.
4. **MainActivity** -- Handles permission requests (phone state, call log, overlay, answer calls), creates the notification channel, and shows a persistent notification.

## Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| [AndroidX AppCompat](https://developer.android.com/jetpack/androidx/releases/appcompat) | 1.7.1 | Backward-compatible Activity and UI components |
| [Material Components](https://github.com/material-components/material-components-android) | 1.13.0 | Material Design theming |
| [ConstraintLayout](https://developer.android.com/reference/androidx/constraintlayout/widget/ConstraintLayout) | 2.2.1 | Flexible layout manager |
| [JUnit](https://junit.org/junit4/) | 4.13.2 | Unit testing |
| [Espresso](https://developer.android.com/training/testing/espresso) | 3.7.0 | UI testing |

## Required Permissions

| Permission | Purpose |
|------------|---------|
| `INTERNET` | Query the phone number lookup API |
| `READ_PHONE_STATE` | Detect incoming calls |
| `READ_CALL_LOG` | Access caller number on Android 9+ |
| `READ_PHONE_NUMBERS` | Read phone number details |
| `SYSTEM_ALERT_WINDOW` | Display overlay on top of other apps |
| `ANSWER_PHONE_CALLS` | Reject calls programmatically (Android 9+) |

## Building

### Prerequisites

- Android Studio (Arctic Fox or later)
- JDK 8+
- Android SDK with API level 36

### Steps

```bash
git clone <repository-url>
cd CallerID
```

Open the project in Android Studio, sync Gradle, and run on a device or emulator.

Alternatively, build from the command line:

```bash
./gradlew assembleDebug
```

The APK will be located at `app/build/outputs/apk/debug/`.

## Project Structure

```
CallerID/
├── app/
│   ├── build.gradle                          # App-level build configuration
│   ├── proguard-rules.pro                    # ProGuard rules
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml           # Permissions, receiver, service declarations
│       │   ├── java/com/example/nieznany_numer/
│       │   │   ├── MainActivity.java         # Entry point, permissions, notification channel
│       │   │   ├── PhoneStateReceiver.java   # BroadcastReceiver for call state changes
│       │   │   ├── OverlayService.java       # Floating window with caller info and controls
│       │   │   ├── PhoneNumberProvider.java  # Async API client for number lookup
│       │   │   └── Notification.java         # Notification activity
│       │   └── res/
│       │       ├── layout/
│       │       │   ├── activity_main.xml     # Main activity layout
│       │       │   ├── overlay_caller.xml    # Floating overlay layout
│       │       │   └── notification.xml      # Notification layout
│       │       ├── drawable/                 # Rating badges and overlay backgrounds
│       │       ├── values/                   # Default strings and themes
│       │       ├── values-en/                # English localization
│       │       ├── values-pl/                # Polish localization
│       │       ├── values-fr/                # French localization
│       │       └── values-ru/                # Russian localization
│       └── test/                             # Unit tests
├── settings.gradle
└── README.md
```

## Configuration

The API endpoint is defined in `PhoneNumberProvider.java`:

```java
private static final String API_BASE = "https://your-server.com/api/v1/numbers/";
```

Replace this URL with your own backend or a compatible phone number lookup API before building.

## License

This project is provided as-is for educational purposes.
