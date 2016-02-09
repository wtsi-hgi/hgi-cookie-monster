FROM wtsi-hgi/cookie-monster
MAINTAINER "Human Genetics Informatics" <hgi@sanger.ac.uk>

# Install PostgreSQL development package for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev

# Install HGI Cookie Monster implementation
COPY requirements.txt /cookie-monster/
COPY hgicookiemonster /cookie-monster/hgicookiemonster/  
RUN pip install -r /cookie-monster/requirements.txt

# Copy setup
COPY setup.conf /cookie-monster
