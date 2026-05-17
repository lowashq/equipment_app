FROM nginx:1.27-alpine

RUN printf '%s\n' \
    '<!doctype html>' \
    '<html lang="en">' \
    '<head><meta charset="utf-8"><title>University Equipment Rental</title></head>' \
    '<body><h1>University Equipment Rental</h1><p>React app placeholder.</p></body>' \
    '</html>' \
    > /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
