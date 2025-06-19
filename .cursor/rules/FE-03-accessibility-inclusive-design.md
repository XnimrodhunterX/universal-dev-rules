# Rule 19E: Accessibility & Inclusive Design

**Rule ID**: 19E  
**Category**: Frontend & Mobile, Quality Engineering  
**Tier**: Enterprise  
**Status**: ✅ Complete  
**Version**: 1.0  
**Last Updated**: 2024-12-19

---

## 📋 **Overview**

Establish comprehensive accessibility and inclusive design standards ensuring digital products are usable by all users, including those with disabilities, across all platforms and devices.

### **Business Value**
- **Legal Compliance**: Meet WCAG 2.1 AA, Section 508, ADA requirements
- **Market Expansion**: Reach 15% additional user base (disability community)
- **User Experience**: Improve usability for all users, not just those with disabilities
- **Brand Reputation**: Demonstrate commitment to inclusion and social responsibility

### **Key Principles**
1. **Universal Design**: Design for the widest range of users from the start
2. **Progressive Enhancement**: Ensure basic functionality works for everyone
3. **Semantic Markup**: Use proper HTML structure for assistive technologies
4. **Inclusive Content**: Create content that serves diverse audiences

---

## 🎯 **Requirements**

### **🔒 Core Requirements**

#### **WCAG 2.1 AA Compliance**
```yaml
wcag_compliance:
  level: "AA"
  version: "2.1"
  
  perceivable:
    - text_alternatives: "All non-text content has text alternatives"
    - captions_transcripts: "Audio/video content has captions/transcripts"
    - adaptable_content: "Content can be presented in different ways without losing meaning"
    - distinguishable: "Make it easier for users to see and hear content"
  
  operable:
    - keyboard_accessible: "All functionality available via keyboard"
    - seizures_safe: "Content doesn't cause seizures or physical reactions"
    - navigable: "Help users navigate and find content"
    - input_modalities: "Make it easier for users to operate functionality"
  
  understandable:
    - readable: "Make text content readable and understandable"
    - predictable: "Make content appear and operate in predictable ways"
    - input_assistance: "Help users avoid and correct mistakes"
  
  robust:
    - compatible: "Maximize compatibility with assistive technologies"
```

#### **Platform-Specific Standards**
```yaml
platform_standards:
  web:
    html_semantic: "Use semantic HTML5 elements"
    aria_labels: "Proper ARIA attributes and landmarks"
    focus_management: "Logical focus order and visible focus indicators"
    color_contrast: "4.5:1 for normal text, 3:1 for large text"
    
  mobile_ios:
    voiceover: "Full VoiceOver support"
    dynamic_type: "Support for Dynamic Type scaling"
    switch_control: "Switch Control navigation support"
    voice_control: "Voice Control compatibility"
    
  mobile_android:
    talkback: "Full TalkBack support"
    font_scaling: "Support system font scaling"
    touch_accessibility: "Minimum 44dp touch targets"
    high_contrast: "High contrast mode support"
    
  desktop:
    screen_readers: "NVDA, JAWS, VoiceOver support"
    keyboard_navigation: "Full keyboard navigation"
    zoom_support: "200% zoom without horizontal scrolling"
    os_accessibility: "Operating system accessibility features"
```

#### **Content Guidelines**
```yaml
content_accessibility:
  language:
    plain_language: "Use clear, simple language"
    reading_level: "Target 8th grade reading level"
    avoid_jargon: "Minimize technical jargon"
    
  structure:
    headings: "Proper heading hierarchy (h1-h6)"
    lists: "Use proper list markup"
    tables: "Data tables with headers and captions"
    forms: "Clear labels and error messages"
    
  media:
    images: "Descriptive alt text for images"
    videos: "Captions and audio descriptions"
    audio: "Transcripts for audio content"
    animations: "Respect prefers-reduced-motion"
```

---

## 🛠 **Implementation**

### **1. Accessibility Testing Framework**

