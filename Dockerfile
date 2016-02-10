FROM wtsi-hgi/cookie-monster
MAINTAINER "Human Genetics Informatics" <hgi@sanger.ac.uk>

# Install PostgreSQL development package for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev

# Install HGI Cookie Monster implementation
WORKDIR /cookie-monster
COPY requirements.txt the_monster.sh ./
COPY hgicookiemonster ./hgicookiemonster/
RUN pip install -r requirements.txt

# Copy setup
COPY setup.conf /cookie-monster/

EXPOSE 5000
ENTRYPOINT ["./the_monster.sh"]
