import argparse
import html
import json
import os.path
import re
import zipfile


def normalize_package_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def get_package_name(wheel_path: str):
    if os.path.isfile(wheel_path):
        with zipfile.ZipFile(wheel_path, "r") as z:
            for file in z.namelist():
                if file.endswith(".dist-info/METADATA"):
                    with z.open(file) as f:
                        content = f.read().decode("utf-8")
                        matches = re.search(r"^Name:\s*(\S+)", content, re.MULTILINE)
                        if matches:
                            return normalize_package_name(matches.group(1))
    return None


def update_index(link_dict: dict[str, str]):
    package_list: set[str] = set()

    for wheel, link in link_dict.items():
        # Get package name
        pkg_name = get_package_name(f"../artifacts/{wheel}")
        if not pkg_name:
            print(f"{wheel} package name is unknown, skipping.")
            continue

        print(f"Processing {wheel}.")
        # Write link to temp file
        os.makedirs(pkg_name, exist_ok=True)
        with open(f"{pkg_name}/{wheel}.link.txt", "w", encoding="utf-8", newline="") as f:
            f.write(link)

        package_list.add(pkg_name)

    # Keep packages published outside the current wheel release, such as honkypy.
    for entry in os.scandir("."):
        if not entry.is_dir() or normalize_package_name(entry.name) != entry.name:
            continue
        if any(file.name.endswith(".link.txt") for file in os.scandir(entry.path)):
            package_list.add(entry.name)

    package_link_list: dict[str, list[tuple[str, str]]] = {}  # For writing the index
    for pkg_name in sorted(package_list):
        # Enumerate all package versions
        links: list[tuple[str, str]] = []

        for file in sorted(os.scandir(pkg_name), key=lambda file: file.name):
            if file.name.endswith(".link.txt"):
                with open(file.path, "r", encoding="utf-8") as f:
                    links.append((file.name[:-9], f.read()))

        package_link_list[pkg_name] = links

    return package_link_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_link_input")
    args = parser.parse_args()

    with open(args.json_link_input) as f:
        packages = update_index(json.load(f))

    # This is the source for the published root page; edit it here, not on gh-pages.
    # Write index
    with open("index.html", "w", encoding="utf-8", newline="") as root_f:
        root_f.write("<!DOCTYPE html>\n<html>\n<body>\n")
        root_f.write("""<p>
This site contains precompiled wheels used by <a href="https://github.com/DarkEnergyProcessor/NPPS4-Android">Android</a>
version of <a href="https://github.com/DarkEnergyProcessor/NPPS4">NPPS4</a>.
</p>
<p>
Packages are compiled with these options:
</p>
<ul>
<li>16KiB page size.</li>
<li>Targets Python 3.14.</li>
<li>arm64-v8a and x86-64 ABI.</li>
<li>Android 7.0 or later (API 24).</li>
</ul>
<p>
The repository can be found <a href="https://github.com/DarkEnergyProcessor/npps4-android-whl">in GitHub</a>.
</p>
""")

        for pkg_name, links in packages.items():
            with open(f"{pkg_name}/index.html", "w", encoding="utf-8", newline="") as sub_f:
                sub_f.write("<!DOCTYPE html>\n<html>\n<body>\n")
                for link in links:
                    sub_f.write(f'<a href="{html.escape(link[1], True)}">{html.escape(link[0])}</a>\n')
                sub_f.write("</body>\n</html>\n")

            root_f.write(f'<a href="{html.escape(pkg_name, True)}/">{html.escape(pkg_name)}</a>\n')

        root_f.write("</body>\n</html>\n")


if __name__ == "__main__":
    main()
