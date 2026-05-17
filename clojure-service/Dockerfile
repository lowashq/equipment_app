FROM alpine:3.20

RUN mkdir -p /www \
    && printf '%s\n' '{"status":"decision-engine-placeholder"}' > /www/index.html

EXPOSE 3001

CMD ["busybox", "httpd", "-f", "-p", "3001", "-h", "/www"]
