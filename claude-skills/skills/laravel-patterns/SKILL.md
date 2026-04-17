---
name: "laravel-patterns"
description: >
  Laravel architecture patterns: Eloquent models, controllers, service layer,
  form requests, resources, and queue jobs. Activate for Laravel development.
metadata:
  version: 1.0.0
  category: engineering
---

# Laravel Patterns Skill

## Model

```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\SoftDeletes;

class User extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = ['email', 'name'];
    protected $hidden = ['password', 'remember_token'];
    protected $casts = [
        'email_verified_at' => 'datetime',
        'is_active' => 'boolean',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->where('is_active', true);
    }
}
```

## Service Layer

```php
namespace App\Services;

use App\Models\User;
use App\Exceptions\DuplicateEmailException;
use Illuminate\Support\Facades\DB;

class UserService
{
    public function create(string $email, string $name): User
    {
        if (User::where('email', $email)->exists()) {
            throw new DuplicateEmailException($email);
        }

        return DB::transaction(function () use ($email, $name) {
            $user = User::create(['email' => $email, 'name' => $name]);
            dispatch(new SendWelcomeEmailJob($user));
            return $user;
        });
    }
}
```

## Form Request (validation)

```php
namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CreateUserRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'email' => ['required', 'email', 'max:255', 'unique:users'],
            'name'  => ['required', 'string', 'max:100'],
        ];
    }
}
```

## Controller (thin)

```php
class UserController extends Controller
{
    public function __construct(private readonly UserService $service) {}

    public function store(CreateUserRequest $request): UserResource
    {
        $user = $this->service->create(
            $request->validated('email'),
            $request->validated('name'),
        );
        return new UserResource($user);
    }
}
```

## API Resource

```php
class UserResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'         => $this->id,
            'email'      => $this->email,
            'name'       => $this->name,
            'created_at' => $this->created_at->toIso8601String(),
        ];
    }
}
```

## N+1 Prevention

```php
// WRONG
$users = User::all();
foreach ($users as $user) {
    $user->orders->count(); // N+1
}

// CORRECT
$users = User::with('orders')->get();
// Or lazy eager loading
$users->loadMissing('orders');
```
