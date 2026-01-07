FROM nginx:alpine

# Copy the static files to nginx html directory
COPY --chmod=644 index.html /usr/share/nginx/html/index.html
COPY --chmod=644 README.md /usr/share/nginx/html/README.md

# Ensure proper permissions
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# nginx will run automatically with default config
