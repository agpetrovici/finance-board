# Finance Board

A simple finance board for personal use.

Currently a work in progress.

It supports several banks and accounts.
It uses a local PostgreSQL database to store the data and a Flask backend to serve the data.

![Finance Board](./docs/finance-board-line.png)

Displays the transactions per month with details over tooltips.

![Finance Board](./docs/finance-board-column-chart.png)

## Data Import

- Desktop
  - [![Watch the video](https://img.youtube.com/vi/rdT5S6Wx1_Q/hqdefault.jpg)](https://www.youtube.com/watch?v=rdT5S6Wx1_Q)
- Mobile
  - [![Watch the video](https://img.youtube.com/vi/u1pUBUBylOU/hqdefault.jpg)](https://www.youtube.com/watch?v=u1pUBUBylOU)

## Installation

1. Clone the repository.
2. Install the dependencies defined in pyproject.toml.
3. Create the PostgreSQL database.
4. Define the environment variables in `.env` defined in `.env.example`.
5. Generate a self signed `cert.pem` and `key.pem` with `openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365`
6. Run the Flask backend `main.py`.
