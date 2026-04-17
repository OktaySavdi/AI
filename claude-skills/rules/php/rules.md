# PHP Rules

Language-specific rules for PHP development. Extends `common/` rules.

## Formatting and Style

- **Formatter**: `PHP CS Fixer` with PSR-12 standard
- **Linter**: `phpstan` at level 8+, `psalm` for strict typing
- PHP version: 8.2+ for new projects (use `readonly`, fibers, typed properties)
- Line length: 120 characters

## Type Safety

```php
<?php

declare(strict_types=1);

// Typed properties (PHP 8.0+)
class User {
    public function __construct(
        public readonly int $id,
        public readonly string $name,
        public readonly string $email,
    ) {}
}

// Union types and nullable
function findUser(int|string $id): ?User {
    // ...
}

// Enums (PHP 8.1+)
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';
}
```

## Error Handling

```php
// Custom exception hierarchy
class AppException extends RuntimeException {}
class ValidationException extends AppException {
    public function __construct(
        private readonly array $errors,
        string $message = '',
    ) {
        parent::__construct($message ?: implode(', ', $errors));
    }

    public function errors(): array { return $this->errors; }
}

// Never swallow exceptions silently
try {
    $result = $this->service->process($input);
} catch (ValidationException $e) {
    $this->logger->warning('Validation failed', ['errors' => $e->errors()]);
    throw $e;  // re-throw or handle explicitly
}
```

## Security

```php
// Never interpolate user input into SQL
// WRONG:
$db->query("SELECT * FROM users WHERE id = $id");

// CORRECT — PDO prepared statements:
$stmt = $db->prepare('SELECT * FROM users WHERE id = :id');
$stmt->execute(['id' => $id]);

// Escape HTML output
echo htmlspecialchars($userInput, ENT_QUOTES, 'UTF-8');

// Hash passwords
$hash = password_hash($password, PASSWORD_ARGON2ID);
$valid = password_verify($input, $hash);
```

## Modern PHP Patterns

```php
// Readonly classes (PHP 8.2+)
readonly class Money {
    public function __construct(
        public int $amount,
        public string $currency,
    ) {}
}

// First-class callables (PHP 8.1+)
$double = fn(int $n): int => $n * 2;
$result = array_map($double, [1, 2, 3]);

// Fibers (PHP 8.1+) for cooperative multitasking
$fiber = new Fiber(function(): void {
    $value = Fiber::suspend('initial');
    echo "Resumed with: $value\n";
});
```

## Testing

```php
// PHPUnit 11+
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\DataProvider;

class UserServiceTest extends TestCase {
    #[Test]
    #[DataProvider('validEmails')]
    public function it_accepts_valid_email(string $email): void {
        $user = new User(1, 'Alice', $email);
        $this->assertSame($email, $user->email);
    }

    public static function validEmails(): array {
        return [
            ['user@example.com'],
            ['user+tag@example.org'],
        ];
    }
}
```

## Tools

```bash
php-cs-fixer fix .             # format
phpstan analyse src/           # static analysis
pest                           # run tests (modern)
phpunit                        # run tests (classic)
composer audit                 # dependency security
```
