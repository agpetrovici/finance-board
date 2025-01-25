export let categories = [
  "2023-01-01",
  "2023-02-01",
  "2023-03-01",
  "2023-04-01",
  "2023-05-01",
  "2023-06-01",
  "2023-71-10",
];

export let series = [
  [
    {
      name: "PRODUCT A",
      data: [
        {
          x: "2023-01-01",
          y: 11,
          tooltip: ["Element A - 1", "Element B - 5000", "Element C - 10000"],
        },
        { x: "2023-02-01", y: 55, tooltip: ["Custom tooltip for A - Jan 2"] },
        { x: "2023-03-01", y: 41, tooltip: ["Custom tooltip for A - Jan 3"] },
        { x: "2023-04-01", y: 67, tooltip: ["Custom tooltip for A - Jan 4"] },
        { x: "2023-05-01", y: 22, tooltip: ["Custom tooltip for A - Jan 5"] },
        { x: "2023-06-01", y: 43, tooltip: ["Custom tooltip for A - Jan 6"] },
        { x: "2023-07-01", y: 36, tooltip: ["Custom tooltip for A - Jan 7"] },
      ],
    },
    {
      name: "PRODUCT B",
      data: [
        { x: "2023-01-01", y: 44, tooltip: ["Custom tooltip for A - Jan 1"] },
        { x: "2023-02-01", y: 55, tooltip: ["Custom tooltip for A - Jan 2"] },
        { x: "2023-03-01", y: 41, tooltip: ["Custom tooltip for A - Jan 3"] },
        { x: "2023-04-01", y: 67, tooltip: ["Custom tooltip for A - Jan 4"] },
        { x: "2023-05-01", y: 22, tooltip: ["Custom tooltip for A - Jan 5"] },
        { x: "2023-06-01", y: 43, tooltip: ["Custom tooltip for A - Jan 6"] },
        { x: "2023-07-01", y: 36, tooltip: ["Custom tooltip for A - Jan 7"] },
      ],
    },
  ],
  [
    {
      name: "PRODUCT 1",
      data: [
        { x: "2023-01-01", y: 0, tooltip: ["Custom tooltip for 1 - Jan 1"] },
        { x: "2023-02-01", y: 55, tooltip: ["Custom tooltip for 1 - Jan 2"] },
        { x: "2023-03-01", y: 41, tooltip: ["Custom tooltip for 1 - Jan 3"] },
        { x: "2023-04-01", y: 67, tooltip: ["Custom tooltip for 1 - Jan 4"] },
        { x: "2023-05-01", y: 22, tooltip: ["Custom tooltip for 1 - Jan 5"] },
        { x: "2023-06-01", y: 43, tooltip: ["Custom tooltip for 1 - Jan 6"] },
        { x: "2023-07-01", y: 36, tooltip: ["Custom tooltip for 1 - Jan 7"] },
      ],
    },
    {
      name: "PRODUCT 2",
      data: [
        { x: "2023-01-01", y: 13, tooltip: ["Custom tooltip for 2 - Jan 1"] },
        { x: "2023-02-01", y: 0, tooltip: ["Custom tooltip for 2 - Jan 2"] },
        { x: "2023-03-01", y: 20, tooltip: ["Custom tooltip for 2 - Jan 3"] },
        { x: "2023-04-01", y: 8, tooltip: ["Custom tooltip for 2 - Jan 4"] },
        { x: "2023-05-01", y: 13, tooltip: ["Custom tooltip for 2 - Jan 5"] },
        { x: "2023-06-01", y: 27, tooltip: ["Custom tooltip for 2 - Jan 6"] },
        { x: "2023-07-01", y: 20, tooltip: ["Custom tooltip for 2 - Jan 7"] },
      ],
    },
    {
      name: "PRODUCT 3",
      data: [
        { x: "2023-01-01", y: 11, tooltip: ["Custom tooltip for 3 - Jan 1"] },
        { x: "2023-02-01", y: 17, tooltip: ["Custom tooltip for 3 - Jan 2"] },
        { x: "2023-03-01", y: 0, tooltip: ["Custom tooltip for 3 - Jan 3"] },
        { x: "2023-04-01", y: 15, tooltip: ["Custom tooltip for 3 - Jan 4"] },
        { x: "2023-05-01", y: 21, tooltip: ["Custom tooltip for 3 - Jan 5"] },
        { x: "2023-06-01", y: 14, tooltip: ["Custom tooltip for 3 - Jan 6"] },
        {
          x: "2023-07-01",
          y: 18,
          tooltip: ["Custom tooltip for 3 - Jan 7", "Other tooltip"],
        },
      ],
    },
  ],
  [
    {
      name: "PRODUCT 1",
      data: [
        { x: "2023-01-01", y: 0, tooltip: ["Custom tooltip for 1 - Jan 1"] },
        { x: "2023-02-01", y: 55, tooltip: ["Custom tooltip for 1 - Jan 2"] },
        { x: "2023-03-01", y: 41, tooltip: ["Custom tooltip for 1 - Jan 3"] },
        { x: "2023-04-01", y: 67, tooltip: ["Custom tooltip for 1 - Jan 4"] },
        { x: "2023-05-01", y: 22, tooltip: ["Custom tooltip for 1 - Jan 5"] },
        { x: "2023-06-01", y: 43, tooltip: ["Custom tooltip for 1 - Jan 6"] },
        { x: "2023-07-01", y: 36, tooltip: ["Custom tooltip for 1 - Jan 7"] },
      ],
    },
    {
      name: "PRODUCT 2",
      data: [
        { x: "2023-01-01", y: 13, tooltip: ["Custom tooltip for 2 - Jan 1"] },
        { x: "2023-02-01", y: 0, tooltip: ["Custom tooltip for 2 - Jan 2"] },
        { x: "2023-03-01", y: 20, tooltip: ["Custom tooltip for 2 - Jan 3"] },
        { x: "2023-04-01", y: 8, tooltip: ["Custom tooltip for 2 - Jan 4"] },
        { x: "2023-05-01", y: 13, tooltip: ["Custom tooltip for 2 - Jan 5"] },
        { x: "2023-06-01", y: 27, tooltip: ["Custom tooltip for 2 - Jan 6"] },
        { x: "2023-07-01", y: 20, tooltip: ["Custom tooltip for 2 - Jan 7"] },
      ],
    },
    {
      name: "PRODUCT 3",
      data: [
        { x: "2023-01-01", y: 11, tooltip: ["A", "B", "C"] },
        { x: "2023-02-01", y: 17, tooltip: ["Custom tooltip for 3 - Jan 2"] },
        { x: "2023-03-01", y: 0, tooltip: ["Custom tooltip for 3 - Jan 3"] },
        { x: "2023-04-01", y: 15, tooltip: ["Custom tooltip for 3 - Jan 4"] },
        { x: "2023-05-01", y: 21, tooltip: ["Custom tooltip for 3 - Jan 5"] },
        { x: "2023-06-01", y: 14, tooltip: ["Custom tooltip for 3 - Jan 6"] },
        {
          x: "2023-07-01",
          y: 18,
          tooltip: ["Custom tooltip for 3 - Jan 7", "Other tooltip"],
        },
      ],
    },
  ],
];
