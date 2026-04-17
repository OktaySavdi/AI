---
name: "perl-patterns"
description: >
  Modern Perl 5.36+ idioms and best practices: strict/warnings, OOP with Moose/Moo,
  error handling, file I/O, and clean module patterns. Activate for Perl code.
metadata:
  version: 1.0.0
  category: engineering
---

# Perl Patterns Skill

## Modern Perl Boilerplate

```perl
#!/usr/bin/env perl
use strict;
use warnings;
use v5.36;  # enables strict, warnings, feature 'say', signatures, etc.

# Named subroutine signatures (v5.36+)
sub greet($name) {
    say "Hello, $name!";
}
```

## OOP with Moo

```perl
package User;
use Moo;
use Types::Standard qw(Str Int Bool);

has id    => (is => 'ro', isa => Str, required => 1);
has email => (is => 'ro', isa => Str, required => 1);
has name  => (is => 'rw', isa => Str, default => '');
has active => (is => 'ro', isa => Bool, default => 1);

sub display_name ($self) {
    return $self->name || $self->email;
}

1;
```

## Error Handling with die/eval

```perl
use Carp qw(croak confess);

sub divide ($a, $b) {
    croak "Division by zero" if $b == 0;
    return $a / $b;
}

my $result = eval { divide(10, 0) };
if (my $err = $@) {
    warn "Error: $err";
}
```

## Modern File I/O

```perl
use Path::Tiny;

# Read file
my $content = path("config.txt")->slurp_utf8;

# Write file
path("output.txt")->spew_utf8("Hello\n");

# Iterate lines
path("data.txt")->lines_utf8(sub { chomp; process($_) });
```

## Regular Expressions

```perl
# Named captures
if ($line =~ /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/) {
    my ($year, $month, $day) = @+{qw(year month day)};
}

# Non-destructive substitution (v5.14+)
my $cleaned = $text =~ s/^\s+|\s+$//gr;

# Compile for reuse
my $EMAIL_RE = qr/\A[\w.+-]+\@[\w-]+\.[\w.]+\z/;
```

## References and Data Structures

```perl
# Hash of arrays
my %by_dept = (
    engineering => ["Alice", "Bob"],
    marketing   => ["Carol"],
);

# Dereference
my @eng = @{$by_dept{engineering}};

# Anonymous constructors
my $user = { id => 1, name => "Alice" };
my $tags = [qw(perl linux devops)];
```

## Useful Modules

```perl
use List::Util qw(sum min max first reduce any all none);
use Scalar::Util qw(blessed looks_like_number reftype);
use POSIX qw(floor ceil);
use JSON::PP;  # stdlib JSON, no XS required
use Time::Piece;  # stdlib date parsing
```

## Anti-Patterns

- `no strict` / `no warnings` — fix the root cause instead
- Global variables `$foo` without `our` declaration
- `die` with non-object errors in modules — makes catching hard
- Regex without `/x` flag for complex patterns (use comments)
- Opening files without checking return value