#### **Automated Testing Suite**
```javascript
// tests/accessibility/automated-a11y-tests.js
/**
 * Automated Accessibility Testing Suite
 * Uses axe-core, Pa11y, and custom validators
 */

const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const pa11y = require('pa11y');

class AccessibilityTestSuite {
    constructor() {
        this.axeConfig = {
            rules: {
                'color-contrast': { enabled: true },
                'keyboard-navigation': { enabled: true },
                'aria-labels': { enabled: true },
                'semantic-markup': { enabled: true }
            },
            tags: ['wcag2a', 'wcag2aa', 'wcag21aa']
        };
    }

    async runFullAccessibilityAudit(page, url) {
        const results = {
            url,
            timestamp: new Date().toISOString(),
            axe: await this.runAxeAudit(page),
            pa11y: await this.runPa11yAudit(url),
            custom: await this.runCustomTests(page),
            score: 0,
            violations: [],
            recommendations: []
        };

        results.score = this.calculateAccessibilityScore(results);
        return results;
    }

    async runAxeAudit(page) {
        try {
            const axeBuilder = new AxeBuilder({ page });
            const results = await axeBuilder
                .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
                .analyze();

            return {
                violations: results.violations,
                passes: results.passes,
                incomplete: results.incomplete,
                inapplicable: results.inapplicable
            };
        } catch (error) {
            console.error('Axe audit failed:', error);
            return { error: error.message };
        }
    }

    async runPa11yAudit(url) {
        try {
            const results = await pa11y(url, {
                standard: 'WCAG2AA',
                includeNotices: false,
                includeWarnings: true,
                chromeLaunchConfig: {
                    headless: true
                }
            });

            return {
                issues: results.issues,
                documentTitle: results.documentTitle,
                pageUrl: results.pageUrl
            };
        } catch (error) {
            console.error('Pa11y audit failed:', error);
            return { error: error.message };
        }
    }

    async runCustomTests(page) {
        const customTests = [
            this.testKeyboardNavigation(page),
            this.testFocusManagement(page),
            this.testColorContrast(page),
            this.testResponsiveDesign(page),
            this.testMotionPreferences(page)
        ];

        const results = await Promise.all(customTests);
        return {
            keyboardNavigation: results[0],
            focusManagement: results[1],
            colorContrast: results[2],
            responsiveDesign: results[3],
            motionPreferences: results[4]
        };
    }

    async testKeyboardNavigation(page) {
        const results = {
            passed: true,
            issues: [],
            coverage: 0
        };

        try {
            // Test tab order
            const focusableElements = await page.$$('[tabindex], input, button, select, textarea, a[href]');
            let tabIndex = 0;

            for (const element of focusableElements) {
                await page.keyboard.press('Tab');
                const focusedElement = await page.locator(':focus');
                
                if (!await focusedElement.isVisible()) {
                    results.issues.push({
                        type: 'invisible_focus',
                        element: await element.getAttribute('id') || await element.textContent(),
                        message: 'Focused element is not visible'
                    });
                    results.passed = false;
                }
                tabIndex++;
            }

            results.coverage = (focusableElements.length - results.issues.length) / focusableElements.length * 100;

        } catch (error) {
            results.passed = false;
            results.issues.push({ type: 'error', message: error.message });
        }

        return results;
    }

    async testFocusManagement(page) {
        const results = {
            passed: true,
            issues: []
        };

        try {
            // Test focus indicators
            const focusableElements = await page.$$('input, button, select, textarea, a[href]');
            
            for (const element of focusableElements) {
                await element.focus();
                
                // Check if focus indicator is visible
                const focusStyle = await element.evaluate((el) => {
                    const style = window.getComputedStyle(el, ':focus');
                    return {
                        outline: style.outline,
                        outlineWidth: style.outlineWidth,
                        boxShadow: style.boxShadow
                    };
                });

                if (focusStyle.outline === 'none' && focusStyle.outlineWidth === '0px' && !focusStyle.boxShadow) {
                    results.issues.push({
                        type: 'missing_focus_indicator',
                        element: await element.getAttribute('id') || await element.textContent(),
                        message: 'Element lacks visible focus indicator'
                    });
                    results.passed = false;
                }
            }

        } catch (error) {
            results.passed = false;
            results.issues.push({ type: 'error', message: error.message });
        }

        return results;
    }

    async testColorContrast(page) {
        const results = {
            passed: true,
            issues: [],
            averageContrast: 0
        };

        try {
            // Inject color contrast testing
            await page.addScriptTag({
                url: 'https://unpkg.com/color-contrast-checker@2.1.0/dist/color-contrast-checker.min.js'
            });

            const contrastResults = await page.evaluate(() => {
                const checker = new ColorContrastChecker();
                const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div, label');
                const results = [];

                textElements.forEach(element => {
                    const style = window.getComputedStyle(element);
                    const color = style.color;
                    const backgroundColor = style.backgroundColor;
                    const fontSize = parseFloat(style.fontSize);

                    if (color && backgroundColor && color !== backgroundColor) {
                        const isLargeText = fontSize >= 18 || (fontSize >= 14 && style.fontWeight >= 700);
                        const requiredRatio = isLargeText ? 3 : 4.5;
                        
                        try {
                            const isValid = checker.isLevelAA(color, backgroundColor, isLargeText);
                            const ratio = checker.getContrastRatio(color, backgroundColor);
                            
                            results.push({
                                element: element.tagName + (element.id ? '#' + element.id : ''),
                                color,
                                backgroundColor,
                                ratio,
                                required: requiredRatio,
                                passed: isValid,
                                isLargeText
                            });
                        } catch (e) {
                            // Skip elements with invalid colors
                        }
                    }
                });

                return results;
            });

            const failedContrasts = contrastResults.filter(result => !result.passed);
            results.issues = failedContrasts.map(result => ({
                type: 'insufficient_contrast',
                element: result.element,
                message: `Contrast ratio ${result.ratio.toFixed(2)} is below required ${result.required}`,
                ratio: result.ratio,
                required: result.required
            }));

            results.passed = failedContrasts.length === 0;
            results.averageContrast = contrastResults.reduce((sum, r) => sum + r.ratio, 0) / contrastResults.length;

        } catch (error) {
            results.passed = false;
            results.issues.push({ type: 'error', message: error.message });
        }

        return results;
    }

    async testResponsiveDesign(page) {
        const results = {
            passed: true,
            issues: [],
            viewports: []
        };

        const viewports = [
            { width: 320, height: 568, name: 'mobile-small' },
            { width: 375, height: 667, name: 'mobile-medium' },
            { width: 768, height: 1024, name: 'tablet' },
            { width: 1024, height: 768, name: 'desktop-small' },
            { width: 1920, height: 1080, name: 'desktop-large' }
        ];

        try {
            for (const viewport of viewports) {
                await page.setViewportSize({ width: viewport.width, height: viewport.height });
                
                // Check for horizontal scrolling
                const hasHorizontalScroll = await page.evaluate(() => {
                    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
                });

                // Check minimum touch target size (mobile viewports)
                let touchTargetIssues = [];
                if (viewport.width <= 768) {
                    touchTargetIssues = await page.evaluate(() => {
                        const interactiveElements = document.querySelectorAll('button, input, select, textarea, a[href]');
                        const issues = [];

                        interactiveElements.forEach(element => {
                            const rect = element.getBoundingClientRect();
                            const minSize = 44; // 44px minimum touch target

                            if (rect.width < minSize || rect.height < minSize) {
                                issues.push({
                                    element: element.tagName + (element.id ? '#' + element.id : ''),
                                    width: rect.width,
                                    height: rect.height,
                                    required: minSize
                                });
                            }
                        });

                        return issues;
                    });
                }

                const viewportResult = {
                    name: viewport.name,
                    width: viewport.width,
                    height: viewport.height,
                    hasHorizontalScroll,
                    touchTargetIssues
                };

                if (hasHorizontalScroll) {
                    results.issues.push({
                        type: 'horizontal_scroll',
                        viewport: viewport.name,
                        message: 'Horizontal scrolling detected'
                    });
                    results.passed = false;
                }

                if (touchTargetIssues.length > 0) {
                    results.issues.push({
                        type: 'small_touch_targets',
                        viewport: viewport.name,
                        count: touchTargetIssues.length,
                        message: `${touchTargetIssues.length} touch targets below 44px minimum`
                    });
                    results.passed = false;
                }

                results.viewports.push(viewportResult);
            }

        } catch (error) {
            results.passed = false;
            results.issues.push({ type: 'error', message: error.message });
        }

        return results;
    }

    async testMotionPreferences(page) {
        const results = {
            passed: true,
            issues: []
        };

        try {
            // Test prefers-reduced-motion support
            await page.emulateMedia({ reducedMotion: 'reduce' });

            const motionElements = await page.evaluate(() => {
                const elements = document.querySelectorAll('*');
                const motionElements = [];

                elements.forEach(element => {
                    const style = window.getComputedStyle(element);
                    if (style.animation !== 'none' || style.transition !== 'all 0s ease 0s') {
                        motionElements.push({
                            element: element.tagName + (element.id ? '#' + element.id : ''),
                            animation: style.animation,
                            transition: style.transition
                        });
                    }
                });

                return motionElements;
            });

            if (motionElements.length > 0) {
                results.issues.push({
                    type: 'motion_not_reduced',
                    count: motionElements.length,
                    message: 'Elements still have motion when reduced motion is preferred'
                });
                results.passed = false;
            }

        } catch (error) {
            results.passed = false;
            results.issues.push({ type: 'error', message: error.message });
        }

        return results;
    }

    calculateAccessibilityScore(results) {
        let score = 100;
        
        // Deduct points for violations
        if (results.axe && results.axe.violations) {
            results.axe.violations.forEach(violation => {
                const deduction = violation.impact === 'critical' ? 20 : 
                                 violation.impact === 'serious' ? 10 : 5;
                score -= deduction;
            });
        }

        // Deduct points for custom test failures
        if (results.custom) {
            Object.values(results.custom).forEach(test => {
                if (!test.passed) {
                    score -= test.issues.length * 5;
                }
            });
        }

        return Math.max(0, score);
    }
}

// Playwright test integration
test.describe('Accessibility Tests', () => {
    let accessibilityTest;

    test.beforeEach(async () => {
        accessibilityTest = new AccessibilityTestSuite();
    });

    test('Home page accessibility', async ({ page }) => {
        await page.goto('/');
        const results = await accessibilityTest.runFullAccessibilityAudit(page, '/');
        
        // Log detailed results
        console.log('Accessibility Score:', results.score);
        if (results.violations.length > 0) {
            console.log('Violations:', results.violations);
        }

        // Expect minimum score
        expect(results.score).toBeGreaterThanOrEqual(90);
        expect(results.axe.violations.filter(v => v.impact === 'critical')).toHaveLength(0);
    });

    test('Form accessibility', async ({ page }) => {
        await page.goto('/contact');
        const results = await accessibilityTest.runFullAccessibilityAudit(page, '/contact');
        
        expect(results.score).toBeGreaterThanOrEqual(95);
        expect(results.custom.keyboardNavigation.passed).toBe(true);
        expect(results.custom.focusManagement.passed).toBe(true);
    });
});

module.exports = AccessibilityTestSuite;
```

