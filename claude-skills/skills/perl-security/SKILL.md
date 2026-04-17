---
name: "perl-security"
description: >
  Perl security patterns: taint mode, safe file I/O, input validation, SQL
  parameterization, and avoiding command injection. Activate for Perl security.
metadata:
  version: 1.0.0
  category: engineering
---

# Perl Security Skill

## Taint Mode

Enable for any script processing external data:
```perl
#!/usr/bin/perl -T
use strict;
use warnings;
```

Untaint only after explicit validation:
```perl
my ($safe_name) = ($input =~ /\A([a-zA-Z0-9_-]{1,50})\z/)
    or die "Invalid name";
# $safe_name is now untainted
```

## Input Validation

```perl
use Params::Validate qw(validate SCALAR ARRAYREF);

sub create_user {
    my %args = validate(@_, {
        email => { type => SCALAR, regex => qr/\A[\w.+-]+\@[\w-]+\.\w+\z/ },
        name  => { type => SCALAR, regex => qr/\A[\w\s]{1,100}\z/ },
    });
}
```

## SQL — Always Parameterized

```perl
use DBI;

# WRONG — SQL injection
my $user = $dbh->selectrow_hashref(
    "SELECT * FROM users WHERE email = '$email'"  # NEVER
);

# CORRECT — parameterized
my $user = $dbh->selectrow_hashref(
    "SELECT * FROM users WHERE email = ?",
    undef,
    $email
);
```

## File I/O Safety

```perl
use Path::Tiny;

# Validate path before use — prevent path traversal
sub safe_read ($base_dir, $filename) {
    my $path = path($base_dir)->child($filename)->realpath;
    die "Path traversal attempt" unless $path->stringify =~ /\A\Q$base_dir\E/;
    return $path->slurp_utf8;
}
```

## Avoiding Shell Injection

```perl
# WRONG — shell injection possible
system("ls $user_input");

# CORRECT — list form, no shell interpolation
system("ls", $user_input);

# Or use IPC::Run for complex commands
use IPC::Run qw(run);
run(["git", "log", "--oneline", $branch], \my $out);
```

## Secrets

```perl
# Read from environment — never hardcode
my $db_pass = $ENV{DB_PASSWORD} // die "DB_PASSWORD not set";

# Or use a secrets file with restricted permissions
my $secret = path("/run/secrets/api_key")->slurp_utf8;
chomp $secret;
```

## Dependency Security

```bash
# Audit installed modules
cpan-audit
# Or with Perl::Critic
perlcritic --severity 1 lib/
```
