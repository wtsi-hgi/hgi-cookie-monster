# The HGI Monster

The HGI implementation of Cookie Monster.

# Containerised Setup

1. Build the Docker image from this repository, using the tag
   `wtsi-hgi/the-monster`.

2. Ensure your Cookie Monster `setup.conf` is specified per
   `setup.example.conf`.

3. Ensure your iRODS environment configuration file
   (`~/.irods/.irodsEnv` or `~/.irods/irods_environment.json`) has
   Kerberos authentication disabled by removing the appropriate iRODS
   authentication scheme line. Your `~/.irods` directory will ultimately
   be bind mounted into the Docker container.

4. Start the Docker container in interactive mode, with the `~/.irods`
   bind mount:

   ```sh
   docker run -it \
              -v /path/to/your/.irods:/root/.irods \
              --entrypoint=/bin/bash \
              wtsi-hgi/the-monster
   ```

   ...When at the shell prompt, run `iinit` and enter your iRODS
   password. This will create the `.irodsA` file in the bind mount,
   which will be reciprocated on the host. Note that the ownership of
   the host's iRODS configuration will change to `root`.

5. Now you can run the container. To avoid having to rebuild the image
   when changes need to be made to the rules, enrichment loaders or
   notification receivers, they can also be bind mounted:

   ```sh
   docker run -d \
              -p 50666:5000 \
              -v /path/to/your/setup:/root/.cookie-monster \
              -v /path/to/your/.irods:/root/.irods \
              -v /path/to/your/rules:/cookie-monster/hgicookiemonster/rules \
              -v /path/to/your/enrichment_loaders:/cookie-monster/hgicookiemonster/enrichment_loaders \
              -v /path/to/your/notification_receivers:/cookie-monster/hgicookiemonster/notification_receivers \
              wtsi-hgi/the-monster
   ```

# License

Copyright (c) 2016 Genome Research Ltd.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <http://www.gnu.org/licenses/>.
