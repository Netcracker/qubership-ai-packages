import { expect, test } from "vitest";
import { isPositive, sumBelow } from "../src/numbers.js";

test("sums below four", () => {
  expect(sumBelow(4)).toBe(6);
});

test("positive and negative", () => {
  expect(isPositive(5)).toBe(true);
  expect(isPositive(-5)).toBe(false);
});
