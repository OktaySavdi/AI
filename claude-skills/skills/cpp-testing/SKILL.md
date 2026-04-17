---
name: "cpp-testing"
description: >
  C++ testing with GoogleTest and CMake/CTest: test structure, mocking with gMock,
  death tests, fixtures, and benchmark patterns. Activate for C++ testing work.
metadata:
  version: 1.0.0
  category: engineering
---

# C++ Testing Skill

## GoogleTest Basics

```cpp
#include <gtest/gtest.h>

TEST(ValidatorTest, RejectsEmptyEmail) {
    EXPECT_FALSE(validateEmail(""));
}

TEST(ValidatorTest, AcceptsValidEmail) {
    EXPECT_TRUE(validateEmail("user@example.com"));
}
```

## Test Fixtures

```cpp
class UserServiceTest : public ::testing::Test {
protected:
    void SetUp() override {
        repo_ = std::make_unique<MockUserRepo>();
        service_ = std::make_unique<UserService>(*repo_);
    }

    std::unique_ptr<MockUserRepo> repo_;
    std::unique_ptr<UserService> service_;
};

TEST_F(UserServiceTest, ReturnsNulloptForUnknownUser) {
    EXPECT_CALL(*repo_, findById("unknown")).WillOnce(Return(std::nullopt));
    auto result = service_->getUser("unknown");
    EXPECT_FALSE(result.has_value());
}
```

## gMock

```cpp
#include <gmock/gmock.h>

class MockUserRepo : public UserRepository {
public:
    MOCK_METHOD(std::optional<User>, findById, (const std::string& id), (const, override));
    MOCK_METHOD(void, save, (const User& user), (override));
};

// Expectations
EXPECT_CALL(*mock, save(testing::_)).Times(1);
EXPECT_CALL(*mock, findById("abc"))
    .WillOnce(testing::Return(User{"abc", "Alice"}));
```

## Death Tests (exception/abort)

```cpp
TEST(ParserTest, ThrowsOnNullInput) {
    EXPECT_THROW(parse(nullptr), std::invalid_argument);
}

// For code that calls abort()/exit()
TEST(AssertTest, AbortsOnInvalidState) {
    EXPECT_DEATH(dangerousOp(), ".*invariant violated.*");
}
```

## CMakeLists.txt Integration

```cmake
enable_testing()

find_package(GTest REQUIRED)

add_executable(unit_tests
    tests/validator_test.cpp
    tests/user_service_test.cpp
)
target_link_libraries(unit_tests
    GTest::gtest_main
    GTest::gmock
    mylib
)

include(GoogleTest)
gtest_discover_tests(unit_tests)
```

## Running Tests

```bash
cmake --build build --target unit_tests
ctest --test-dir build --output-on-failure
ctest --test-dir build -R "UserService.*"  # filter by regex
```

## Google Benchmark

```cpp
#include <benchmark/benchmark.h>

static void BM_ParseJson(benchmark::State& state) {
    const std::string json = R"({"key": "value"})";
    for (auto _ : state) {
        benchmark::DoNotOptimize(parseJson(json));
    }
}
BENCHMARK(BM_ParseJson);
BENCHMARK_MAIN();
```
