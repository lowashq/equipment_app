FROM nginx:1.27-alpine

RUN printf '%s\n' \
    'server {' \
    '    listen 3001;' \
    '    server_name localhost;' \
    '    location / {' \
    '        default_type application/json;' \
    '        return 200 "{\"status\":\"decision-engine-placeholder\"}";' \
    '    }' \
    '}' \
    > /etc/nginx/conf.d/default.conf

EXPOSE 3001

CMD ["nginx", "-g", "daemon off;"]
