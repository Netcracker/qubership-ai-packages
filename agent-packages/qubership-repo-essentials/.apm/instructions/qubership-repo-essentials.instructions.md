---
description: Backward compatibility of released contracts.
applyTo: "**"
---

## Backward compatibility

A released contract keeps working for existing consumers: a public API, a CLI flag, a configuration key, a Helm value,
a CR field, an environment variable, a default, stored data, a wire format. Released means present in a release tag;
anything added after the last release may still change. Instead of renaming, removing, making an optional parameter
required, or changing a default, add an optional parameter or keep the old name as a deprecated alias. A removal needs
a deprecation at least 3 years old and a new major version.
