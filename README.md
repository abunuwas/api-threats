# API THREATS

Welcome to *API Threats*!

API Threats helps you master API security with practical challenges.

This repository hosts the source code of each challenge.

The official website is https://apithreats.com.

I publish a new challenge every 2 weeks.

Every challenge has two parts:
* Hacking an API to find its vulnerabilities on https://apithreats.com
* Looking at the source code in this repo to pinpoint the root cause of the vulnerability

Every two weeks, I deploy the vulnerable API to https://apithreats.com, 
and you have one week to hack the API and find the vulnerabilities.

The following week, I share the API code in this repository, 
and you have another week to go through the code and find the 
root cause of the vulnerability and suggest a fix.

If you want to participate, submit your solutions on https://apithreats.com. Instructions below :fingerdown

I raffle a signed copy of my book "Microservice APIs" among all participants every week!

The API security challenges are hosted on https://apithreats.com

## INTRODUCING API THREATS

We're API pros, there's no UI here. Except for a Swagger and a Redoc UIs, that is.

You can load the API Threats API in 3 ways:

> Swagger UI: https://apithreats.com/docs

> Redoc UI:. https://apithreats.com/redoc

> OpenAPI spec: https://apithreats.com/openapi.json

Explanation:
---
We have a public endpoint GET /challenges, which gives you a list of all the challenges available.

The rest of the endpoints allow you to:
> publish your solutions to the challenges, 
> get a list of your solutions
> and update your solutions with a link.

Since those endpoints access private resources, they are protected, so you'll need to log in.
See below how to create an account and log in:down

HOW TO LOG IN AND AUTHORIZE YOUR REQUESTS

Go to https://apithreats.com/login

If you don't have an account yet, create one.

I've done login with Auth0. To make it as simple as possible for you, I'm using the authorization code flow, 
so you just need register/login, and I handle everything else in the backend. If all goes well, you'll see 
your access token in the response from the API.

To access the protected endpoints, click on the "Authorize" button on the Swagger UI and paste your token.

If you access the API from a terminal, Postman, or using code, just include the access token as a 
Bearer token in the Authorization header.

If the token expires, log in again.

Hopefully all this makes sense. If it doesn't, reach out to me, and I'll be glad to help.

HOW TO WORK ON THE CHALLENGES

Let's say you want to work on challenge 0001.

First, load the challenge details from its resource endpoint: https://apithreats.com/challenges/0001/docs

This week's challenge is challenge 0001. We have an API that allows us to place orders and check their details. But there's something off in the access controls. Can you guess what it is?

HINT: you'll need to create two accounts.

We have 2 endpoints:

> POST /orders to place orders

> GET /orders/{id} to get the details of an order

Plus

> POST /solutions to post your solution to the challenge

> POST /solutions/{solution_id}/link to add a link to your LinkedIn post

HOW TO PARTICIPATE

1. Go to https://apithreats.com/login and create an account and get your access token follow the steps described earlier

2. Go https://apithreats.com/challenges/0001/docs, play with the API and try to find th vulnerability

3. Once you've found the vulnerability, publish your solution to POST https://apithreats.com/challenges/0001/solutions

BONUS - To increase the chances of winning a signed copy of "Microservice APIs" :down

4. Publish your solution on LinkedIn tagging me or microapis.io

5. Like and share this post

6. Reply to this post

I'm rolling out API Threats as we speak, so it's possible you'll encounter errors. If that happens, please let me know and I'll fix them promptly.

Let the hunger games start!!!
