IMAGE ?= ros2-lecture:jazzy
# Registry image for `make push`, e.g. ghcr.io/<owner>/ros2-lecture:jazzy
REGISTRY_IMAGE ?= ghcr.io/CHANGE_ME/ros2-lecture:jazzy
PLATFORMS ?= linux/amd64,linux/arm64

.PHONY: build up down logs shell push clean-ws

build:            ## build the image for this machine
	docker build -t $(IMAGE) .

up:               ## start the lecture environment 
	docker compose up -d
	@echo "Desktop: http://localhost:6080   VS Code: http://localhost:8080"

down:             ## stop it (workspace files are kept)
	docker compose down

logs:
	docker compose logs -f

shell:            ## terminal inside the container as user 'ros'
	docker compose exec -u ros ros bash

push:             ## manual multi-arch push (normally done by .github/workflows/build.yml)
	docker buildx build --platform $(PLATFORMS) -t $(REGISTRY_IMAGE) --push .

clean-ws:         ## remove colcon build artefacts from the workspace
	rm -rf workspace/build workspace/install workspace/log
