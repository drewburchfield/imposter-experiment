FROM nginx:alpine

# Copy the static files to nginx html directory
COPY index.html /usr/share/nginx/html/
COPY README.md /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# nginx will run automatically with default config
