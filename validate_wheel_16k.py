import glob
import sys
import zipfile

import elftools.elf.elffile

from typing import IO


def check_16kb_alignment(file: IO[bytes], target_alignment: int = 16384):
    elf = elftools.elf.elffile.ELFFile(file)

    load_segments = list(elf.iter_segments("PT_LOAD"))

    if not load_segments:
        print(f"No LOAD segments")
        return False

    is_aligned = True

    for i, seg in enumerate(load_segments):
        alignment = seg.header.p_align

        if alignment % target_alignment == 0:
            print(f"Segment {i} is compliant (p_align: {alignment}) ✅")
        else:
            print(f"Segment {i} is NOT aligned (p_align: {alignment}) ❌")
            is_aligned = False

    return is_aligned


if __name__ == "__main__":
    for file in glob.glob("artifacts/**/*.whl", recursive=True):
        print(file)
        with zipfile.ZipFile(file, "r") as z:
            for info in z.infolist():
                if info.filename.endswith(".so"):
                    print("-", info.filename)
                    with z.open(info, "r") as f:
                        check_16kb_alignment(f)
        print()
