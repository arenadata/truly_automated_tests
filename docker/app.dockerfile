# Official PHP image
FROM php:fpm
# Install other requirements
RUN apt-get update \
    && apt-get install -y \
       unzip
# Install composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer
# Install required extensions
RUN docker-php-ext-install pdo_mysql
RUN pecl install xdebug \
    && docker-php-ext-enable xdebug
# Add user for an application
RUN groupadd -g 1000 www
RUN useradd -u 1000 -ms /bin/bash -g www www
# Change user
USER www
