# TON NFT Scan

SQL database of TON NFTs.

#### Useful links

- Django admin: [http://localhost:8008/admin/](http://localhost:8001/admin/).

## Local development

- Install [Docker](https://docs.docker.com/engine/install/ubuntu/)
  and [Docker Compose](https://docs.docker.com/compose/install/)
- Copy `.env.dist` to `.env` and populate variables
- Build and start docker containers with `docker-compose build && docker-compose up`
- Enter the container environment with `docker container exec -it tonnftscan.app bash`
- Execute management commands from inside the container with `python3 manage.py <command>`
- - To view emails cron logs run `tail -1000 var/mail/mail` from inside the container

#### Code style

We use Black code style with settings in `pyproject.toml`. Run `black .` to lint code.

#### Available commands

- `python manage.py createsuperuser` to crate superuser
- `certbot certonly --standalone -d tonsearch.org`