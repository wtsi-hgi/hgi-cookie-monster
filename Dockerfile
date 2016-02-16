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

EXPOSE 5000
ENTRYPOINT ["./the_monster.sh"]
