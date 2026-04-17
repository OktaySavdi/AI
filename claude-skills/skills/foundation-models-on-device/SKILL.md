---
name: "foundation-models-on-device"
description: >
  Apple on-device LLM with FoundationModels framework. Covers model capabilities,
  structured output, and privacy-first AI patterns. Activate for on-device AI.
metadata:
  version: 1.0.0
  category: engineering
---

# Foundation Models On-Device Skill

## FoundationModels Framework (Apple Intelligence)

Available on Apple Silicon devices with iOS 18.1+ / macOS 15.1+.

```swift
import FoundationModels

// Check availability
guard LanguageModel.isAvailable else {
    // Fall back to cloud or disable feature
    return
}
```

## Text Generation

```swift
let model = LanguageModel()
let session = LanguageModelSession()

// Simple completion
let response = try await session.respond(to: "Summarize this text: \(text)")
print(response.content)

// Streaming response
for try await chunk in session.streamResponse(to: prompt) {
    print(chunk, terminator: "")
}
```

## Structured Output (Generable)

```swift
@Generable
struct ExtractedContact {
    var name: String
    var email: String?
    var phone: String?
    var company: String?
}

let contact = try await session.respond(
    to: "Extract contact info from: \(rawText)",
    generating: ExtractedContact.self
)
print(contact.name)
```

## Session Management

```swift
// System prompt for consistent behavior
let session = LanguageModelSession(
    instructions: "You are a helpful assistant that responds in JSON format."
)

// Multi-turn conversation
session.append(role: .user, content: "What is 2+2?")
let reply = try await session.respond()
session.append(role: .assistant, content: reply.content)
session.append(role: .user, content: "And 3+3?")
```

## Privacy Patterns

```swift
// Process sensitive data on-device only
func classifySensitiveDocument(_ content: String) async throws -> String {
    // FoundationModels runs entirely on-device
    // No data leaves the device
    let model = LanguageModel()
    let session = LanguageModelSession()
    return try await session.respond(to: "Classify: \(content)").content
}
```

## Capability Checking

```swift
// Check what tasks the on-device model supports
let capabilities = LanguageModel.capabilities
if capabilities.contains(.reasoning) {
    // Use for complex tasks
}
if capabilities.contains(.structuredOutput) {
    // Use @Generable structs
}
```

## Best Practices

- Use on-device for privacy-sensitive content (medical, financial, personal)
- Smaller context window than cloud — keep prompts concise (< 2000 tokens)
- Response latency is 50-200ms on Apple Silicon — suitable for interactive UI
- Use streaming for responses > 50 words to avoid perceived lag