#### **Manual Testing Guidelines**
```markdown
# Manual Accessibility Testing Guide

## 🧪 **Screen Reader Testing**

### **NVDA (Windows)**
1. **Setup**: Download and install NVDA (free)
2. **Navigation**: Use arrow keys to navigate content
3. **Headlines**: H key to jump between headings
4. **Links**: K key to cycle through links
5. **Forms**: F key to navigate form fields
6. **Landmarks**: D key for landmark navigation

**Test Checklist**:
- [ ] All content is announced clearly
- [ ] Heading structure is logical
- [ ] Form labels are read correctly
- [ ] Error messages are announced
- [ ] Dynamic content changes are announced

### **VoiceOver (macOS)**
1. **Activation**: Cmd + F5 to enable
2. **Navigation**: VO + Arrow keys
3. **Rotor**: VO + U for element list
4. **Headings**: VO + Cmd + H
5. **Links**: VO + Cmd + L

### **TalkBack (Android)**
1. **Activation**: Settings > Accessibility > TalkBack
2. **Navigation**: Swipe right/left
3. **Explore by touch**: Touch and drag
4. **Global gestures**: Two-finger swipe up

## ⌨️ **Keyboard Navigation Testing**

### **Test Sequence**
1. **Tab Order**: Press Tab to navigate through all interactive elements
2. **Focus Indicators**: Verify all focused elements have visible indicators
3. **Skip Links**: Test skip navigation links
4. **Modal Dialogs**: Ensure focus is trapped within modals
5. **Dropdown Menus**: Test with arrow keys and Enter
6. **Custom Controls**: Verify ARIA controls work with keyboard

### **Key Combinations to Test**
- **Tab/Shift+Tab**: Forward/backward navigation
- **Enter/Space**: Activate buttons and links
- **Arrow Keys**: Navigate within components
- **Esc**: Close modals and dropdowns
- **Home/End**: Navigate to beginning/end of content

## 🎨 **Visual Testing**

### **Color Contrast**
1. **Tools**: Use WebAIM Contrast Checker or browser extensions
2. **Ratios**: 4.5:1 for normal text, 3:1 for large text
3. **Test States**: Default, hover, focus, visited
4. **All Combinations**: Text/background, border/background

### **Zoom Testing**
1. **200% Zoom**: Ensure no horizontal scrolling
2. **400% Zoom**: Content should reflow appropriately
3. **Text Scaling**: Test browser text size increases
4. **Mobile Zoom**: Test pinch-to-zoom functionality

### **Color Independence**
1. **Grayscale**: View page in grayscale
2. **Color Blindness**: Use color blindness simulators
3. **Information**: Ensure no information is conveyed by color alone
4. **Status**: Error/success states should not rely only on color

## 📱 **Mobile Accessibility**

### **Touch Targets**
- **Size**: Minimum 44x44 pixels (iOS), 48x48dp (Android)
- **Spacing**: Adequate spacing between targets
- **Gestures**: Test custom gestures work with assistive tech

### **Platform Features**
- **iOS**: VoiceOver, Switch Control, Voice Control
- **Android**: TalkBack, Select to Speak, Voice Access
- **Orientation**: Test both portrait and landscape
- **Dynamic Type**: Test with increased text sizes
```

