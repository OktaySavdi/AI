---
name: "swift-protocol-di-testing"
description: >
  Protocol-based dependency injection for testable Swift code. Covers protocol
  witnesses, mock injection, and test patterns. Activate for Swift DI/testing.
metadata:
  version: 1.0.0
  category: engineering
---

# Swift Protocol DI Testing Skill

## Protocol-Based Dependencies

```swift
// Define protocol (interface) in the consuming module
protocol UserRepository {
    func user(for id: String) async throws -> User
    func save(_ user: User) async throws
}

// Production implementation
struct RemoteUserRepository: UserRepository {
    private let client: HTTPClient

    func user(for id: String) async throws -> User {
        try await client.get("/users/\(id)")
    }

    func save(_ user: User) async throws {
        try await client.post("/users", body: user)
    }
}

// Service uses the protocol, not the concrete type
struct UserService {
    private let repo: any UserRepository

    init(repo: some UserRepository) {
        self.repo = repo
    }
}
```

## Mock for Testing

```swift
final class MockUserRepository: UserRepository {
    var stubbedUser: User?
    var savedUsers: [User] = []
    var shouldThrow: Error?

    func user(for id: String) async throws -> User {
        if let error = shouldThrow { throw error }
        return stubbedUser ?? .init(id: id, name: "Mock User")
    }

    func save(_ user: User) async throws {
        if let error = shouldThrow { throw error }
        savedUsers.append(user)
    }
}
```

## Test Pattern

```swift
import XCTest

@MainActor
final class UserServiceTests: XCTestCase {
    var repo: MockUserRepository!
    var sut: UserService!

    override func setUp() {
        repo = MockUserRepository()
        sut = UserService(repo: repo)
    }

    func testLoadUserCallsRepository() async throws {
        repo.stubbedUser = User(id: "1", name: "Alice")
        let user = try await sut.loadUser(id: "1")
        XCTAssertEqual(user.name, "Alice")
    }

    func testLoadUserPropagatesError() async {
        repo.shouldThrow = URLError(.notConnectedToInternet)
        do {
            _ = try await sut.loadUser(id: "1")
            XCTFail("Expected error")
        } catch {
            XCTAssertTrue(error is URLError)
        }
    }
}
```

## Environment Object DI (SwiftUI)

```swift
// Pass dependencies through the environment
struct AppDependencies {
    var userRepo: any UserRepository = RemoteUserRepository()
    var analytics: any AnalyticsService = FirebaseAnalytics()
}

struct ContentView: View {
    @Environment(\.dependencies) private var deps
    // ...
}

// Test override
let testDeps = AppDependencies(
    userRepo: MockUserRepository(),
    analytics: NoOpAnalytics()
)
```
