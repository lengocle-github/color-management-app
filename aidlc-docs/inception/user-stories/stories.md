# User Stories — Colorful iGame RGB Controller

## Epic 1: GPU Detection & Connection

### US-01: Detect GPU on Launch
**As** Lê, **I want** the app to automatically detect my Colorful iGame RTX 5070 when launched, **so that** I can immediately start controlling the LED.

**Acceptance Criteria:**
- Given the app is launched, when GPU is connected and driver is working, then the app shows GPU name and status "Connected"
- Given the GPU is not detected, when the app launches, then it shows error message with retry button and troubleshooting tips
- Given detection fails, when user clicks retry, then the app attempts detection again

### US-02: Auto-Reconnect on Disconnect
**As** Lê, **I want** the app to auto-retry when GPU connection is lost, **so that** I don't have to manually restart the app.

**Acceptance Criteria:**
- Given GPU was connected but disconnects, when connection is lost, then app shows "Reconnecting..." and retries every 5 seconds
- Given auto-retry succeeds, when GPU is detected again, then app restores previous LED state

### US-02B: Override & Clear External RGB Settings
**As** Lê, **I want** the app to clear/override any RGB settings that other software (iGame Center, OpenRGB, etc.) has previously applied to the GPU, **so that** my app has exclusive control over the LED without being affected by stale settings from other programs.

**Acceptance Criteria:**
- Given another RGB app has previously set a color/effect on the GPU, when my app launches and takes control, then the previous settings are cleared and replaced by my app's settings
- Given my app is running, when another app tries to set LED color, then my app can re-assert control (override lock)
- Given the override operation is performed, when clearing external settings, then no harm is done to the GPU hardware (only LED controller registers are affected, not GPU core/memory)

### US-02C: Exclusive Control Mode
**As** Lê, **I want** an "Exclusive Control" option that prevents other RGB software from changing my LED settings while my app is active, **so that** my colors don't get overwritten unexpectedly.

**Acceptance Criteria:**
- Given exclusive mode is enabled, when my app is active, then it periodically re-writes LED state to prevent external overrides
- Given exclusive mode is enabled, when I disable it, then other apps are free to control the LED again

---

## Epic 2: Static Color Control

### US-03: Set Static Color
**As** Lê, **I want** to pick a color and apply it to the GPU LED, **so that** my PC has the color I like.

**Acceptance Criteria:**
- Given the app is connected to GPU, when I select a color from the color picker and click Apply, then the GPU LED changes to that color
- Given a color is applied, when I close the app, then the LED stays at the selected color

### US-04: Color Input Methods
**As** Lê, **I want** multiple ways to input a color (picker, HEX, RGB values), **so that** I can use whichever method is convenient.

**Acceptance Criteria:**
- Given the color section is open, when I use the visual color picker, then the HEX/RGB values update in sync
- Given I type a HEX code, when I press Enter, then the color picker updates to match

---

## Epic 3: LED Effects

### US-05: Apply Effect
**As** Lê, **I want** to select a lighting effect (breathing, rainbow, wave, etc.), **so that** my GPU has animated lighting.

**Acceptance Criteria:**
- Given effects list is shown, when I select an effect and click Apply, then the GPU LED starts the selected animation
- Given an effect is active, when I adjust speed slider, then the animation speed changes in real-time

### US-06: Adjust Effect Parameters
**As** Lê, **I want** to adjust speed and brightness of effects, **so that** I can customize how intense the animation is.

**Acceptance Criteria:**
- Given an effect is selected, when I change brightness slider, then LED brightness changes accordingly
- Given an effect is selected, when I change speed slider, then animation speed updates

---

## Epic 4: Preset Color Themes

### US-07: Browse Preset Themes
**As** Lê, **I want** to see a list of preset color themes (Cyberpunk, Vaporwave, etc.), **so that** I can quickly apply a popular look.

**Acceptance Criteria:**
- Given presets section is open, when I browse the list, then I see theme names with color preview swatches
- Given I click a preset, when I confirm apply, then the GPU LED uses that theme's colors with the selected effect