### **2. Component Accessibility Library**

#### **Accessible React Components**
```jsx
// components/accessible/AccessibleButton.jsx
import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';

const AccessibleButton = forwardRef(({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  ariaLabel,
  ariaDescribedBy,
  onClick,
  type = 'button',
  ...props
}, ref) => {
  const baseClasses = 'btn';
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger'
  };
  const sizeClasses = {
    small: 'btn-sm',
    medium: 'btn-md',
    large: 'btn-lg'
  };

  const className = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    disabled && 'btn-disabled',
    loading && 'btn-loading'
  ].filter(Boolean).join(' ');

  return (
    <button
      ref={ref}
      type={type}
      className={className}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      aria-busy={loading}
      onClick={onClick}
      {...props}
    >
      {loading && (
        <span 
          className="btn-spinner" 
          aria-hidden="true"
          role="status"
        >
          <span className="sr-only">Loading...</span>
        </span>
      )}
      <span className={loading ? 'btn-content-loading' : 'btn-content'}>
        {children}
      </span>
    </button>
  );
});

AccessibleButton.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  ariaLabel: PropTypes.string,
  ariaDescribedBy: PropTypes.string,
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['button', 'submit', 'reset'])
};

AccessibleButton.displayName = 'AccessibleButton';

export default AccessibleButton;
```

