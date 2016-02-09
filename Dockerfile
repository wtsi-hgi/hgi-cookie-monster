FROM wtsi-hgi/cookie-monster
MAINTAINER "Human Genetics Informatics" <hgi@sanger.ac.uk>

# Install PostgreSQL development package for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev

COPY * /cookie-monster/
RUN pip install -r /cookie-monster/requirements.txt
