FROM ruby:3.3-alpine

RUN apk add --update --no-cache ruby-dev build-base libxml2-dev libxslt-dev
RUN gem install bundler:2.5.14
RUN gem i fastlane

ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

ENTRYPOINT ["fastlane"]
CMD []