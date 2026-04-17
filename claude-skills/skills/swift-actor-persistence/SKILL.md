---
name: "swift-actor-persistence"
description: >
  Thread-safe Swift data persistence with actors. Covers actor isolation,
  @MainActor, and safe concurrent storage patterns. Activate for Swift persistence.
metadata:
  version: 1.0.0
  category: engineering
---

# Swift Actor Persistence Skill

## Actor for Thread-Safe Storage

```swift
actor UserStore {
    private var users: [String: User] = [:]

    func user(for id: String) -> User? {
        users[id]
    }

    func save(_ user: User) {
        users[user.id] = user
    }

    func delete(id: String) {
        users.removeValue(forKey: id)
    }

    func allUsers() -> [User] {
        Array(users.values)
    }
}

// Usage — always async
let store = UserStore()
await store.save(user)
let found = await store.user(for: "abc")
```

## File Persistence with Actor

```swift
import Foundation

actor PersistentStore<T: Codable> {
    private let fileURL: URL
    private var cache: [String: T] = [:]

    init(filename: String) {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        fileURL = docs.appendingPathComponent(filename)
        if let data = try? Data(contentsOf: fileURL),
           let loaded = try? JSONDecoder().decode([String: T].self, from: data) {
            cache = loaded
        }
    }

    func get(_ key: String) -> T? { cache[key] }

    func set(_ key: String, value: T) throws {
        cache[key] = value
        let data = try JSONEncoder().encode(cache)
        try data.write(to: fileURL, options: .atomic)
    }
}
```

## @MainActor for UI State

```swift
@MainActor
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false

    private let store: UserStore

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        users = await store.allUsers()
    }
}
```

## Sendable Requirements

```swift
// Value types are Sendable by default
struct User: Sendable {
    let id: String
    let name: String
}

// Classes need explicit Sendable conformance with proper isolation
final class Config: @unchecked Sendable {
    private let lock = NSLock()
    private var _value: String = ""
    var value: String {
        get { lock.withLock { _value } }
        set { lock.withLock { _value = newValue } }
    }
}
```
