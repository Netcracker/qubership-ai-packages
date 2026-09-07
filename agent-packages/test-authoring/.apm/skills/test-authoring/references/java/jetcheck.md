# jetCheck

How a property-based test on the JVM is written with jetCheck, what a falsified property prints, and what the T1
reader needs from the file to rerun it. The rule that uses this file is `SKILL.md` §4, the property-based test.

## What a falsified property prints

```text
org.jetbrains.jetCheck.PropertyFalsified:
Falsified on -1
Shrunk in 28 stages, by trying 31 examples

To re-run the minimal failing case, run
  PropertyChecker.customized().rechecking("8Kaashzk7pPUHgH/////Hw==")
    .forAll(...)
To re-run the test with all intermediate shrinking steps, use `recheckingIteration(-2079737578537190492L, 1)` instead for last iteration, or `withSeed(-2079737578537190492L)` for all iterations
```

The message carries the shrunk counterexample as the generator's `toString` of the value, the reproduce blob, and the
seed. The test name and the message therefore have to say which property was falsified, because `Falsified on -1`
does not: name the test for the invariant (`ensureBytesNeverReturnsANegativeCount`), and build the generator so the
value prints as the reader will read it.

## The shape

```java
@Test
void ensureBytesNeverReturnsANegativeCount() {
    PropertyChecker.forAll(Generator.integers(), n -> stream.ensureBytes(n) >= 0);
}
```

- **The message is the reproducer.** Every failure prints the `rechecking(blob)` call that replays the minimal case
  and the `withSeed(seed)` call that replays the whole iteration, so the test does not pin a seed: a pinned seed
  explores the same values on every run. Use `withSeed` while diagnosing, and take it out with the fix.
- **Every counterexample the tool ever found becomes an explicit test**, a plain `@Test` beside the property with the
  value as a literal, so the failure has a name and survives a change of generator. `ImperativeCommand` scenarios
  (`checkScenarios`) are for stateful properties, where the counterexample is a command sequence and the explicit
  test replays it.
- **The predicate is the specification's invariant, not the implementation's.** `ensureBytes(n) == n` restates the
  code; `ensureBytes(n) >= 0` is a claim the specification makes.
- **The generator covers the domain the invariant is stated over**, boundaries included: `Generator.integers()` reaches
  `Integer.MIN_VALUE`, a hand-built range may not.