```jsx
// components/accessible/AccessibleModal.jsx
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import PropTypes from 'prop-types';

const AccessibleModal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  closeOnOverlayClick = true,
  closeOnEscapeKey = true,
  focusFirstElement = true,
  returnFocusOnClose = true
}) => {
  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);
  const [modalRoot, setModalRoot] = useState(null);

  useEffect(() => {
    // Create modal root if it doesn't exist
    let root = document.getElementById('modal-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'modal-root';
      document.body.appendChild(root);
    }
    setModalRoot(root);

    return () => {
      // Cleanup if needed
      if (root && root.children.length === 0) {
        document.body.removeChild(root);
      }
    };
  }, []);

  useEffect(() => {
    if (isOpen) {
      // Store previous focus
      previousFocusRef.current = document.activeElement;
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
      
      // Focus management
      if (focusFirstElement && modalRef.current) {
        const firstFocusable = modalRef.current.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (firstFocusable) {
          firstFocusable.focus();
        }
      }

      // Add aria-hidden to main content
      const main = document.querySelector('main');
      if (main) {
        main.setAttribute('aria-hidden', 'true');
      }
    } else {
      // Restore body scroll
      document.body.style.overflow = '';
      
      // Return focus
      if (returnFocusOnClose && previousFocusRef.current) {
        previousFocusRef.current.focus();
      }

      // Remove aria-hidden from main content
      const main = document.querySelector('main');
      if (main) {
        main.removeAttribute('aria-hidden');
      }
    }

    return () => {
      document.body.style.overflow = '';
      const main = document.querySelector('main');
      if (main) {
        main.removeAttribute('aria-hidden');
      }
    };
  }, [isOpen, focusFirstElement, returnFocusOnClose]);

  useEffect(() => {
    const handleEscapeKey = (event) => {
      if (closeOnEscapeKey && event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscapeKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isOpen, closeOnEscapeKey, onClose]);

  const handleOverlayClick = (event) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  const handleFocusTrap = (event) => {
    if (!modalRef.current) return;

    const focusableElements = modalRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (event.key === 'Tab') {
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
  };

  if (!isOpen || !modalRoot) {
    return null;
  }

  const sizeClasses = {
    small: 'modal-sm',
    medium: 'modal-md',
    large: 'modal-lg',
    xlarge: 'modal-xl'
  };

  return createPortal(
    <div
      className="modal-overlay"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onKeyDown={handleFocusTrap}
    >
      <div
        ref={modalRef}
        className={`modal-content ${sizeClasses[size]}`}
        role="document"
      >
        <div className="modal-header">
          <h2 id="modal-title" className="modal-title">
            {title}
          </h2>
          <button
            type="button"
            className="modal-close"
            aria-label="Close modal"
            onClick={onClose}
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>,
    modalRoot
  );
};

AccessibleModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  size: PropTypes.oneOf(['small', 'medium', 'large', 'xlarge']),
  closeOnOverlayClick: PropTypes.bool,
  closeOnEscapeKey: PropTypes.bool,
  focusFirstElement: PropTypes.bool,
  returnFocusOnClose: PropTypes.bool
};

export default AccessibleModal;
```

