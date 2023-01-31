.env.nodered:
	cp .env.nodered.template .env.nodered

.env.webapp:
	cp .env.webapp.template .env.webapp

start-nodered: .env.nodered
	docker-compose build rednode-bnbc db-bnbc bnbc-redis
	docker-compose up rednode-bnbc db-bnbc bnbc-redis

start-webapp: .env.webapp
	docker-compose build bnbc-python
	docker-compose up bnbc-python
