---
name: "perl-testing"
description: >
  Perl TDD with Test2::V0: test structure, fixtures, mocking, prove, and
  Devel::Cover. Activate for Perl testing work.
metadata:
  version: 1.0.0
  category: engineering
---

# Perl Testing Skill

## Test2::V0 Basics

```perl
use Test2::V0;

# Equality
is(add(1, 2), 3, "adds two numbers");

# Regex match
like(error_message(), qr/invalid email/, "error mentions email");

# Deep structure
is(
    get_user(1),
    { id => 1, name => "Alice", active => T() },
    "returns user hash"
);

done_testing;
```

## Object Matchers

```perl
use Test2::V0;

is($user, object {
    prop blessed => "User";
    call id    => 42;
    call email => "alice@example.com";
    call name  => match qr/\w+/;
});
```

## Subtests

```perl
subtest "user creation" => sub {
    my $user = User->new(email => "test@example.com");
    ok($user, "creates user");
    is($user->email, "test@example.com", "email set correctly");
};

subtest "validation" => sub {
    like(
        dies { User->new(email => "invalid") },
        qr/invalid email/,
        "rejects invalid email"
    );
};

done_testing;
```

## Mocking with Test::MockModule

```perl
use Test::MockModule;

my $mock = Test::MockModule->new("EmailService");
$mock->mock(send => sub { return 1 });  # stub

# Or capture calls
my @sent;
$mock->mock(send => sub { push @sent, $_[1] });

UserService->register("alice@example.com");
is(scalar @sent, 1, "sent one email");
```

## Testing with Fixtures

```perl
use Test2::V0;
use DBI;

my $dbh;
BEGIN {
    $dbh = DBI->connect("dbi:SQLite::memory:", "", "", { RaiseError => 1 });
    $dbh->do("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)");
}
END { $dbh->disconnect }

subtest "find user by email" => sub {
    $dbh->do("INSERT INTO users VALUES (1, 'alice@example.com')");
    my $repo = UserRepo->new(dbh => $dbh);
    my $user = $repo->find_by_email("alice@example.com");
    is($user->{id}, 1, "found user");
};

done_testing;
```

## Running Tests

```bash
prove -l t/          # run all tests in t/
prove -lv t/users.t  # verbose single file
prove -lj4 t/        # parallel, 4 workers
```

## Coverage with Devel::Cover

```bash
cover -delete
HARNESS_PERL_SWITCHES=-MDevel::Cover prove -l t/
cover -report html
# Open cover_db/coverage.html
```

## Test File Layout

```
t/
  unit/
    01-user.t
    02-validator.t
  integration/
    10-db-repo.t
  00-compile.t   # just `use Module; pass` for all modules
```
