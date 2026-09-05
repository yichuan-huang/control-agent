import { expect, test } from "vitest";
import { plotWindow } from "./plotWindow";
test("plot zoom and autorange map to bounded server window changes only once", () => {
  expect(
    plotWindow({ "xaxis.range[0]": 2, "xaxis.range[1]": 8 }, [null, null]),
  ).toEqual([2, 8]);
  expect(
    plotWindow({ "xaxis.range[0]": 2, "xaxis.range[1]": 8 }, [2, 8]),
  ).toBeUndefined();
  expect(plotWindow({ "xaxis.autorange": true }, [2, 8])).toEqual([null, null]);
  expect(plotWindow({ autosize: true }, [2, 8])).toBeUndefined();
  expect(
    plotWindow({ "xaxis.range[0]": 8, "xaxis.range[1]": 2 }, [null, null]),
  ).toBeUndefined();
});