#### **CSS Accessibility Utilities**
```css
/* styles/accessibility.css */

/* Screen reader only content */
.sr-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

/* Skip navigation links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--color-primary);
  color: white;
  padding: 8px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 9999;
  font-weight: bold;
}

.skip-link:focus {
  top: 6px;
}

/* Focus indicators */
*:focus {
  outline: 2px solid var(--color-focus, #0066cc);
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  * {
    background-color: ButtonFace;
    color: ButtonText;
  }
  
  a {
    color: LinkText;
  }
  
  button {
    border: 1px solid ButtonText;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Color contrast utilities */
.text-high-contrast {
  color: var(--color-text-high-contrast, #000000);
  background-color: var(--color-bg-high-contrast, #ffffff);
}

/* Touch target sizing */
.touch-target {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Responsive text scaling */
@media (min-width: 320px) {
  html {
    font-size: calc(16px + 6 * ((100vw - 320px) / 680));
  }
}

@media (min-width: 1000px) {
  html {
    font-size: 22px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #ffffff;
    --color-background: #121212;
    --color-focus: #66b3ff;
  }
}

/* Print styles for accessibility */
@media print {
  .no-print,
  .skip-link,
  nav,
  .modal-overlay {
    display: none !important;
  }
  
  a[href^="http"]:after {
    content: " (" attr(href) ")";
  }
  
  * {
    background: white !important;
    color: black !important;
    <provider>-shadow: none !important;
    text-shadow: none !important;
  }
}
```

---

## 📊 **Templates & Tools**

