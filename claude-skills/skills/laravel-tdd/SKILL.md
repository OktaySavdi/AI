---
name: "laravel-tdd"
description: >
  Laravel TDD workflow with PHPUnit and Pest: feature tests, unit tests,
  factories, and RefreshDatabase. Activate for Laravel TDD work.
metadata:
  version: 1.0.0
  category: engineering
---

# Laravel TDD Skill

## Test Types

```
tests/
  Unit/         → pure PHP unit tests, no framework
  Feature/      → HTTP, database, queue integration
```

## Feature Test (Pest)

```php
use App\Models\User;

it('creates a user', function () {
    $response = $this->postJson('/api/users', [
        'email' => 'new@example.com',
        'name'  => 'New User',
    ]);

    $response->assertStatus(201)
        ->assertJsonPath('data.email', 'new@example.com');

    $this->assertDatabaseHas('users', ['email' => 'new@example.com']);
});

it('rejects duplicate email', function () {
    User::factory()->create(['email' => 'dup@example.com']);

    $this->postJson('/api/users', ['email' => 'dup@example.com', 'name' => 'Copy'])
        ->assertStatus(422)
        ->assertJsonValidationErrors(['email']);
});
```

## Feature Test (PHPUnit)

```php
class CreateUserTest extends TestCase
{
    use RefreshDatabase;

    public function test_creates_user(): void
    {
        $response = $this->postJson('/api/users', [
            'email' => 'new@example.com',
            'name'  => 'New User',
        ]);

        $response->assertCreated();
        $this->assertDatabaseCount('users', 1);
    }
}
```

## Factories

```php
class UserFactory extends Factory
{
    public function definition(): array
    {
        return [
            'email'    => $this->faker->unique()->safeEmail(),
            'name'     => $this->faker->name(),
            'is_active' => true,
        ];
    }

    public function inactive(): static
    {
        return $this->state(['is_active' => false]);
    }
}

// Usage
User::factory()->create();
User::factory()->inactive()->create();
User::factory()->count(10)->create();
```

## Unit Test

```php
it('formats display name from name field', function () {
    $user = new User(['name' => 'Alice Smith', 'email' => 'alice@example.com']);
    expect($user->displayName())->toBe('Alice Smith');
});

it('falls back to email when name is empty', function () {
    $user = new User(['name' => '', 'email' => 'alice@example.com']);
    expect($user->displayName())->toBe('alice@example.com');
});
```

## Commands

```bash
php artisan test                          # all tests
php artisan test --filter CreateUserTest  # specific class
php artisan test --parallel               # parallel execution
php artisan test --coverage               # coverage report
./vendor/bin/pest                         # Pest runner
```
