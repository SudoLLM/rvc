build:
	docker build -t rvc_api -f Dockerfile.api .

run:
	docker compose -f docker-compose.api.yml up -d