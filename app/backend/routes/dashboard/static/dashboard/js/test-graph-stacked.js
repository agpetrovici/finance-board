import { categories, series } from "./test-data.js";

import { graphBarStacked } from "./graph-bar-stacked.js";

graphBarStacked(series, categories, "#column-chart-categories");