### **Accessibility Audit Template**
```markdown
# Accessibility Audit Report

## 📋 **Audit Information**
- **Page/Component**: {{PAGE_NAME}}
- **Auditor**: {{AUDITOR_NAME}}
- **Date**: {{AUDIT_DATE}}
- **WCAG Level**: {{WCAG_LEVEL}}
- **Tools Used**: {{TOOLS_LIST}}

## 🎯 **Overall Score**
- **Accessibility Score**: {{SCORE}}/100
- **WCAG Compliance**: {{COMPLIANCE_LEVEL}}
- **Critical Issues**: {{CRITICAL_COUNT}}
- **Total Issues**: {{TOTAL_ISSUES}}

## 🔍 **Detailed Findings**

### **Critical Issues (Must Fix)**
| Issue | Location | WCAG Criterion | Impact | Recommendation |
|-------|----------|----------------|--------|----------------|
| {{ISSUE}} | {{LOCATION}} | {{WCAG_REF}} | {{IMPACT}} | {{RECOMMENDATION}} |

### **High Priority Issues**
| Issue | Location | WCAG Criterion | Impact | Recommendation |
|-------|----------|----------------|--------|----------------|
| {{ISSUE}} | {{LOCATION}} | {{WCAG_REF}} | {{IMPACT}} | {{RECOMMENDATION}} |

### **Medium Priority Issues**
| Issue | Location | WCAG Criterion | Impact | Recommendation |
|-------|----------|----------------|--------|----------------|
| {{ISSUE}} | {{LOCATION}} | {{WCAG_REF}} | {{IMPACT}} | {{RECOMMENDATION}} |

## ✅ **What's Working Well**
- {{POSITIVE_FINDING_1}}
- {{POSITIVE_FINDING_2}}
- {{POSITIVE_FINDING_3}}

## 🛠 **Recommended Actions**

### **Immediate (This Sprint)**
1. {{IMMEDIATE_ACTION_1}}
2. {{IMMEDIATE_ACTION_2}}

### **Short Term (Next Sprint)**
1. {{SHORT_TERM_ACTION_1}}
2. {{SHORT_TERM_ACTION_2}}

### **Long Term (Next Quarter)**
1. {{LONG_TERM_ACTION_1}}
2. {{LONG_TERM_ACTION_2}}

## 📈 **Testing Coverage**

### **Automated Testing**
- [x] Axe-core validation
- [x] Color contrast checking
- [x] Keyboard navigation
- [x] Focus management
- [ ] Screen reader compatibility

### **Manual Testing**
- [x] NVDA screen reader
- [x] Keyboard-only navigation
- [x] Mobile accessibility
- [ ] VoiceOver testing
- [ ] High contrast mode

## 📞 **Next Steps**
1. Address critical issues within 1 week
2. Schedule follow-up audit in 2 weeks
3. Implement automated testing in CI/CD
4. Train team on accessibility best practices
```

### **Component Accessibility Checklist**
```markdown
# Component Accessibility Checklist

## 🏗️ **Semantic Structure**
- [ ] Uses semantic HTML elements (header, nav, main, section, article, aside, footer)
- [ ] Proper heading hierarchy (h1-h6) without skipping levels
- [ ] Lists use proper markup (ul, ol, li)
- [ ] Tables have proper headers and captions
- [ ] Forms have associated labels

## ⌨️ **Keyboard Navigation**
- [ ] All interactive elements are keyboard accessible
- [ ] Logical tab order throughout the component
- [ ] Custom components implement proper keyboard handling
- [ ] Focus indicators are visible and have sufficient contrast
- [ ] Focus doesn't get trapped unexpectedly

## 🎨 **Visual Design**
- [ ] Color contrast meets WCAG AA standards (4.5:1 normal, 3:1 large text)
- [ ] Information is not conveyed by color alone
- [ ] Text can be resized up to 200% without loss of functionality
- [ ] Touch targets are at least 44x44 pixels
- [ ] Content is readable in both light and dark modes

## 🔊 **Screen Reader Support**
- [ ] All images have appropriate alt text
- [ ] Decorative images have empty alt attributes (alt="")
- [ ] Form controls have descriptive labels
- [ ] Error messages are properly associated with form fields
- [ ] Dynamic content changes are announced

## 📱 **Mobile Accessibility**
- [ ] Component works with mobile screen readers (VoiceOver, TalkBack)
- [ ] Touch targets are appropriately sized
- [ ] Component supports system font scaling
- [ ] Orientation changes don't break functionality
- [ ] Custom gestures are accessible

## 🎭 **ARIA Implementation**
- [ ] ARIA labels provide clear descriptions
- [ ] ARIA roles are used appropriately
- [ ] ARIA states (expanded, checked, selected) are managed correctly
- [ ] Live regions announce dynamic changes
- [ ] Landmark roles help with navigation

## 🧪 **Testing Completed**
- [ ] Automated testing (axe-core, Pa11y)
- [ ] Keyboard navigation testing
- [ ] Screen reader testing (at least one tool)
- [ ] Mobile accessibility testing
- [ ] Color contrast validation
- [ ] Zoom testing (up to 200%)

## 📝 **Documentation**
- [ ] Accessibility features documented
- [ ] Usage examples include accessibility considerations
- [ ] Known limitations documented
- [ ] Testing instructions provided
```

