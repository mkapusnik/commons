FROM debian:buster

ENV ANDROID_VERSION="33"
ENV ANDROID_VERSION_v2="31"
ENV ANDROID_BUILD_TOOLS_VERSION="33.0.0"
ENV ANDROID_BUILD_TOOLS_VERSION_2="30.0.3"
ENV TOOLS_VERSION="5.0"
ENV ANDROID_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip"
ENV ANDROID_ROOT="/opt/android_sdk"
ENV FLUTTER_ROOT="/opt/flutter"
ENV PATH="$ANDROID_ROOT/cmdline-tools/tools/bin:$ANDROID_ROOT/platform-tools:$ANDROID_ROOT/platforms:$FLUTTER_ROOT/bin:$PATH"

RUN apt-get update -y && apt-get install -y unzip curl git default-jdk-headless && apt-get clean && rm -rf /var/lib/{apt,dpkg,cache,log}

# Install the Android SDK Dependency.
RUN mkdir -p /home/$USER/.android \
  && touch /home/$USER/.android/repositories.cfg \
  && curl -o android.zip $ANDROID_TOOLS_URL \
  && mkdir -p $ANDROID_ROOT/cmdline-tools \
  && unzip -qq -d $ANDROID_ROOT/cmdline-tools android.zip \
  && rm android.zip \
  && mv $ANDROID_ROOT/cmdline-tools/cmdline-tools $ANDROID_ROOT/cmdline-tools/tools

RUN yes "y" | sdkmanager "--update" "--verbose" \
  && yes "y" | sdkmanager "build-tools;$ANDROID_BUILD_TOOLS_VERSION" \
  && yes "y" | sdkmanager "build-tools;$ANDROID_BUILD_TOOLS_VERSION_2" \
  && yes "y" | sdkmanager "platforms;android-$ANDROID_VERSION" \
  && yes "y" | sdkmanager "platforms;android-$ANDROID_VERSION_v2" \
  && yes "y" | sdkmanager "cmdline-tools;$TOOLS_VERSION" \
  && yes "y" | sdkmanager "platform-tools" \
  && yes "y" | sdkmanager "ndk;23.0.7599858"

RUN git clone -b stable --depth 1 --single-branch https://github.com/flutter/flutter "${FLUTTER_ROOT}"
RUN flutter update-packages
RUN flutter config --no-analytics \
  && flutter precache --no-ios --no-macos \
  && yes "y" | flutter doctor --android-licenses \
  && flutter doctor -v

ENTRYPOINT [ "flutter" ]