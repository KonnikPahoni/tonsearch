#!/bin/bash

/etc/init.d/nginx stop
certbot certonly --standalone -d tonsearch.org

/etc/init.d/nginx start