---

## 🔧 **Validation & Testing**

### **Accessibility Test Automation**
```yaml
# .github/workflows/accessibility.yml
name: Accessibility Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  accessibility-audit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build application
      run: npm run build
    
    - name: Start application
      run: npm start &
      
    - name: Wait for application
      run: npx wait-on http://localhost:3000
    
    - name: Run Lighthouse CI
      uses: treosh/lighthouse-ci-action@v9
      with:
        configPath: './lighthouse-ci.json'
        uploadArtifacts: true
        temporaryPublicStorage: true
    
    - name: Run Pa11y
      run: |
        npm install -g pa11y
        pa11y --standard WCAG2AA --reporter json \
          http://localhost:3000 > pa11y-results.json
    
    - name: Run axe-core tests
      run: npm run test:accessibility
    
    - name: Upload accessibility reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: accessibility-reports
        path: |
          lhci_reports/
          pa11y-results.json
          accessibility-test-results.json
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          try {
            const results = JSON.parse(fs.readFileSync('accessibility-test-results.json'));
            const score = results.score;
            const violations = results.violations.length;
            
            const comment = `## ♿ Accessibility Test Results
            
            **Score**: ${score}/100
            **Violations**: ${violations}
            
            ${violations > 0 ? '⚠️ Please address accessibility issues before merging.' : '✅ All accessibility tests passed!'}
            
            [View detailed report](${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID})`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          } catch (error) {
            console.log('Could not post comment:', error);
          }
```

---

## 📈 **Metrics & Monitoring**

### **Accessibility KPIs**
```yaml
accessibility_kpis:
  compliance_metrics:
    - name: "wcag_aa_compliance"
      target: "100%"
      measurement: "percentage of pages meeting WCAG 2.1 AA"
    
    - name: "accessibility_score"
      target: "> 95"
      measurement: "average accessibility score across all pages"
    
    - name: "critical_violations"
      target: "0"
      measurement: "number of critical accessibility violations"
  
  user_experience:
    - name: "keyboard_navigation_coverage"
      target: "100%"
      measurement: "percentage of functionality accessible via keyboard"
    
    - name: "screen_reader_compatibility"
      target: "100%"
      measurement: "percentage of content readable by screen readers"
    
    - name: "mobile_accessibility_score"
      target: "> 90"
      measurement: "mobile-specific accessibility score"
  
  testing_coverage:
    - name: "automated_test_coverage"
      target: "100%"
      measurement: "percentage of components with automated a11y tests"
    
    - name: "manual_test_frequency"
      target: "monthly"
      measurement: "frequency of manual accessibility testing"
```

---

## 📚 **References & Standards**

### **Compliance Mappings**
- **WCAG 2.1**: Web Content Accessibility Guidelines Level AA
- **Section 508**: US Federal accessibility requirements
- **ADA**: Americans with Disabilities Act compliance
- **EN 301 549**: European accessibility standard
- **AODA**: Accessibility for Ontarians with Disabilities Act

### **Integration Points**
- **Rule 14A**: Frontend Development (UI implementation)
- **Rule 07A**: Testing Strategy (accessibility testing)
- **Rule 18A**: Quality Assurance (accessibility QA)
- **Rule 19C**: Data Governance (accessible data handling)

---

**Implementation Status**: ✅ Complete  
**Validation Required**: Automated testing integration, screen reader testing, compliance validation  
**Next Steps**: Integrate with existing frontend components and testing framework 