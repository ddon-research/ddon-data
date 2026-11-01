cmake_minimum_required(VERSION 3.20)
project(plbatch CXX)

# PatternLanguage checkout at master 300d7388 (2026-09-13; UTF-8 JSON strings, see README); build.sh fetches it.
set(PL_SOURCE_DIR "" CACHE PATH "PatternLanguage source tree at 300d7388475dd7ffd04239dfc889b72fe08bae18")
if (NOT EXISTS "${PL_SOURCE_DIR}/lib/include/pl/pattern_language.hpp")
    message(FATAL_ERROR "PL_SOURCE_DIR='${PL_SOURCE_DIR}' is not a PatternLanguage checkout (run build.sh)")
endif ()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(LIBPL_ENABLE_CLI OFF CACHE BOOL "" FORCE)
set(LIBPL_ENABLE_TESTS OFF CACHE BOOL "" FORCE)
set(LIBPL_ENABLE_EXAMPLE OFF CACHE BOOL "" FORCE)
set(LIBPL_SHARED_LIBRARY OFF CACHE BOOL "" FORCE)
add_subdirectory("${PL_SOURCE_DIR}" pl EXCLUDE_FROM_ALL)

add_executable(plbatch plbatch.cpp)
# nlohmann_json: the copy PatternLanguage bundles (its target is global; the variable is not), used
# to validate every JSON output.
target_link_libraries(plbatch PRIVATE libpl libpl-gen nlohmann_json ${FMT_LIBRARIES})
if (MINGW)
    # One self-contained exe: no libstdc++/libgcc/winpthread DLLs beside it.
    target_link_options(plbatch PRIVATE -static)
endif ()
