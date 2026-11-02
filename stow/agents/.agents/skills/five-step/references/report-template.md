# Five-step report

Keep it short. Numbers where you have them. "Not measured" where you do not.

```markdown
## Five-step report: <scope>

### Deleted
- <code, abstraction, requirement, dependency, or process removed, with evidence it was unused or unneeded>

### Simplified
- <architecture or implementation change and the reader-load it removed>

### Optimized
- <runtime or cycle-time improvement, with the before and after measurement>

### Automated
- <script, check, or generator added, and the manual step it replaces>

### Testing
- <tests added, changed, removed>
- <commands run and results>

### Breaking changes
- <removed or changed contract, who it affects, migration note>

### Remaining opportunities
- <significant simplification deferred, and why>
```

The measure of success is how much unnecessary complexity is gone for good, not how much code changed.
