# Official PHP image
FROM php:apache
# Install other requirements
RUN apt-get update \
    && apt-get install -y \
       unzip
# Install composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer
# Configure apache
RUN  rm /etc/apache2/sites-available/000-default.conf \
     && rm /etc/apache2/sites-enabled/000-default.conf
COPY ./docker/apache2.conf /etc/apache2/apache2.conf
# Enable rewrite module
RUN a2enmod rewrite
# Copy sources
COPY ./app /var/www/html
WORKDIR /var/www/html
# Installing dependecies
RUN composer install --optimize-autoloader --no-scripts --no-dev --profile --ignore-platform-reqs -vv
# Init database
RUN touch storage/app/arenadata_db.sqlite
ENV DB_CONNECTION=sqlite
ENV DB_DATABASE=/var/www/html/storage/app/arenadata_db.sqlite
ENV DB_FOREIGN_KEYS=true
RUN php artisan migrate --force
RUN php artisan db:seed --force
# Fix permissions
RUN chgrp -R www-data storage /var/www/html/storage
RUN chmod -R ug+rwx storage /var/www/html/storage
