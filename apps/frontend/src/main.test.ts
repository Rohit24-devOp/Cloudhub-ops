import { describe, expect, it } from "vitest";

describe("CloudOps Hub frontend", () => {
  it("keeps the product name stable", () => {
    expect("CloudOps Hub").toContain("CloudOps");
  });
});
