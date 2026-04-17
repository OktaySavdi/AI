# Swift Rules

Language-specific rules for Swift development. Extends `common/` rules.

## Formatting and Style

- **Formatter**: `swift-format` (Swift.org official)
- **Linter**: `SwiftLint` with rules enabled: `force_cast`, `force_try`, `implicitly_unwrapped_optional`
- Swift version: 5.10+ / Swift 6 concurrency mode for new projects
- Line length: 120 characters

## Type Safety

```swift
// Avoid forced unwrapping — use guard let / if let
guard let url = URL(string: urlString) else {
    throw URLError(.badURL)
}

// Never force cast
// WRONG: let vc = storyboard as! MyViewController
// CORRECT:
guard let vc = storyboard as? MyViewController else { return }

// Use Result type for operations that can fail
func loadData() async -> Result<Data, Error> {
    do {
        let data = try await fetchRemote()
        return .success(data)
    } catch {
        return .failure(error)
    }
}
```

## Memory Management

```swift
// Avoid strong retain cycles — use [weak self] in closures
Task { [weak self] in
    guard let self else { return }
    await self.doWork()
}

// Use unowned only when lifetime is guaranteed
class Parent {
    var child: Child?
}
class Child {
    unowned let parent: Parent  // parent always outlives child
}
```

## Concurrency (Swift 6)

```swift
// Actors for mutable shared state
actor Cache {
    private var store: [String: Data] = [:]
    func get(_ key: String) -> Data? { store[key] }
    func set(_ key: String, value: Data) { store[key] = value }
}

// @MainActor for UI updates
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []

    func load() async {
        let data = await fetchData()
        items = data  // safe — @MainActor
    }
}
```

## Error Handling

```swift
// Define typed error enums
enum APIError: Error, LocalizedError {
    case notFound(id: String)
    case unauthorized
    case serverError(statusCode: Int)

    var errorDescription: String? {
        switch self {
        case .notFound(let id): "Resource \(id) not found"
        case .unauthorized: "Authentication required"
        case .serverError(let code): "Server error: \(code)"
        }
    }
}
```

## SwiftUI Patterns

```swift
// Prefer @Observable (iOS 17+) over ObservableObject
@Observable class AppModel {
    var count = 0
}

// Break views into small, focused components
struct UserRow: View {
    let user: User  // pass only what's needed, not the whole model
    var body: some View { ... }
}

// Use ViewModifier for reusable styling
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}
```

## Tools

```bash
swift build                    # build
swift test                     # test
swift-format --in-place .      # format
swiftlint lint                 # lint
```