### US-08: Create Custom Theme
**As** Lê, **I want** to create my own color theme from any combination of colors, **so that** I can have a unique look.

**Acceptance Criteria:**
- Given I'm in custom theme creation, when I add 2-5 colors, then I can save it as a named theme
- Given I have custom themes, when I browse presets, then my custom themes appear alongside built-in ones

---

## Epic 5: Dynamic Color (Temperature-Based)

### US-09: Configure Temperature-Based Color
**As** Lê, **I want** to set color thresholds based on GPU temperature, **so that** the LED tells me at a glance if my GPU is running hot.

**Acceptance Criteria:**
- Given dynamic color mode is on, when GPU temp is below low threshold, then LED is cool color (e.g., blue)
- Given GPU temp crosses high threshold, when temperature rises, then LED transitions to warm color (e.g., red)

### US-10: Configure Load-Based Color
**As** Lê, **I want** LED color to change based on GPU load percentage, **so that** I can see how hard my GPU is working.

**Acceptance Criteria:**
- Given load-based mode is active, when GPU load changes, then LED color transitions proportionally

---

## Epic 6: LED Power Control

### US-11: Turn Off LED
**As** Lê, **I want** to turn off the GPU LED completely, **so that** it doesn't distract me when I want a dark setup.

**Acceptance Criteria:**
- Given LED is on, when I click "Turn Off LED", then the LED goes completely dark
- Given LED is off, when I click "Turn On LED", then it restores the previous color/effect

---

## Epic 7: Profile Management

### US-12: Save Profile
**As** Lê, **I want** to save my current LED settings as a profile, **so that** I can switch between different looks easily.

**Acceptance Criteria:**
- Given I have a LED configuration active, when I click "Save Profile" and enter a name, then the profile is saved
- Given I have saved profiles, when I select one from the list, then the LED applies that profile's settings

### US-13: Auto-Apply on Startup
**As** Lê, **I want** to set a default profile that applies when Windows starts, **so that** my preferred LED setting is always on.

**Acceptance Criteria:**
- Given I have profiles, when I mark one as "Apply on Startup", then next time Windows starts, that profile loads automatically

---

## Epic 8: System Integration

### US-14: System Tray
**As** Lê, **I want** the app to minimize to system tray, **so that** it doesn't take up taskbar space.

**Acceptance Criteria:**
- Given the app is open, when I click minimize/close, then it goes to system tray
- Given the app is in tray, when I right-click the tray icon, then I see quick actions (profiles, turn off LED, open app)

### US-15: Start with Windows
**As** Lê, **I want** option to start the app with Windows, **so that** my LED profile is always applied.

**Acceptance Criteria:**
- Given settings has "Start with Windows" toggle, when I enable it, then the app launches on boot (minimized to tray)

---

## Story Summary

| Epic | Stories | Priority |
|---|---|---|
| GPU Detection & Connection | US-01, US-02, US-02B, US-02C | Foundation (must have) |
| Static Color Control | US-03, US-04 | Core |
| LED Effects | US-05, US-06 | Core |
| Preset Color Themes | US-07, US-08 | Core |
| Dynamic Color | US-09, US-10 | Core |
| LED Power Control | US-11 | Core |
| Profile Management | US-12, US-13 | Core |
| System Integration | US-14, US-15 | Core |

**Total**: 17 user stories across 8 epics. All features equal priority as per user preference.

---

## INVEST Criteria Compliance

| Criteria | Status |
|---|---|
| **Independent** | ✅ Each story can be implemented independently (except US-02 depends on US-01) |
| **Negotiable** | ✅ Stories describe outcomes, not implementation details |
| **Valuable** | ✅ Each story delivers user-visible value |
| **Estimable** | ✅ Stories are scoped enough to estimate effort |
| **Small** | ✅ Each story is a single feature/behavior |
| **Testable** | ✅ All have Given/When/Then acceptance criteria |
