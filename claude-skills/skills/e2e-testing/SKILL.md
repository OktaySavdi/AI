---
name: "e2e-testing"
description: >
  Playwright end-to-end testing patterns covering Page Object Model, test fixtures,
  test data management, and CI integration. Activate when writing or reviewing E2E tests.
license: MIT
metadata:
  version: 1.0.0
  author: ECC
  category: testing
---

# E2E Testing Skill

## Page Object Model

```typescript
// pages/login.page.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  private readonly emailInput: Locator;
  private readonly passwordInput: Locator;
  private readonly submitButton: Locator;

  constructor(private page: Page) {
    this.emailInput = page.getByTestId('email-input');
    this.passwordInput = page.getByTestId('password-input');
    this.submitButton = page.getByRole('button', { name: 'Log in' });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

## Test Structure

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

test.describe('Authentication', () => {
  test('user can log in with valid credentials', async ({ page }) => {
    // Arrange
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // Act
    await loginPage.login('user@example.com', 'password');

    // Assert
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome')).toBeVisible();
  });

  test('shows error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('wrong@example.com', 'wrong');
    await expect(page.getByText('Invalid credentials')).toBeVisible();
  });
});
```

## Fixtures for Test Data

```typescript
// fixtures.ts
import { test as base } from '@playwright/test';

type Fixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('[data-testid=email]', process.env.TEST_USER_EMAIL!);
    await page.fill('[data-testid=password]', process.env.TEST_USER_PASSWORD!);
    await page.click('[type=submit]');
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

## playwright.config.ts

```typescript
export default defineConfig({
  testDir: 'tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['junit', { outputFile: 'results.xml' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
  },
});
```

## What to Test

- [ ] Critical user flows (auth, primary workflow, checkout)
- [ ] Error paths (invalid input, network failure, 404)
- [ ] Auth boundaries (unauthenticated requests redirect to login)
- [ ] Responsive layout (at least 2 viewports)

## What NOT to Test in E2E

- Unit-testable logic (test that in unit tests)
- Internal implementation details
- Every edge case (too slow, use integration tests)
