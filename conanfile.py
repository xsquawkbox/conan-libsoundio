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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

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
        }
        if self.options.shared:
            build_defs['BUILD_DYNAMIC_LIBS'] = True
            build_defs['BUILD_STATIC_LIBS'] = False
        else:
            build_defs['BUILD_DYNAMIC_LIBS'] = False
            build_defs['BUILD_STATIC_LIBS'] = True
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