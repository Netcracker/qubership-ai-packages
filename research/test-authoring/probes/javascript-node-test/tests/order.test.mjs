import { test } from 'node:test';

for (const name of ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']) {
  test(name, () => {});
}
