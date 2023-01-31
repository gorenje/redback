# Redback - Node-Red as Backend

A initial attempt to use [Node-Red](https://nodered.org/) as a complete and inclusive backend for a web application.

The web application is a minimal-viable bidding platform, the aim is to allow users to create auctions quickly and easily without major overhead. User registration and login is done via email and login codes are sent via email.

A big warning from the start: everything I describe here is **working in progress**, must of the features are implemented but aren't rock-solid or cover every possible eventuallity.

## Proof of Concept.

This is an attempt to partially implement everything that is required for a production ready minimal-viable bidding platform using Node-Red. 

Once everything is in place, it can be extended as necessary. Production ready includes quality assurance and customer support (for example), hence time was spent building tools that support those activities.

## Motivation

I have always been a big fan of [Yahoo Pipes](https://en.wikipedia.org/wiki/Yahoo!_Pipes) and have been looking for a similar tool for years. [Node-Red](https://nodered.org/) is an superb emulation of Yahoo Pipes:

> Node-RED is a programming tool for wiring together hardware devices, APIs and online services in new and interesting ways.

> It provides a browser-based editor that makes it easy to wire together flows using the wide range of nodes in the palette that can be deployed to its runtime in a single-click.

So I decided to have a play around with it and initially had no idea what I could do with it (not having any IoT device at home). Then I had an idea for an auction/bidding site and thought that I would try out Node-Red instead of the usual Python front and backend solution. 

## Bidding/Auction Platform - why?

Because there isn't just one type of Apple(tm) in this world.

The idea behind this platform is a slightly different idea than normal bidding platforms. Normal auctions sellers make buyers, what if this is turned around and buyers make sellers? I become a buyer when I have the highest bid for something someone is selling, what if I offer to buy something from someone who never intended to sell it?

## Architecture & Features & Design Decisions

Architecture is very simple: 

- Node-Red as API, (web-)socket and admin tool endpoint;
- Postgres as datastore;
- Python as web frontend solely interacts with the Node-Red provided API, no direct contact to Postgres;
- Web-front using jQuery and connecting to the Node-Red (web-)socket endpoint.

Whether this scales is another story. But it has many advantages over coding a backend in Python on some other editor-based programming-languages.

### Design Decisions

Some of the design decisions made:

- Keep the entry barriers low and human interchange (via the platform) to a minimum.
- No password, no social media logins, no chat, no image uploads. 
- No financial transactions on the platform, all payments handled off-site, peer-to-peer.
- Python web frontend has no contact to Postgres database, all communication is done via an API provided by Node-Red. API provided should also be utilisable for mobiles apps or other integration into other applications.
- Provide a white-label solution, no branding.

### Features

- Simple but functional web frontend built with python-flask
- Realtime bidding and auction notifications via web-sockets 
- Admin tool for admin tasks such as content moderation and user banning, i.e. those activities that are done by customer support. This is built on top of the Node-Red dashboard and provides initial functionality.
- Initial content moderation done by [OpenAI Q&A API](https://platform.openai.com/examples/default-qa)
- Email delivery using [Fastmail JMap](https://www.fastmail.com/blog/jmap-new-email-open-standard/)
- Templated based Emails (both HTML and text)
- Dockerisation for local usage
- Documentation for QA support
- Functionality in the database via Postgres triggers and functions because these can be modelled. This goes against frameworks such as Rails that maintain a dumb database is a good database.

## Getting Started

Minimum requirement are [make](https://en.wikipedia.org/wiki/Make_(software)) and [docker](https://en.wikipedia.org/wiki/Docker_(software)) to get started. 

Steps:

- `make start-nodered` will initialise, start both Node-Red and Postgres. Redis is also started for the Python frontend.
- `make start-webapp` will start the Python frontend.

Each step needs to be done in its own terminal window.

After that, Node Red can be accessed via [http://127.0.0.1:1880](http://127.0.0.1:1880) and the web frontend via [http://127.0.0.1:8082](http://127.0.0.1:8082).

I won't go into the details of sign up, login and create auctions, that is beyond the scope. 

## Repository Structure

I have deployed all this to Heroku and hence the top-level structure is a python webapp that is deployable to heroku.

Node-Red is deployed by updating flows on heroku. I installed Node-Red using this [repo](https://github.com/gorenje/node-red-heroku). The Node-Red [flow.json](/node-red/data/flows.json) contains the entire backend, credentials are stored in `.env` files on the top-level.

When running Node-Red locally, changes made to the flow are stored in the repo, i.e., each deploy overwrites the `flows.json` in this repo. 

The [database schema](/postgres/database-schema.sql) was generated using [pgModeler](https://pgmodeler.io/) which meant that I used a lot more functionality within the database than in the application. For example, `updated_at` fields are updated via postgres triggers and not via an ORM. Database changes are trigger and will remain so.

## Lesson Learnings

These are all my personal opinions and learnings, your mileage will vary.

I have tried to keep the Node-Red flows as clear as possible but flows are similar to codebases, they get very confusing and interwoven very quickly. It is easy to lose the overview when several flows are defined in one flow tab.

Node-Red requires just as much discipline as coding. Refactoring and descriptive naming are even more important than when coding. 

The gains that business flows and logic are clearly visible makes Node-Red perfect for product-managers who which to have an idea what is happening in the boiler rooms. I have tried to create flows that focus on core logic. 

For example, I created a flow that handles the routing: all HTTP requests come in to this flow. They are then, as a good router does, distributed to other flows based on their HTTP method and path. This provides an overview of all API endpoints, using a single giant flow!

Email templates are another example. All email templates (both HTML and text) are defined in a single flow. This then allows those that design the emails to easily change them, without having to asking developers or checking out codebases themselves.

These things only make sense if one has gone through the pain of updating email templates in the codebase or have tried to find the code that is run for a specific API endpoint.

