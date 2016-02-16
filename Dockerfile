FROM wtsi-hgi/cookie-monster
MAINTAINER "C. Monster Esq." <cmonster@sanger.ac.uk>

# Install PostgreSQL development package for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev

# Install HGI Cookie Monster implementation
WORKDIR /cookie-monster
COPY requirements.txt the_monster.sh ./
COPY hgicookiemonster ./hgicookiemonster/
RUN pip install -r requirements.txt

# HTTP API on port 5000; /cookie-monster-setup bind mount for setup
EXPOSE 5000
VOLUME /cookie-monster-setup
ENTRYPOINT ["./the_monster.sh"]
