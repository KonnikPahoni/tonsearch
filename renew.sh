#!/bin/bash

service nginx stop

certbot certonly --standalone -d tonsearch.org

service nginx start