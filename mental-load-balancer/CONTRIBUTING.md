# Contributing to Mental Load Balancer

We love your input! We want to make contributing to Mental Load Balancer as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mental-load-balancer.git
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the extension:
   ```bash
   npm run compile
   ```

4. Run tests:
   ```bash
   npm test
   ```

## Project Structure

```
mental-load-balancer/
├── src/                    # Source files
│   ├── extension.ts        # Main extension logic
│   ├── mentalState.ts      # Mental state tracking
│   ├── jokeEngine.ts       # Joke generation
│   ├── backoff.ts         # Backoff strategy
│   └── types.ts           # TypeScript interfaces
├── test/                  # Automated tests
├── .vscode/              # VS Code integration files
├── package.json          # Dependencies and commands
└── tsconfig.json         # TypeScript configuration
```

## Adding New Features

### Mental State Tracking
To add new metrics to track:
1. Add new fields to `MentalStateMetrics` interface in `types.ts`
2. Implement tracking in `MentalStateTracker` class
3. Update pressure score calculation
4. Add relevant tests

### Joke Engine
To add new joke categories:
1. Add new category to `jokeTemplates` in `JokeEngine`
2. Update context detection logic
3. Add language-specific jokes if relevant

### UI Components
For new UI features:
1. Follow VS Code's webview guidelines
2. Use CSS variables for theming
3. Ensure accessibility
4. Add proper error handling

## Code Style

- Use TypeScript strictly typed
- Follow VS Code extension guidelines
- Use async/await for promises
- Document public APIs
- Write meaningful commit messages

## Testing

Please write tests for new code. Test examples:

```typescript
describe('MentalStateTracker', () => {
    it('should calculate pressure score correctly', () => {
        const tracker = new MentalStateTracker();
        // Add test implementation
    });
});
```

## Documentation

### Code Documentation
- Use JSDoc for public APIs
- Include examples in complex functions
- Document configuration options

### User Documentation
- Update README.md for feature changes
- Add examples for new settings
- Include screenshots if relevant

## Pull Request Process

1. Update the README.md with details of changes
2. Update the version number in package.json
3. Add your changes to CHANGELOG.md
4. The PR will be merged once you have sign-off

## Any questions?

Feel free to open an issue or contact the maintainers.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.