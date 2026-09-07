# ArchUnit

How a test on an open set of classes is written on the JVM, and what a violation prints. The rule that uses this file
is `SKILL.md` §4, the test on an open set. ArchUnit is the tool where the set is the classes on the class path that
satisfy a predicate: every implementation of an interface, every class in a package, every class with an annotation.
Where the set is the constants of an enum, `EnumSet.allOf` or `values()` and a plain assertion do the job without a
library.

## The two shapes

**A rule over the set.** Every member has to satisfy a predicate; the report lists the members that do not.

```java
JavaClasses prod = new ClassFileImporter()
    .withImportOption(new ImportOption.DoNotIncludeTests())
    .importPackages("m");

classes().that().implement(Handler.class)
    .should().beAnnotatedWith(Handles.class)
    .check(prod);
```

Fails with the rule's own text as the message and one line per violating class:

```text
Architecture Violation [Priority: MEDIUM] - Rule 'classes that implement m.Handler should be annotated with @Handles' was violated (1 times):
Class <m.BHandler> is not annotated with @Handles in (BHandler.java:0)
```

**The set against a second set.** The members found on the class path are compared with the members another place
enumerates, and the assertion prints both sides:

```java
Set<Kind> handled = prod.stream()
    .filter(c -> c.isAssignableTo(Handler.class) && !c.isInterface() && c.isAnnotatedWith(Handles.class))
    .map(c -> c.getAnnotationOfType(Handles.class).value())
    .collect(toSet());
assertEquals(EnumSet.allOf(Kind.class), handled, "kinds with a Handler implementation");
```

Fails as `kinds with a Handler implementation ==> expected: <[A, B, C]> but was: <[A]>`, and the missing members are
read off the two sets.

## What the reviewer checks

- **The set is read from the code, and the predicate from the specification.** The test fires on the next author's
  addition because it reads the members from the class path; the property each member has to satisfy is still a
  literal or a hand-written predicate, never derived from the same members.
- **The import excludes the tests** (`DoNotIncludeTests`), or the test's own fixtures join the set.
- **A `@ArchTest` field with `ArchRule` under `@AnalyzeClasses`** caches the import across rules in one class; a
  fresh `ClassFileImporter` per test is right where one rule is all there is.
- **Freezing** (`FreezingArchRule.freeze(rule)`) records today's violations and fails only on new ones. It is for a
  rule adopted over a legacy set; a new rule on a new set has no violations to freeze.
