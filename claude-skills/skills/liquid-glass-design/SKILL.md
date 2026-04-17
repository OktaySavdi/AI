---
name: "liquid-glass-design"
description: >
  iOS 26 Liquid Glass design system patterns. Covers glassmorphism effects,
  SF Symbols 7, and visionOS-compatible SwiftUI components. Activate for iOS 26 UI.
metadata:
  version: 1.0.0
  category: engineering
---

# Liquid Glass Design Skill

## Core Liquid Glass Effect (iOS 26 / SwiftUI)

```swift
import SwiftUI

struct LiquidGlassCard: View {
    let title: String
    let content: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline)
                .fontWeight(.semibold)
            Text(content)
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.ultraThinMaterial)           // Liquid Glass material
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(.white.opacity(0.25), lineWidth: 1)
        )
        .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
    }
}
```

## Material Hierarchy

```swift
// iOS 26 material options (thinnest to thickest)
.background(.ultraThinMaterial)    // most transparency
.background(.thinMaterial)
.background(.regularMaterial)
.background(.thickMaterial)
.background(.ultraThickMaterial)   // least transparency
```

## Adaptive Glass Colors

```swift
// Tinted glass
.background(.thinMaterial.tint(.blue.opacity(0.15)))

// Dynamic tint based on content
struct TintedGlass: View {
    @Environment(\.colorScheme) var colorScheme

    var glassTint: Color {
        colorScheme == .dark
            ? .white.opacity(0.08)
            : .white.opacity(0.6)
    }

    var body: some View {
        Rectangle()
            .fill(.ultraThinMaterial)
            .overlay(glassTint)
    }
}
```

## SF Symbols 7 Patterns

```swift
// Variable symbols (animated fill)
Image(systemName: "wifi", variableValue: signalStrength)

// Animated symbol effects
Image(systemName: "heart.fill")
    .symbolEffect(.bounce, value: isLiked)
    .symbolEffect(.pulse, isActive: isLoading)

// Hierarchical rendering
Image(systemName: "folder.fill.badge.plus")
    .symbolRenderingMode(.hierarchical)
    .foregroundStyle(.blue)
```

## Design Principles

- Glass surfaces should reveal depth — use layered cards
- Blur radius: 20-40pt for most surfaces
- Borders: white at 15-25% opacity for light definition
- Shadows: low opacity (8-15%), soft radius (10-20pt)
- Text over glass: prefer `.primary` and `.secondary` tints, not fixed colors
- Avoid pure black/white — let material handle contrast
