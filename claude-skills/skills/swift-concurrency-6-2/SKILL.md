---
name: "swift-concurrency-6-2"
description: >
  Swift 6.2 Approachable Concurrency patterns: async/await, structured concurrency,
  task groups, and data race prevention. Activate for Swift concurrency work.
metadata:
  version: 1.0.0
  category: engineering
---

# Swift Concurrency 6.2 Skill

## Async/Await

```swift
// Async function
func fetchUser(id: String) async throws -> User {
    let (data, response) = try await URLSession.shared.data(from: URL(string: "/users/\(id)")!)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw APIError.notFound
    }
    return try JSONDecoder().decode(User.self, from: data)
}

// Call from sync context
Task {
    do {
        let user = try await fetchUser(id: "1")
        print(user.name)
    } catch {
        print("Error: \(error)")
    }
}
```

## Structured Concurrency (TaskGroup)

```swift
func fetchAllUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        for id in ids {
            group.addTask { try await fetchUser(id: id) }
        }
        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}
```

## Swift 6.2 Approachable Concurrency

Swift 6.2 relaxes strict concurrency checking for common patterns:

```swift
// nonisolated(unsafe) for legacy bridging (use sparingly)
nonisolated(unsafe) var legacyDelegate: SomeDelegate?

// @preconcurrency for older APIs
@preconcurrency import UIKit

// Default actor isolation (Swift 6.2 feature)
// Main actor isolation is now the default for @Observable types on UI thread
@Observable class ViewModel {
    var items: [Item] = []  // automatically @MainActor in SwiftUI context
}
```

## Task Cancellation

```swift
func longOperation() async throws -> Result {
    for i in 0..<1000 {
        try Task.checkCancellation()  // throws CancellationError if cancelled
        await processItem(i)
    }
    return result
}

// Cancel from outside
let task = Task { try await longOperation() }
task.cancel()
```

## Async Sequences

```swift
// Custom AsyncSequence
struct Countdown: AsyncSequence, AsyncIteratorProtocol {
    typealias Element = Int
    var count: Int

    mutating func next() async -> Int? {
        guard count > 0 else { return nil }
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        defer { count -= 1 }
        return count
    }

    func makeAsyncIterator() -> Countdown { self }
}

// Usage
for await n in Countdown(count: 3) {
    print(n)
}
```

## Common Patterns

```swift
// Debounce user input
actor SearchActor {
    private var currentTask: Task<Void, Never>?

    func search(query: String) {
        currentTask?.cancel()
        currentTask = Task {
            try? await Task.sleep(nanoseconds: 300_000_000)  // 300ms debounce
            guard !Task.isCancelled else { return }
            await performSearch(query)
        }
    }
}
```
