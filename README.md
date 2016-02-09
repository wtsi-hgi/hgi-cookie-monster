# The HGI Monster

The HGI implementation of Cookie Monster

# Containerised Setup

1. Build the [`docker-baton`](https://github.com/wtsi-hgi/docker-baton)
   image using the HGI `feature/specificquery` fork of baton, with the
   tag `wtsi-hgi/baton:0.16.1-specificquery`.

2. Build the [`docker-cookie-monster`](https://github.com/wtsi-hgi/docker-cookie-monster)
   image, with the tag `wtsi-hgi/cookie-monster`.

3. Build the image from this repository, using the tag
   `wtsi-hgi/the-monster`.

**TODO** iRODS setup here

The container can now be run with:

    docker run -d -p 5000:5000 wtsi-hgi/the-monster

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
