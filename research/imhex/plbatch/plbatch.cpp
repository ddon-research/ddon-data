// plbatch: run one ImHex pattern over many files in one process and write JSON per file.
//
// Equivalent per file to `imhex --pl format --pattern P -I ... --input F --output F.json`
// (ImHex 1.38.1 embeds PatternLanguage fb6ea061 and its JSON formatter), but one runtime serves
// every file: reset() -> setDataSource() -> executeString() -> FormatterJson::format().
//
// Usage: plbatch --pattern FILE [-I DIR]... --in-root DIR --out-root DIR [--force] [--time] < list
//   list      newline-separated paths relative to --in-root (CR before LF is ignored)
//   output    <out-root>/<rel>.json, written to a temp file and renamed into place;
//             on failure <out-root>/<rel>.json.err holds the errors and no .json is written
//   stdout    one line per file: "ok   <rel>", "skip <rel>" or "FAIL <rel> (see <err>)",
//             the same lines packets/imhex-export.sh counts
//   --force   overwrite existing JSON (default: skip files whose JSON exists)
//   --time    also time parse-only, execute and format per file; totals go to stderr
// Exit code: 0 when every file is ok or skipped, 1 when any failed, 2 on a usage error.

#include <fmt/format.h>   // must precede the PL headers (error.hpp uses fmt::format)
#include <pl/pattern_language.hpp>
#include <pl/formatters.hpp>

#include <chrono>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <system_error>
#include <vector>

#ifdef _WIN32
#include <process.h>
#define PLBATCH_GETPID _getpid
#else
#include <unistd.h>
#define PLBATCH_GETPID getpid
#endif

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

    [[noreturn]] void usage(const char *message) {
        std::fprintf(stderr, "plbatch: %s\nusage: plbatch --pattern FILE [-I DIR]... --in-root DIR --out-root DIR [--force] [--time] < list\n", message);
        std::exit(2);
    }

    bool readFile(const fs::path &path, std::string &out) {
        std::ifstream in(path, std::ios::binary);
        if (!in) return false;
        std::ostringstream buffer;
        buffer << in.rdbuf();
        out = std::move(buffer).str();
        return !in.bad();
    }

    bool writeFile(const fs::path &path, const void *data, size_t size) {
        std::ofstream out(path, std::ios::binary | std::ios::trunc);
        if (!out) return false;
        out.write(static_cast<const char *>(data), std::streamsize(size));
        out.close();
        return !out.fail();
    }

    double ms(Clock::duration d) {
        return std::chrono::duration<double, std::milli>(d).count();
    }

}

