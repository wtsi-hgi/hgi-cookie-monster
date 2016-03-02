FROM wtsi-hgi/cookie-monster
MAINTAINER "C. Monster Esq." <cmonster@sanger.ac.uk>

# Install PostgreSQL development package for psycopg2
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq-dev

# Install HGI Cookie Monster implementation
WORKDIR /cookie-monster
COPY requirements.txt the_monster.sh ./
COPY hgicookiemonster ./hgicookiemonster/

# pip can go die in a fire
RUN pip uninstall -y cookiemonster \
                     baton-python-wrapper
RUN pip install -r requirements.txt
RUN curl $(sed -rn "s|^git\+https://github.com/(.+).git@(.+)#egg=.+$|https://raw.githubusercontent.com/\1/\2/requirements.txt|p" requirements.txt) \
  | xargs pip install

EXPOSE 5000
ENTRYPOINT ["./the_monster.sh"]