from conans import ConanFile, CMake, tools

class LibsoundioConan(ConanFile):
    name = "libsoundio"
    version = "2.0.0"
    license = "MIT"
    author = "Chris Collins <kuroneko@sysadninjas.net>"
    url = "https://github.com/xsquawkbox/conan-libsoundio"
    description = "libsoundio portable audio library"
    topics = ("audio", "portability")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_jack": [True, False],
        "enable_alsa": [True, False],
        "enable_pulseaudio": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_jack": False,
        "enable_alsa": True,
        "enable_pulseaudio": True,
    }
    generators = "cmake"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if self.settings.os != 'Linux':
            del self.options.enable_jack
            del self.options.enable_alsa
            del self.options.enable_pulseaudio

    def source(self):
        git = tools.Git("libsoundio")
        git.clone(url="https://github.com/xsquawkbox/libsoundio.git", branch="%s-xsb"%self.version)
        tools.replace_in_file("libsoundio/CMakeLists.txt", "project(libsoundio C)",
                              '''project(libsoundio C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def _configure_cmake(self):
        build_defs = {
            'BUILD_DYNAMIC_LIBS': None,
            'BUILD_STATIC_LIBS': None,
            # Examples & Tests fail on windows due to no unistd.h
            'BUILD_EXAMPLE_PROGRAMS': False,
            'BUILD_TESTS': False,
            'ENABLE_JACK': False,
            'ENABLE_PULSEAUDIO': False,
            'ENABLE_ALSA': False,
        }
        if self.options.shared:
            build_defs['BUILD_DYNAMIC_LIBS'] = True
            build_defs['BUILD_STATIC_LIBS'] = False
        else:
            build_defs['BUILD_DYNAMIC_LIBS'] = False
            build_defs['BUILD_STATIC_LIBS'] = True
        if 'enable_jack' in self.options:
            build_defs['ENABLE_JACK'] = self.options.enable_jack
        if 'enable_pulseaudio' in self.options:
            build_defs['ENABLE_PULSEAUDIO'] = self.options.enable_pulseaudio
        if 'enable_alsa' in self.options:
            build_defs['ENALBE_ALSA'] = self.options.enable_alsa
        if self.settings.os == 'Windows':
            build_defs['ENABLE_COREAUDIO'] = False
        elif self.settings.os == 'Macos':
            build_defs['ENABLE_WASAPI'] = False
        else:
            build_defs['ENABLE_COREAUDIO'] = False
            build_defs['ENABLE_WASAPI'] = False
        cmake = CMake(self)
        cmake.configure(defs=build_defs, source_folder="libsoundio")
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["soundio"]
        if not self.options.shared:
            self.cpp_info.defines += ['SOUNDIO_STATIC_LIBRARY']
            if self.settings.os == 'Macos':
                self.cpp_info.frameworks += ['CoreAudio', 'AudioUnit', 'CoreFoundation']
            if self.settings.os == 'Linux':
                if self.options.enable_jack:
                    self.cpp_info.libs += ['jack']
                if self.options.enable_pulseaudio:
                    self.cpp_info.libs += ['pulse']
                if self.options.enable_alsa:
                    self.cpp_info.libs += ['asound']
                self.cpp_info.libs += ['pthread']