int main(int argc, char **argv) {
    fs::path patternPath, inRoot, outRoot;
    std::vector<fs::path> includes;
    bool force = false, timing = false;

    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        auto next = [&]() -> const char * {
            if (i + 1 >= argc) usage(("missing value for " + arg).c_str());
            return argv[++i];
        };
        if (arg == "--pattern" || arg == "-p") patternPath = next();
        else if (arg == "-I" || arg == "--includes") includes.emplace_back(next());
        else if (arg == "--in-root") inRoot = next();
        else if (arg == "--out-root") outRoot = next();
        else if (arg == "--force") force = true;
        else if (arg == "--time") timing = true;
        else usage(("unknown argument " + arg).c_str());
    }
    if (patternPath.empty() || inRoot.empty() || outRoot.empty()) usage("--pattern, --in-root and --out-root are required");

    std::string patternCode;
    if (!readFile(patternPath, patternCode)) usage(("cannot read pattern " + patternPath.string()).c_str());
    const std::string patternSource = patternPath.string();
    for (const auto &dir : includes)
        if (!fs::is_directory(dir)) usage(("include directory not found: " + dir.string()).c_str());

    const auto formatters = pl::gen::fmt::createFormatters();
    auto &json = *formatters.front();   // FormatterJson, the default of `--pl format`
    if (json.getName() != "json") usage("first formatter is not json");

    pl::PatternLanguage runtime;
    std::string logText;
    runtime.setLogCallback([&logText](auto level, const std::string &message) {
        if (level == pl::core::LogConsole::Level::Error) { logText += message; logText += '\n'; }
    });

    const std::string tmpSuffix = ".tmp." + std::to_string(PLBATCH_GETPID());
    std::string data, line;
    size_t ok = 0, skipped = 0, failed = 0;
    Clock::duration tParse{}, tExec{}, tFormat{};

    while (std::getline(std::cin, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) continue;
        const std::string &rel = line;
        const fs::path input = inRoot / fs::path(rel);
        const fs::path out = outRoot / fs::path(rel + ".json");
        const fs::path err = outRoot / fs::path(rel + ".json.err");
        const fs::path tmp = outRoot / fs::path(rel + ".json" + tmpSuffix);
        std::error_code ec;

        if (!force && fs::exists(out, ec)) {
            std::printf("skip %s\n", rel.c_str()); std::fflush(stdout);
            skipped++;
            continue;
        }

        auto fail = [&](const std::string &why) {
            fs::create_directories(err.parent_path(), ec);
            writeFile(err, why.data(), why.size());
            fs::remove(tmp, ec);
            std::printf("FAIL %s (see %s)\n", rel.c_str(), err.generic_string().c_str()); std::fflush(stdout);
            failed++;
        };

        fs::create_directories(out.parent_path(), ec);
#ifdef _WIN32
        // Same guard as imhex-export.sh: keep paths under MAX_PATH for the native readers.
        if (const auto abs = fs::absolute(tmp, ec).string(); abs.size() >= 260) {
            fail("path too long (" + std::to_string(abs.size()) + " chars, Windows limit 260): " + abs + "\n");
            continue;
        }
#endif
        if (!readFile(input, data)) { fail("cannot read input " + input.string() + "\n"); continue; }

        if (timing) {
            runtime.reset();
            auto t0 = Clock::now();
            (void)runtime.parseString(patternCode, patternSource);
            tParse += Clock::now() - t0;
        }

        runtime.reset();
        logText.clear();
        runtime.setDangerousFunctionCallHandler([] { return false; });
        runtime.setIncludePaths(includes);
        runtime.setDataSource(0, data.size(), [&data](pl::u64 address, pl::u8 *buffer, size_t size) {
            std::memcpy(buffer, data.data() + address, size);
        });

        auto t1 = Clock::now();
        const bool success = runtime.executeString(patternCode, patternSource);
        auto t2 = Clock::now();
        tExec += t2 - t1;

        if (!success) {
            std::string why;
            const auto &compileErrors = runtime.getCompileErrors();
            if (!compileErrors.empty()) {
                why = "Compilation failed\n";
                for (const auto &e : compileErrors) why += e.format() + "\n";
            } else if (const auto &e = runtime.getEvalError(); e.has_value()) {
                why = "Pattern Error: " + std::to_string(e->line) + ":" + std::to_string(e->column) + " -> " + e->message + "\n";
            } else {
                why = "Pattern failed without an error message\n";
            }
            fail(why + logText);
            continue;
        }

        auto result = json.format(runtime);
        tFormat += Clock::now() - t2;
        if (result.empty()) { fail("formatter produced no output\n" + logText); continue; }
        if (!writeFile(tmp, result.data(), result.size())) { fail("cannot write " + tmp.string() + "\n"); continue; }
        fs::rename(tmp, out, ec);
        if (ec) { fail("cannot rename " + tmp.string() + ": " + ec.message() + "\n"); continue; }
        fs::remove(err, ec);
        std::printf("ok   %s\n", rel.c_str());
        ok++;
        std::fflush(stdout);
    }
    std::fflush(stdout);

    if (timing) {
        const size_t n = ok + failed;
        std::fprintf(stderr, "plbatch timing: %zu file(s); parse-only %.3f ms, execute (parse+evaluate) %.3f ms, format %.3f ms total",
                     n, ms(tParse), ms(tExec), ms(tFormat));
        if (n > 0)
            std::fprintf(stderr, "; per file parse %.3f ms, evaluate %.3f ms, format %.3f ms",
                         ms(tParse) / n, (ms(tExec) - ms(tParse)) / n, ms(tFormat) / n);
        std::fprintf(stderr, "\n");
    }
    return failed == 0 ? 0 : 1;
}
